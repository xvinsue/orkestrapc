from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, FieldList
from wtforms.validators import DataRequired, InputRequired


class LoginForm(FlaskForm):

    username = StringField(label='Username', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])




class addAsset(FlaskForm):

    name = StringField(label='Brand Name', validators=[DataRequired(), InputRequired()])
    category = SelectField(label='Category', choices=['Mouse', 'Keyboard'])
    asset_tag = StringField(label='Asset Tag', validators=[DataRequired()], default="None")
    serial_no = StringField(label='Serial Number', validators=[DataRequired()], default="None")

class assignAsset(FlaskForm):

    name = SelectField(label='Brand Name', name="name-1", validators=[DataRequired(), InputRequired()])
    # category = SelectField(label='Category', name="cat-1", choices=['Mouse', 'Keyboard'])
    asset_tag = StringField(label='Asset Tag', name="asset-1", validators=[DataRequired()], default="None")
    serial_no = StringField(label='Serial Number',name="serial-1",  validators=[DataRequired()], default="None")
    user = SelectField(label="Assign to", name="user-1", validators=[DataRequired()])
    

