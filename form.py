from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, FieldList, IntegerField
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

    id = SelectField(label='Asset ID', validators=[DataRequired(), InputRequired()])
    agent_name = SelectField(label='Assign To:', validators=[DataRequired()])
    

    