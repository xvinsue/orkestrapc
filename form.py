from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):

    username = StringField(label='Username', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])


class RegistrationForm(FlaskForm):

    register_user = StringField(label='Username', validators=[DataRequired()])
    register_pass = PasswordField(
        label='Password', validators=[DataRequired()])
    confirm_pass = PasswordField(
        label='Password', validators=[DataRequired()])