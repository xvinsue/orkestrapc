from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user


db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text)
    password = db.Column(db.String(200))
    type = db.Column(db.Text)

class Asset(db.Model):
    __tablename__ = 'asset'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'))
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    date_assigned = db.Column(db.Text)


class Stock(db.Model):
    __tablename__ = 'stock'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, unique=False, nullable=False)
    category = db.Column(db.String(30), unique=False, nullable=False)
    asset_tag = db.Column(db.String(30), unique=False, nullable=False)
    serial_number = db.Column(db.String(30), unique=False, nullable=False)

    
class Employee(db.Model):
    __tablename__ = "employee"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.Text)
    # accountability_path = db.Column(db.Text)
    role = db.Column(db.Text)


class ReplaceNo(db.Model):
    __tablename__ = "replaceNo"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    replacement_no = db.Column(db.Integer, nullable=True, default=0)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'))



def create_database():
    db.create_all()



