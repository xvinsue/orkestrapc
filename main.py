from flask import Flask, render_template, request, jsonify, url_for, send_from_directory, abort, redirect, flash, Blueprint
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from icecream import ic
from form import LoginForm, addAsset
import hashlib
from models import db, User, Asset, Employee, Stock
from sqlalchemy import cast, text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY'] = 'your secret keylalal242ss'


login_manager = LoginManager()
login_manager.init_app(app)

db.init_app(app)


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
        
        return "No employees found"

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


@app.route("/user/", defaults= {"fullname":None} ,methods=['GET', 'POST'])
@app.route("/user/<fullname>", methods=['GET', 'POST'])
@login_required
def getUser(fullname):

    error = ""

    if fullname:
        resolved_emp_details = db.session.query(
        Employee.full_name,
        Stock.name.label('asset_name'),
        Stock.category,
        Stock.asset_tag,
        Stock.serial_number,
        Asset.replacement_no
    ) \
    .join(Asset, Employee.id == Asset.employee_id) \
    .join(Stock, Asset.stock_id == Stock.id)


        resolved_emp_details = resolved_emp_details.filter(Employee.full_name == fullname)

        resolved_emp_details = resolved_emp_details.filter(Employee.id != None) \
            .order_by(Employee.full_name, Asset.id) \
            .all()
        
        if resolved_emp_details:
            # Group data by employee name
            emp_details = {}
            for emp_name, asset_name, category, asset_tag, serial_number, replacement_no in resolved_emp_details:
                if emp_name not in emp_details:
                    emp_details[emp_name] = []
                emp_details[emp_name].append({
                    'name': asset_name,
                    'category': category,
                    'asset_tag': asset_tag,
                    'serial_number': serial_number,
                    'replacement_no': replacement_no
                })
            number_of_assets = numOfAssets() 
            agents = total_agents()
            return render_template("view.html", agents=agents, number_of_assets=number_of_assets, emp_details=emp_details)
        else:
            error = f"No asset yet assigned to agent {fullname}"
            return render_template("view.html",  emp_details={}, error=error)
    else:
        error = f"No fullname was provided"
        return render_template("view.html",  emp_details={}, error=error)


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
    # Combine queries with joins and filtering
    resolved_emp_details = db.session.query(
        Employee.full_name,
        Stock.name.label('asset_name'),
        Stock.category,
        Stock.asset_tag,
        Stock.serial_number,
        Asset.replacement_no
    ) \
    .join(Asset, Employee.id == Asset.employee_id) \
    .join(Stock, Asset.stock_id == Stock.id) \
    .filter(Employee.id != None) \
    .order_by(Employee.full_name, Asset.id) \
    .all()

    # Group data by employee name
    emp_details = {}

    # Call the other necessary functions
    number_of_assets = numOfAssets()
    ic("num", number_of_assets)
    unallocated_stocks()
    agents = total_agents()

    if resolved_emp_details:
        for emp_name, asset_name, category, asset_tag, serial_number, replacement_no in resolved_emp_details:
            if emp_name not in emp_details:
                emp_details[emp_name] = []
            emp_details[emp_name].append({
                'name': asset_name,
                'category': category,
                'asset_tag': asset_tag,
                'serial_number': serial_number,
                'replacement_no': replacement_no
            })
       
    else:
        error = "No assets assigned to any agents yet."

 
    return render_template('view.html', agents=agents, number_of_assets=number_of_assets, emp_details=emp_details, error=error)

# ----------------------- CRUD FOR ASSET ONLY ----------------------------

@app.route("/add-asset", methods=['POST', 'GET'])
def add_asset_form():

    form = addAsset()
    error = ""
    if request.method == 'POST':

        name = request.form.get('name')
        category = request.form.get('category')
        asset_tag = request.form.get('asset_tag')
        serial_no = request.form.get('serial_no')

        is_exist = Stock.query.filter(
            (Stock.asset_tag == asset_tag) | (asset_tag is None)
        ).first()

        
        if not is_exist:

            data = Stock(name=name, category=category, asset_tag=asset_tag, serial_number=serial_no)

            db.session.add(data)
            db.session.commit()

            error = "Asset successfully added."
        else:
            error = f"It seems like asset-tag {asset_tag} for asset category {category} already exists."
        return render_template("add-asset.html", error=error, form=form)

    return render_template('add-asset.html', form=form, error=error)

# ---------------- EXPERIMENTAL ---------------------

@app.route("/asset-view", methods=['GET'])
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

@app.route("/update-asset/<num>", methods=['GET', 'POST'])
@login_required
def update_asset(num):

    form = addAsset()  # Assuming addAsset() creates the form object
    asset = Stock.query.filter_by(id=num).first()

    if form.validate_on_submit():
        # Update asset data based on form data (logic omitted for brevity)
        return redirect(url_for('asset_view'))  # Redirect after update

    return render_template('update-asset.html', form=form, asset=asset)



# ----------------- NO CHANGES NEEDED PROBABLY -----------------
# ----------------- LOGIN, HOME, LOGOUT ------------------
@app.route("/login", methods=['GET', 'POST'])
def index():

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
            return redirect(url_for("view"))

        else:

            return render_template("login.html", form=form, error="Wrong username or password.")

    return render_template("login.html", form=form)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@login_manager.user_loader
def load_user(user_id):

    return User.query.get(int(user_id))


if __name__ == '__main__':
    app.run(debug=True)