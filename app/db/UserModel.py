from flask import g
from psycopg2 import sql
from werkzeug.security import generate_password_hash,check_password_hash
from ..email import send_email
import os
from .config import CRUD

class User(CRUD):
    tablename = 'users'
    associations = {'roles':'one'}
    def __init__(self,username,role_id,password):
        self.id = None
        self.username = username
        self.in_db = self._check_user()
        if self.in_db is False:
            self.role_id = role_id
            self.password = password
    
    def _check_user(self):
        user = self._check(self.tablename,'username',self.username)
        if user is None or len(user) == 0:
            return False
        else:
            # print ('The user was already in the database and these are his/her attributes: ',user)
            self.id = user[0][0]
            self.role_id = user[0][1]
            self.password_hash = user[0][2]
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
            primary_key = self._insert(self.tablename, username=self.username,
            role_id=self.role_id,password_hash=self.password_hash)
            if primary_key is not None:
                self.id = primary_key
                self.in_db = True
                send_email(os.environ.get('ADMIN_EMAIL'),'New User',
                                'mail/new_user', name=self.username)
        else:
            print ('The user was already in the database')

    def delete(self):
        if self.in_db is True:
            self._delete(self.tablename,self.id)
        else:
            print ('The user is not in the database')