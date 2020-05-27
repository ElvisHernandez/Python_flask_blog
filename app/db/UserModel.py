from flask import g
from psycopg2 import sql
from werkzeug.security import generate_password_hash,check_password_hash
from ..email import send_email
import os
from .config import CRUD, Database,Config
from flask_login import UserMixin
from .. import login_manager

@login_manager.user_loader
def load_user(user_id):
    db = Database(Config)
    conn = db.get_db()
    # user_email = CRUD._check('users','id',user_id)[1]
    user = User('',id=user_id)
    if user.in_db is False:
        return None
    print ('This is inside the load_user function in the UserModel module')
    conn.close()
    return user
    

class User(UserMixin,CRUD):
    tablename = 'users'
    associations = {'roles':'one'}
    def __init__(self,email,username=None,role_id=None,password='PROXY_PASSWORD',**kwargs):
        self.id = kwargs.get('id',None)
        self.email = email
        self.username = username
        self.in_db = self._check_user()
        if self.in_db is False:
            self.role_id = role_id
            self.password = password
    
    def _check_user(self):
        if self.id is not None:
            user = self._check(self.tablename,'id',self.id)
        else:
            user = self._check(self.tablename,'email',self.email)
        print ('This is the user after checking: ',user)
        if user is None or len(user) == 0:
            return False
        else:
            self.id = user[0]
            self.email = user[1]
            self.username = user[2]
            self.password_hash = user[3]
            self.role_id = user[4]
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
            # print ('This is in the role instance method: ',role_name)
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
            if prop == "password" or prop == "password_hash":
                print ('You cannot update the password in this way')
                return None
        if self.in_db is True:
            user = self._update(self.tablename,self.id,prop_dict)
            if user is not None:
                self.username = user[1]

    def delete(self):
        if self.in_db is True:
            self._delete(self.tablename,self.id)
        else:
            print ('The user is not in the database')