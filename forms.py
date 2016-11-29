from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, validators, Form, BooleanField, SelectField, RadioField
from wtforms.validators import DataRequired, NumberRange, Optional
from wtforms_components import IntegerField


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

class AddAppForm(Form):
    appname = StringField('Appname', [validators.Length(min=1, max=30), validators.DataRequired()])

class UpdateAppForm(Form):
    activeapps = SelectField('ActiveApps')
    activeradio = RadioField('ActiveRadio', choices=[('Delete', 'Delete'),('Deactivate', 'Deactivate')], default='Delete')
    deactiveapps = SelectField('DeactiveApps')
    deactiveradio = RadioField('DeactiveRadio', choices=[('Delete', 'Delete'),('Activate', 'Activate')], default='Delete')