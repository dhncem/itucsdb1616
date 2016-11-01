from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, validators, Form
from wtforms.validators import DataRequired, NumberRange, Optional
from wtforms_components import IntegerField

from datetime import datetime


class LoginForm(Form):
    username = StringField('Username', [validators.DataRequired()])

    password = PasswordField('Password',[validators.DataRequired()])

class RegisterForm(Form):
    username = StringField('Username',
                           [validators.Length(min=6, max=15), validators.DataRequired()])
    password = PasswordField('Password',
                             [validators.Length(min=6, max=15), validators.DataRequired(),
                              validators.EqualTo('confirmPass', message="Passwords do not match!")])
    confirmPass = PasswordField('Confirm Password')