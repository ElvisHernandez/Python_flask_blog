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
        self.username = username
        self.role_id = role_id
        self.password = password
        self.in_db = self._check_user()
    
    def _check_user(self):
        query = self._check(self.tablename,'username',self.username)
        if query is None or len(query) == 0:
            return False
        else:
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
            print ('This is in the role instance method: ',role_name)
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

    def insert_user(self):
        if self.in_db is False:   
            try:
                conn = g.db
                cursor = conn.cursor()
                sql_insert = sql.SQL('''INSERT INTO {} (username,role_id,password_hash)
                    VALUES (%s,%s,%s)''').format(sql.Identifier(self.tablename))

                cursor.execute(sql_insert,(self.username,self.role_id,self.password_hash))
                conn.commit()
                self.in_db = True
                send_email(os.environ.get('ADMIN_EMAIL'),
                    'New User', 'mail/new_user', name=self.username)
                cursor.close()
                print ('The user was successfully inserted into the database')
            except:
                print ('Something went wrong with the insertion')
        else:
            print ('The user was already in the database')