from flask import g
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,TextAreaField,BooleanField,SelectField
from wtforms.validators import DataRequired,Length,Email,Regexp,ValidationError
from ..db.UserModel import User
from flask_pagedown.fields import PageDownField

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')

class EditProfileForm(FlaskForm):
    name = StringField('Real name',validators=[Length(0,64)])
    location = StringField('Location',validators=[Length(0,64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

class EditProfileAdminForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),
        Length(1,64),Email()])
    username = StringField('Username',validators=[DataRequired(),
        Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
        'Usernames must have only letters, numbers, dots or '
        'underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role',coerce=int)
    name = StringField('Real name',validators=[Length(0,64)])
    location = StringField('Location', validators=[Length(0,64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self,user,*args,**kwargs):
        super(EditProfileAdminForm,self).__init__(*args,**kwargs)
        self.role.choices = self._get_role_choices()
        self.user = user
    
    def validate_email(self,field):
        u = User(email=field.data)
        if field.data != self.user.email and u.in_db:
            raise ValidationError('Email already registered.')

    def validate_username(self,field):
        u = User(username=field.data)
        if field.data != self.user.username and u.in_db:
            raise ValidationError('Username already in use.')
        
    @staticmethod
    def _get_role_choices():
        try:
            conn = g.db
            cursor = conn.cursor()
            sql_query = 'SELECT id,name FROM roles;'
            cursor.execute(sql_query)
            results = cursor.fetchall()
            return results
        except:
            print ('Something went wrong in the get_role_choices method')
            return None
    
class PostForm(FlaskForm):
    body = PageDownField("What's on your mind?",validators=[DataRequired()])
    submit =  SubmitField('Submit')