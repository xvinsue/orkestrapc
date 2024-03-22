from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, FieldList, IntegerField
from wtforms.validators import DataRequired, InputRequired, Length, ValidationError


class LoginForm(FlaskForm):

    username = StringField(label='Username', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])

class addAsset(FlaskForm):

    name = StringField(label='Brand Name', validators=[DataRequired(), InputRequired()])
    category = SelectField(label='Category', choices=['Mouse', 'Keyboard', 'CPU', 'Monitor', 'Headset', "Camera", "Chair"])
    asset_tag = StringField(label='Asset Tag', validators=[DataRequired()], default="None")
    serial_no = StringField(label='Serial Number', validators=[DataRequired()], default="None")

class assignAsset(FlaskForm):

    id = SelectField(label='Asset ID', validators=[DataRequired(), InputRequired()])
    agent_name = SelectField(label='Assign To:', validators=[DataRequired()])
    

class UnassignedAgents(FlaskForm):

    names = SelectField(label="Agent list", validators=[DataRequired()])


class employeeForm(FlaskForm):
    
    id = IntegerField(label="id", validators=[DataRequired()])
    name = StringField(label="Agent full name", validators=[DataRequired(), Length(min=5)])
    role = SelectField(label='Category', choices=['MSE', 'SA', 'FSE', 'HR', 'Recruit', 'Intern'])


    def validate_name(form, field):
        excluded_chars = "*?!'^+%&/()=}][{$#123456789"
        for char in field.data:
            if char in excluded_chars:
                raise ValidationError(
                    f"Character {char} is not allowed in full name.")

