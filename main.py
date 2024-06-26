from flask import Flask, render_template, request, jsonify, url_for, redirect, flash
from flask_login import login_user, LoginManager, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy
from icecream import ic
from form import LoginForm, addAsset, assignAsset, UnassignedAgents, employeeForm, employeeForm2
import hashlib
from models import db, User, Asset, Employee, Stock, ReplaceNo
from sqlalchemy import cast, text
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY'] = 'your secret keylalal242ss'


login_manager = LoginManager()
login_manager.init_app(app)

db.init_app(app)

with app.app_context(): db.create_all()

current_date = datetime.now()
formatted_date = current_date.strftime('%d/%m/%Y')

# ----------------- USEF DEF -----------------

# Get total number of assets
def numOfAssets():

    category_counts = db.session.query(
        Stock.category, db.func.count(Stock.id).label('count')
    ) \
    .group_by(Stock.category).all()

    if category_counts:
        for category, count in category_counts:
            ic(f"Category: {category}, Count: {count}")
        
        return category_counts

# Get all assets that are not currently not assigned yet.
def unallocated_stocks():
    unallocated_stocks = db.session.query(Stock) \
    .outerjoin(Asset, Stock.id == Asset.stock_id) \
    .filter(Asset.id == None) \
    .all()

    if unallocated_stocks:

        for stock in unallocated_stocks:
            ic(f"Unallocated Stock: {stock.name} (Category: {stock.category}), (Asset Tag: {stock.asset_tag})")

    return unallocated_stocks

# Get total number of agents
def total_agents():

    total_agents = Employee.query.count()

    if total_agents == 0 :
        
        return False

    return total_agents

def get_employee_details(search_name=None):
    if search_name:
        # Perform wildcard search on employee full names
        emp_details = db.session.query(Employee) \
            .filter(Employee.full_name.like(f"{search_name.lower()}%")) \
            .all()
 
    if len(emp_details) == 0:
        full_names = False

    else:
        # Convert to list of dictionaries with just full names
        full_names = [{'full_name': emp.full_name, 'role': emp.role} for emp in emp_details]

    return full_names

# password for admin: stillmissinu
def hash_sha256(data):
    sha256 = hashlib.sha256()
    sha256.update(data.encode('utf-8'))
    return sha256.hexdigest()


# This route is used for the search function from both search.html and view.html
@app.route("/search", methods=['GET', 'POST'])
@login_required
def search():
    search_name = ''
    search_view = ''
    match = []

    if request.method == 'POST':

        if 'fname' in request.form:
            search_name = request.form.get('fname')
            match = get_employee_details(search_name)
           
            return render_template('search.html', match=match)
        elif 'fname-view' in request.form:

            search_view = request.form.get('fname-view')
            # Handle search based on view parameter
            match = get_employee_details(search_view)

            if match == False:
                fullname = ""
            else:
                fullname = match[0]['full_name']

            return redirect(url_for('getUser', fullname=fullname))
    
    return render_template("search.html")


@app.route("/user/<fullname>", methods=['GET', 'POST'])
@login_required
def getUser(fullname):

    error = ""

    form = UnassignedAgents()

    if fullname:

        resolved_emp_details = db.session.query(
        Employee.full_name,
        Stock.name.label('asset_name'),
        Stock.category,
        Stock.asset_tag,
        Stock.serial_number,
        Asset.stock_id.label('asset_id')
    ) \
    .join(Asset, Employee.id == Asset.employee_id) \
    .join(Stock, Asset.stock_id == Stock.id) 


        resolved_emp_details = resolved_emp_details.filter(Employee.full_name == fullname)

        # Use the user_id to query all stock_id in the ReplaceNo table
        # and then get each category and 
        # pair them accordingly to the category that matches from the 
        # resolved_emp_details object.

        employee = Employee.query.filter_by(full_name=fullname).first()
        user_id = employee.id

        stock_id_in_replaceNo = ReplaceNo.query.filter_by(employee_id=user_id).all()
        categories = {}

        for stock in stock_id_in_replaceNo:
            stockTable = Stock.query.filter_by(category=stock.category).first()
            categories[stockTable.category] = stock.replacement_no 
            
        resolved_emp_details = resolved_emp_details.filter(Employee.id != None) \
            .order_by(Employee.full_name, Asset.id) \
            .all()
        
        if resolved_emp_details:
            # Group data by employee name
            emp_details = {}
            for emp_name, asset_name, category, asset_tag, serial_number, asset_id in resolved_emp_details:
                if emp_name not in emp_details:
                    emp_details[emp_name] = []

         
                asset_info = {
                'name': asset_name,
                'category': category,
                'asset_tag': asset_tag,
                'serial_number': serial_number,
                'asset_id': asset_id
                }

                all_unassigned_query = """
                        SELECT * FROM employee
                        WHERE id NOT IN (
                        SELECT employee_id FROM asset
                        );
                """

                empty_agents = db.session.execute(text(all_unassigned_query))

                form.names.choices = [(str(row[0]), str(row[1])) for row in empty_agents]


                # Check for category match and append Replace_No:
                if category in categories:
                    asset_info['Replace_No'] = categories[category]

                emp_details[emp_name].append(asset_info) 
                
            
            return render_template("view_user.html", emp_details=emp_details, form=form, fullname=fullname)
        else:
            no_assets_flag = True
            error = f"No asset yet assigned to agent {fullname}"
            flash(error)
            return render_template("view_user.html", no_assets_flag=no_assets_flag , emp_details={}, error=error)
    else:
        error = f"No fullname was provided"
        flash(error)
        return render_template("view_user.html",  emp_details={}, error=error)


@app.route("/view", methods=['GET'])
@login_required
def view():
    error = ""
    emp_details = {}
    number_of_assets = ""

    # Get all assets that is currently assigned to an employee

    deployed_assets = db.session.query(Asset) \
    .join(Employee, Asset.employee_id == Employee.id) \
    .filter(Employee.id != None).all()

    # Create a dictionary to store asset IDs for each employee
    emp_id_assets = {}
    for da in deployed_assets:
        emp_id = da.employee_id
        if emp_id not in emp_id_assets:
            emp_id_assets[emp_id] = []
        emp_id_assets[emp_id].append(da.id)

    resolved_emp_details = db.session.query(
    Employee.full_name,
    Stock.name.label('asset_name'),
    Stock.category,
    Stock.asset_tag,
    Stock.serial_number
    ) \
    .join(Asset, Employee.id == Asset.employee_id) \
    .join(Stock, Asset.stock_id == Stock.id) \
    .filter(Employee.id != None) \
    .group_by(Employee.full_name, Stock.id) \
    .order_by(Employee.full_name, Asset.id) \
    .all()

    # Group data by employee name
    emp_details = {}

    # Call the other necessary functions
    number_of_assets = numOfAssets()
    unallocated_stocks()
    agents = total_agents()

    if resolved_emp_details:
        for emp_name, asset_name, category, asset_tag, serial_number in resolved_emp_details:
            if emp_name not in emp_details:
                emp_details[emp_name] = []
            emp_details[emp_name].append({
                'name': asset_name,
                'category': category,
                'asset_tag': asset_tag,
                'serial_number': serial_number
            })
       
    else:
        error = "No assets assigned to any agents yet."

 
    return render_template('view.html', agents=agents, number_of_assets=number_of_assets, emp_details=emp_details, error=error)

# ----------------------- CRUD FOR ASSET ONLY ----------------------------

@app.route("/add-asset", methods=['POST', 'GET'])
@login_required
def add_asset_form():

    form = addAsset()
    error = ""
    if request.method == 'POST':

        name = request.form.get('name')
        category = request.form.get('category')
        asset_tag = request.form.get('asset_tag')
        serial_no = request.form.get('serial_no')

        is_exist = Stock.query.filter_by(name=name, category=category, asset_tag=asset_tag).first()
        
        if not is_exist:

            data = Stock(name=name, category=category, asset_tag=asset_tag, serial_number=serial_no)

            db.session.add(data)
            db.session.commit()

            error = "Asset successfully added."
        else:
            error = f"It seems like asset-tag {asset_tag} for asset category {category} already exists."
        return render_template("add-asset.html", error=error, form=form)

    return render_template('add-asset.html', form=form, error=error)

@app.route("/asset-view", methods=['GET'])
@login_required
def asset_view():
    
    
    msg = ""
    all_stocks_query = """
    SELECT * FROM stock
    WHERE id NOT IN (
    SELECT stock_id FROM asset
    );
    """
    
    stocks_not_in_asset = db.session.execute(text(all_stocks_query))

    if not stocks_not_in_asset:

        msg = "No unassigned assets found."

    return render_template("asset-view.html", msg=msg, stocks=stocks_not_in_asset)

# Delete asset since the original query gets
# all assets that are not currently assigned
@app.route("/delete-asset/<asset_id>", methods=['GET', 'POST'])
@login_required
def delete_asset(asset_id):

    flash(f'Asset {asset_id} successfully deleted!')
    asset = Stock.query.filter_by(id=asset_id).first()

    db.session.delete(asset)
    db.session.commit()

    return redirect(url_for('asset_view'))

# Update unassigned assets
@app.route("/update-asset/<num>", methods=['GET', 'POST'])
@login_required
def asset_update(num):

    form = addAsset() 
    asset = Stock.query.filter_by(id=num).first()
    

    if request.method == 'POST':
        
        name = request.form.get('name')
        category = request.form.get('category')
        asset_tag = request.form.get('asset_tag')
        serial_no = request.form.get('serial_no')

        asset.name = name
        asset.category = category
        asset.asset_tag = asset_tag
        asset.serial_number = serial_no
        db.session.commit()

        return redirect(url_for('asset_view'))  

    return render_template('update-asset.html', form=form, asset=asset,num=num)


@app.route("/get_categories", methods=['POST', 'GET'])
def get_categories():
  
  name = request.args.get('a')
  ic(name)
  # Fetch categories based on the name and field name (modify query)
  categories = db.session.query(Stock.category).filter_by(name=name).first()
 
  ic(categories)

  return jsonify(categories)


@app.route("/assign-asset", methods=['GET', 'POST'])
@login_required
def assign_asset():

    msg = ""
    form = assignAsset()

    all_stocks_query = """
    SELECT * FROM stock
    WHERE id NOT IN (
    SELECT stock_id FROM asset
    );
    """

    users = Employee.query.all()

    for user in users:
        ic(user.id)

    stocks_not_in_asset = db.session.execute(text(all_stocks_query)).fetchall()

    if not stocks_not_in_asset:
        msg = "No unassigned assets found."
    else:
        form.id.choices = [(str(row[0]), str(row[0])) for row in stocks_not_in_asset]
        form.agent_name.choices = [(str(row.id),  str(row.full_name + " (" + row.role + ")")) for row in users]

    return render_template("assign-asset copy.html", form=form, msg=msg, stocks=stocks_not_in_asset)

@app.route("/assign_asset_controller", methods=['POST'])
@login_required
def assign_asset_controller():

    msg = ""

    id = request.form.get('id')
    agent_name = request.form.get('agent_name')

    user_id = Employee.query.filter_by(id=agent_name).first()

    if user_id:

        asset = Asset(stock_id=id, employee_id=user_id.id, date_assigned=formatted_date)
        db.session.add(asset)

        #Get category of asset
        stock = Stock.query.filter_by(id=id).first()

        replacement_record = ReplaceNo(employee_id=user_id.id, replacement_no=0, category=stock.category)
        db.session.add(replacement_record)

        db.session.commit()


        msg = "Asset assigned successfully!"
        flash(msg, 'success')
    else:

        msg = "Agent not found - please try again."
        flash(msg, 'error')

    return redirect(url_for('assign_asset'))

# Idea from the view route there is an edit button there
# and it will pre-populate a form
@app.route("/assign-update/<user_id>", methods=['GET', 'POST'])
def assign_update():

    return render_template('assign-update.html')

@app.route("/replace_asset/<fn>/<asset_id>", methods=['GET', 'POST'])
def replace_asset(fn, asset_id):

    msg = ""

    form = assignAsset()

    stock_det = Stock.query.filter_by(id=asset_id).first()

    # Get all assets that are not unassigned that matches the 
    # category to be replaced.
    all_stocks_query = f"""
    SELECT * FROM stock
    WHERE id NOT IN (
    SELECT stock_id FROM asset
    ) AND category = '{stock_det.category}';
    """

    stocks_not_in_asset = db.session.execute(text(all_stocks_query)).fetchall()

    if not stocks_not_in_asset:

        msg = "No unassigned assets found."
    else:
        form.id.choices = [(str(row[0]), str(row[0])) for row in stocks_not_in_asset]

    return render_template("replace_asset.html", form=form, msg=msg, stocks=stocks_not_in_asset, stock_det=stock_det, fn=fn)

@app.route("/replace_asset_controller", methods=['POST', 'GET'])
def replace_controller():

    
    if request.method == 'POST':

        old_id = request.form.get('old_id')
        full_name= request.form.get('fullname')
        asset_id = request.form.get('id')


        # Update the specific entry in the ReplaceNo table
        # Find the row using category and employee ID and plus + 1 as a counter
        getEmpName = Employee.query.filter_by(full_name=full_name).first()
        getCategory = Stock.query.filter_by(id=asset_id).first()
        replaceNo = ReplaceNo.query.filter_by(employee_id=getEmpName.id, category=getCategory.category).first()

        if replaceNo:
            replaceNo.replacement_no += 1
            db.session.commit()

        employee = Employee.query.filter_by(full_name=full_name).first()

        if employee:
            # Use employee ID and old ID for asset to be remove and replace with the
            # asset_id to be replaced.
            asset = Asset(stock_id=asset_id, employee_id=employee.id, date_assigned=current_date)
            db.session.add(asset)

            asset_to_delete = Asset.query.filter_by(stock_id=old_id, employee_id=employee.id).first()

            if asset_to_delete:
                db.session.delete(asset_to_delete)
                db.session.commit()
            else:
                flash("Asset to delete not found")
        else:
            flash("Employee not found!!")


        return redirect(url_for('getUser', fullname=full_name))

@app.route('/replace_all_asset/', methods=['GET', 'POST'])
def replace_all_asset():

    if request.method == 'POST':

        old_agent = request.form.get('agentToEmpty')
        new_agent = request.form.get('names')


        new_agent = Employee.query.filter_by(id=new_agent).first()

        # Find the old agent using full name:
        user = Employee.query.filter_by(full_name=old_agent).first()

        if user:  # Check if the old agent exists
            # Fetch all assets assigned to the old agent:
            assets_to_update = Asset.query.filter_by(employee_id=user.id).all()

            if assets_to_update:  # Check if there are assets assigned
                # Update employee_id for all fetched assets:
                for asset in assets_to_update:
                    asset.employee_id = new_agent.id

                # Commit the changes to the database:
                db.session.commit()

                # Change th employee_id in the ReplaceNo using the new_agent
                transfer_replace_count = ReplaceNo.query.filter_by(employee_id=user.id).all()

                if transfer_replace_count:
                    for transfer in transfer_replace_count:

                        transfer.employee_id = new_agent.id
                    
                    db.session.commit()
                    error_msg = f"Succesfully transferred asset from {old_agent} to {new_agent.full_name}"
                else:
                    error_msg = f"No replacement history was found for the old agent {old_agent}"
                    flash(error_msg)
            else:
                # Handle the case where no assets are found for the old agent
                error_message = f"No assets found assigned to agent {old_agent}."
                flash(error_message)
        else:
            # Handle the case where the old agent is not found
            error_message = f"Agent with name '{old_agent}' not found."
            flash(error_message)
        
        return redirect(url_for('getUser', fullname=new_agent.full_name))


@app.route("/return_asset/<asset_id>/<fn>", methods=['GET', 'POST'])
def return_asset(fn, asset_id):

    
    take_back_asset = Asset.query.filter_by(stock_id=asset_id).first()
    get_asset_detail = Stock.query.filter_by(id=asset_id).first()

    if take_back_asset:
        asset_name = f"{get_asset_detail.name} with asset tag {get_asset_detail.asset_tag}"

        db.session.delete(take_back_asset)
        db.session.commit()
        msg = f"Asset {asset_name} successfully taken back from {fn}!"
        flash(msg)
    else:
        msg = "Asset ID was not found please try again."

    return redirect(url_for('getUser', fullname=fn))


# ----------------- NO CHANGES NEEDED PROBABLY  DOWN HERE-----------------
# ----------------- LOGIN, HOME, LOGOUT ------------------
@app.route("/login", methods=['GET', 'POST'])
def login():

    form = LoginForm()

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        hashed = hash_sha256(password)

        is_user_exists = User.query.filter_by(
            username=username, password=hashed).first()
        ic(is_user_exists)
        if is_user_exists:
            login_user(is_user_exists, remember=True)
            return redirect(url_for("home"))

        else:

            return render_template("login.html", form=form, error="Wrong username or password.")

    return render_template("login.html", form=form)

@app.route("/register", methods=['GET', 'POST'])
def register():

    form = LoginForm()

    # if request.method == "POST":

    #     username = request.form.get("username")
    #     password = request.form.get("password")
    #     type = request.form.get("user")

    #     hashed = hash_sha256(password)

    #     is_user_exists = User.query.filter_by(
    #         username=username, password=hashed).first()
    #     ic(is_user_exists)
    #     if is_user_exists:
    #         login_user(is_user_exists, remember=True)
    #         return redirect(url_for("home"))

    #     else:

    #         return render_template("login.html", form=form, error="Wrong username or password.")

    return render_template("register.html", form=form)

# ---------------- EXPERIMENTAL ---------------------
# CRUD FOR EMPLOYEE
@app.route('/add-emp', methods=['GET', 'POST'])
def add_emp():

    form = employeeForm2()

    
    if form.validate_on_submit():

        name = request.form.get('name')
        role = request.form.get('role')

        is_emp_exist = Employee.query.filter_by(full_name=name, role=role).first()

        if not is_emp_exist:

            employeeObj = Employee(full_name=name, role=role)
            db.session.add(employeeObj)
            db.session.commit()

            msg = "New user added succesfully!"
            flash(msg)
        else:
            msg = f"Employee {is_emp_exist.full_name} already exist at department {is_emp_exist.role}"
            flash(msg)

        return redirect(url_for('add_emp'))

    return render_template('add-emp.html', form=form)

@app.route("/view-emp", methods=['GET', 'POST'])
def view_emp():

    employee = Employee.query.all()

    if not employee:

        msg = "No employee found!"
        flash(msg)

    return render_template("view_emp.html", employee=employee)

@app.route('/confirm_delete_emp/<fn>', methods=['GET', 'POST'])
def confirm_delete_emp(fn):
    bye_emp = Employee.query.filter_by(full_name=fn).first()
    if bye_emp:
        # Delete associated entries (consider alternatives to .all())
        delete_replace_entry = ReplaceNo.query.filter_by(employee_id=bye_emp.id).delete()
        delete_asset_entry = Asset.query.filter_by(employee_id=bye_emp.id).delete()

        db.session.delete(bye_emp)
        db.session.commit()

        # Update db1 and db2 variables based on actual deletions
        db1 = "ReplaceNo" if delete_replace_entry else ""
        db2 = "Asset" if delete_asset_entry else ""

        msg = f"Agent {bye_emp.full_name} succesfully removed from tables {db1}, {db2}."
        flash(msg)
    else:
        flash(f"Employee with ID {bye_emp.id} not found.")

    return redirect(url_for('view_emp'))


@app.route("/update-emp/<fn>", methods=['GET', 'POST'])
@login_required
def name_emp_update(fn):

    form = employeeForm()

    getEmp = Employee.query.filter_by(full_name=fn).first()

    if not getEmp:

        msg = "Employee not found, please try again!"
        flash(msg)

        return redirect(url_for('view_emp'))

    form.id.data = getEmp.id
    form.name.data = getEmp.full_name
    form.role.data = getEmp.role

    return render_template('update_emp.html', form=form)

@app.route('/update-emp-controller', methods=['POST'])
@login_required
def update_emp_controller():

    if request.method == 'POST':

        id = request.form.get('id')
        full_name = request.form.get('name')
        role = request.form.get('role')

        empObject = Employee.query.filter_by(id=id).first()

        if empObject:

            empObject.full_name = full_name
            empObject.role = role
            
            db.session.commit()
            
            msg = "Employee details update succesfully."
        else:
            msg = "Employee not found! please try again later."
        
        flash(msg)
        
    return redirect(url_for('view_emp'))

@app.route("/")
def index():
    return render_template("index.html")
@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@login_manager.user_loader
def load_user(user_id):

    return db.session.get(User,(user_id))


if __name__ == '__main__':
    app.run(debug=True)