from flask_wtf import FlaskForm

from wtforms import StringField, EmailField, PasswordField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import InputRequired, ValidationError, Email, EqualTo, Length

from app.models import UserModel

validator_message = 'Hello? forgot me ;-;'

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(message=validator_message)])
    password = PasswordField('Password', validators=[InputRequired(message=validator_message)])
    remember_me = BooleanField('Remember Me?')
    submit = SubmitField('Sign in')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(message=validator_message)])
    email = EmailField('Email', validators=[InputRequired(message=validator_message), Email()])
    password = PasswordField('Password', validators=[InputRequired(message=validator_message)])
    repeat_pass = PasswordField('Repeat Password', validators=[InputRequired(message=validator_message), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = UserModel.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('This username already exists')

    def validate_email(self, email):
        user = UserModel.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('This email has already been used')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(message=validator_message)])
    about_me = TextAreaField('About Me', validators=[Length(min=0, max=256)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = UserModel.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('This username already exists. Please choose a different one')
