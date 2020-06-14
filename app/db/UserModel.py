from flask import g,current_app,request
from datetime import datetime
from psycopg2 import sql
from werkzeug.security import generate_password_hash,check_password_hash
from ..email import send_email
import os
import hashlib
from .config import CRUD,Database
from .RoleModel import Role,Permissions
from flask_login import UserMixin, AnonymousUserMixin
from .. import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

formatter = logging.Formatter('%(levelname)s:%(name)s:%(asctime)s:%(funcName)s:%(message)s')	
file_handler = logging.FileHandler(os.path.abspath('logs') + '/UserModel.log')
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

@login_manager.user_loader
def load_user(user_id):
    user = User(id=user_id)
    if user.in_db is False:
        return None
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
        self.name = columns.get("name",None)
        self.location = columns.get('location',None)
        self.about_me = columns.get('about_me',None)
        self.member_since = columns.get('member_since',None)
        self.last_seen = columns.get('last_seen',None)
        self.avatar_hash = columns.get('avatar_hash',None)
        if not 'no_check' in columns:
            self.in_db = self._check_user()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()
    
    ### Auth methods ###
    
    @property
    def password(self): 
        '''Raises AttributeError if the password attribute is attempted to
        be accessed directly.'''
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self,password):
        '''Invokes the generate_password_hash provided by werkzeug.security
        to generate a secure hash.'''
        self.password_hash = generate_password_hash(password)

    def verify_password(self,password):
        '''Invokes the check_password_hash provided by werkzeug.security to 
        verify or deny a provided password against the stored password_hash.'''
        return check_password_hash(self.password_hash,password)
    
    def generate_confirmation_token(self, expiration=3600):
        '''Generates a confirmation token for authentication purposes
        which is hashed with the SECRET_KEY configuration variable of Flask'''
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')
    
    def confirm(self,token):
        '''Verifies or denies the confirmation token generated by the 
        generate_confirmation_token method'''
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
    
    ### Permissions methods ###

    def can(self,perm):
        '''Returns true if the user has the passed permissions and false otherwise.'''
        role = self.role()
        if role is not None:
            return role.has_permission(perm)
        else:
            logger.warning('Could not find an associated role in the database.')
            return False

    def is_administrator(self):
        '''Returns true if a user has administrator permissions and false otherwise.'''
        role = self.role()
        if role is not None:
            return role.has_permission(Permissions.ADMIN)
        else:
            return False

    ### Association/relationship methods ###

    def follower_count(self):
        try:
            conn = g.db
            cursor = conn.cursor()
            sql_query = '''SLECT COUNT(*) FROM follow WHERE followed_id = %s;'''
            cursor.execute(sql_query,(self.id,))
            count = cursor.fetchone()[0]
            return count
        except:
            logger.exception("Something went wrong getting the follower count \
                    of user %s" % self.username)

    def followed_count(self):
        try:
            conn = g.db
            cursor = conn.cursor()
            sql_query = '''SELECT COUNT(*) FROM follow WHERE follower_id = %s;'''
            cursor.execute(sql_query,(self.id,))
            count = cursor.fetchone()
            return count
        except:
            logger.exception("Something went wrong getting the followed count \
                    of user %s" % self.username)

    def follow(self,user):
        '''Creates an entry in the follow table that establishes a follow relationship
        between the user and the passed in user if not already present in the database.'''
        if self.is_following(user):
            logger.info('Follow relationship already exists in the databse.')
            return 
        try:
            conn = g.db 
            cursor = conn.cursor()
            sql_insert = '''INSERT INTO follow (follower_id,followed_id) VALUES (%s,%s) RETURNING follower_id;'''
            cursor.execute(sql_insert,(self.id,user.id))
            conn.commit()
            follower_id = cursor.fetchone()
            if follower_id is None or follower_id[0] != self.id:
                return False
            return True
        except:
            logger.exception('Something went wrong when user: %s tried to follow user: %s' % (self.username,user.username))
        
    def unfollow(self,user):
        '''Removes an established follow relationship from the database if one is already present.'''
        if not self.is_following(user):
            logger.info('There is no follow relationship to remove from the database.')
            return
        try:
            conn = g.db
            cursor = conn.cursor()
            sql_delete = '''DELETE FROM follow WHERE followed_id = %s AND follower_id = %s RETURNING follower_id;'''
            cursor.execute(sql_delete,(user.id,self.id))
            conn.commit()
            follower_id = cursor.fetchone()
            print ('User %s unfollowed user %s' % (self.username,user.username))
            if follower_id is None or follower_id[0] != self.id:
                return False
            return True
        except:
            logger.exception('Something went wrong when user: %s tried to unfollow user: %s' % (self.username,user.username))

    def is_following(self,user):
        '''Returns True if the user is following the provided user and returns 
        false otherwise.'''
        if user.id is None or user.in_db is False:
            return False
        try:
            conn = g.db
            cursor = conn.cursor()
            sql_query = '''SELECT follower_id FROM follow WHERE followed_id = %s
                           AND follower_id = %s;'''
            cursor.execute(sql_query,(user.id,self.id))
            follower_id = cursor.fetchone()
            if follower_id is None or follower_id[0] != self.id:
                return False
            return True
        except: 
            logger.exception('''Something went wrong when trying to determine whether \
                    user: %s follows user: %s.''' % (self.username,user.username)) 

    def is_followed_by(self,user):
        '''Returns True if the user is followed by the provided user and
        returns False otherwise.'''
        if user.id is None or user.in_db is False:
            return False
        try:
            conn = g.db
            cursor = conn.cursor()
            sql_query = '''SELECT followed_id FROM follow WHERE followed_id = %s \
                           AND follower_id = %s;'''
            cursor.execute(sql_query,(self.id,user.id))
            followed_id = cursor.fetchone()
            if followed_id is None or followed_id[0] != self.id:
                return False
            return True
        except:
            logger.exception('''Something went wrong when trying to determine whether \
                    user: %s is followed by user: %s''' % (self.username,user.username))

    def posts(self):
        '''Returns all the posts written by a user'''
        if self.in_db:
            posts = Post.posts_by_author(self.id)
            return posts
        else:
            return []

    def role(self):
        '''Returns an instance of the Role class that corresponds
        to the role_id of the user.'''
        try:
            role = Role(id=self.role_id)
            return role
        
        except psycopg2.DatabaseError as e: 
            logger.exception('Something went wrong in the role instance method: %s' % e)
            return None

    ### User Avatar methods ###

    def gravatar_hash(self):
        '''Generates a hash based off a user's email that corresponds 
        to a Gravar avatar. '''
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    def gravatar(self,size=100,default='identicon',rating='g'):
        '''This method is invoked automatically to provide a default
        avatar in the case that a user does not provide their own.'''
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or self.gravatar_hash()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    ### CRUD and/or utility methods ###

    def ping(self):
        '''Used in auth blueprint before every request if a user
        is logged in to track the latest time for which they were on the app''' 
        self.last_seen = datetime.utcnow()
        new_prop = {'last_seen':self.last_seen}
        self.update(new_prop)

    def _check_user(self):
        '''Used in the constructor to automatically fetch
        the attributes of a already in the database.'''
        if self.id is not None:
            user_dict = self._check(self.tablename,'id',int(self.id))
        elif self.username is not None:
            user_dict = self._check(self.tablename,'username',self.username)
        elif self.email is not None:
            user_dict = self._check(self.tablename,'email',self.email)
        else:
            logger.info('No unique identifier was provided to check for user in database')
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
            self.name = user_dict.get("name",None)
            self.location = user_dict.get('location',None)
            self.about_me = user_dict.get('about_me',None)
            self.member_since = user_dict.get('member_since',None)
            self.last_seen = user_dict.get('last_seen',None)
            self.avatar_hash = user_dict.get('avatar_hash',None)
            return True
    
    def insert(self):
        '''Inserts an instance of a User into the database if not already present and sends
        the owner of the site an email to notify them that a new member has joined.'''
        if self.in_db is False:
            primary_key = self._insert(self.tablename,email=self.email, username=self.username,
            role_id=self.role_id,password_hash=self.password_hash,avatar_hash=self.avatar_hash)
            if primary_key is not None:
                self.id = primary_key
                self.in_db = True
                send_email(os.environ.get('ADMIN_EMAIL'),'New User',
                                'mail/new_user', name=self.username)
        else:
            logger.info('The user was already in the database')

    def update(self,prop_dict):
        '''Updates the attributes of a user already in the database. prop_dict is a dictionary
        with the attributes/columns that you want to update as keys, and their values as the values.
        e.g. prop_dict = {'username': 'TheNewUsername','role': 'TheNewRole'}'''
        if "password" in prop_dict:
            logger.info('You cannot update the password in this way')
            return None
        if "email" in prop_dict:
            self.email = prop_dict['email']
            self.avatar_hash = self.gravatar_hash()
            prop_dict['avatar_hash'] = self.avatar_hash

        if self.in_db is True:
            user = self._update(self.tablename,self.id,prop_dict)
            if user is not None:
                for prop in prop_dict:
                    if hasattr(self,prop):
                        self.__dict__[prop] = prop_dict[prop]

    def delete(self):
        '''Deletes a user from the database if they are present.'''
        if self.in_db is True:
            self._delete(self.tablename,self.id)
        else:
            logger.info('The user is not in the database')

class AnonymousUser(AnonymousUserMixin):
    def can(self,perm):
        return False
    
    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser
from .PostModel import Post
