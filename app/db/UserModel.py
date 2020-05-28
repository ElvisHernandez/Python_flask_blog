from flask import g,current_app
from psycopg2 import sql
from werkzeug.security import generate_password_hash,check_password_hash
from ..email import send_email
import os
from .config import CRUD, Database,Config
from flask_login import UserMixin
from .. import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
    db = Database(Config)
    conn = db.get_db()
    user = User(id=user_id)
    if user.in_db is False:
        return None
    print ('This is inside the load_user function in the UserModel module')
    conn.close()
    return user
    

class User(UserMixin,CRUD):
    tablename = 'users'
    associations = {'roles':'one'}
    def __init__(self,**columns):
        self.confirmed = False
        self.id = columns.get('id',None)
        self.username = columns.get('username',None)
        self.email = columns.get('email',None)
        self.role_id = columns.get('role_id',None)
        self.password = columns.get("password",'PROXY_PASSWORD')
        self.in_db = self._check_user()

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')
    
    def confirm(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        new_prop = {'confirmed': True}
        self.update(new_prop)
        return True
        
    
    def _check_user(self):
        if self.id is not None:
            user_dict = self._check(self.tablename,'id',self.id)
        elif self.username is not None:
            user_dict = self._check(self.tablename,'username',self.username)
        elif self.email is not None:
            user_dict = self._check(self.tablename,'email',self.email)
        else:
            print ('No unique identifier was provided to check for user in database')
            return False
        if user_dict is None: 
            return False
        else:
            self.id = user_dict['id']
            self.email = user_dict['email']
            self.username = user_dict['username']
            self.password_hash = user_dict['password_hash']
            self.confirmed = user_dict['confirmed']
            self.role_id = user_dict['role_id']
            return True
    
    
    def role(self):
        try:
            conn = g.db
            cursor = conn.cursor()
            sql_join = sql.SQL('''SELECT name FROM users
            JOIN roles ON users.role_id = roles.id
            WHERE users.username = %s''')
            cursor.execute(sql_join,(self.username,))
            role_name = cursor.fetchall()[0][0]
            return role_name
        
        except: 
            print ('Something went wrong in the role instance method')
            return None

    @property
    def password(self): 
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    def insert(self):
        if self.in_db is False:
            primary_key = self._insert(self.tablename,email=self.email, username=self.username,
            role_id=self.role_id,password_hash=self.password_hash)
            if primary_key is not None:
                self.id = primary_key
                self.in_db = True
                send_email(os.environ.get('ADMIN_EMAIL'),'New User',
                                'mail/new_user', name=self.username)
        else:
            print ('The user was already in the database')
    
    def update(self,prop_dict):
        '''prop_dict is a dictionary with the attributes/columns that 
        you want to update as keys, and their values as the values.
        e.g. prop_dict = {'username': 'TheNewUsername','role': 'TheNewRole'}'''
        for prop in prop_dict:
            if prop == "password":
                print ('You cannot update the password in this way')
                return None
        if self.in_db is True:
            user = self._update(self.tablename,self.id,prop_dict)
            if user is not None:
                self.username = user[1] # gotta come back to this 

    def delete(self):
        if self.in_db is True:
            self._delete(self.tablename,self.id)
        else:
            print ('The user is not in the database')