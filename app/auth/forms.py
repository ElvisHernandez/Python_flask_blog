from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired,Length,Email,Regexp,EqualTo
from wtforms import ValidationError
from ..db.UserModel import User
from flask_login import current_user

class RegistrationForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Length(1,64),Email()])
    username = StringField('Username',validators=[DataRequired(),Length(1,64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,'''Usernames must have only letters, numbers,
        dots or underscores''')])
    password = PasswordField('Password',validators=[DataRequired(),
        EqualTo('password2',message="Passwords must match.")])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self,field):
        user = User(email=field.data)
        if user.in_db is True:
            raise ValidationError('Email is already registered')
    
    def validate_username(self,field):
        user = User(username=field.data)
        if user.in_db is True:
            raise ValidationError('Username is already in use.')


class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Length(1,64),Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

class UpdatePasswordForm(FlaskForm):
    old_password = PasswordField('Current Password',validators=[DataRequired()])

    new_password = PasswordField('New Password',validators=[DataRequired(),
        EqualTo('new_password_confirmation',message="Passwords must match")])
    new_password_confirmation = PasswordField('New Password Confirmation',validators=[DataRequired()])
    submit = SubmitField('Update Password')

    def validate_old_password(self,field):
        if not current_user.verify_password(field.data):
            raise ValidationError('Current password does not match registered password.')

class PasswordResetEmailForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Length(1,64),Email()])
    submit = SubmitField('Send password reset email')

class ResetPasswordForm(FlaskForm):
    new_password = PasswordField('New password',validators=[DataRequired(),
        EqualTo('new_password_confirmation',message="Passwords must match.")])
    new_password_confirmation = PasswordField('New password confirmation', validators=[DataRequired()])
    submit = SubmitField('Reset Password')