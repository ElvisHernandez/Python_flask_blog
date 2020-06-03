from .config import CRUD
from flask import g
from datetime import datetime
from .UserModel import User

class Post(CRUD):
    tablename = 'posts'
    def __init__(self,**columns):
        self.id = columns.get('id',None)
        self.body = columns.get('body',None)
        self.time_stamp = datetime.utcnow()
        self.author_id = columns.get('author_id',None)
        self.in_db = self._check_post()

    @staticmethod
    def get_all_posts():
        try:
            conn = g.db
            cursor = conn.cursor()
            sql_query = 'SELECT * FROM posts ORDER BY time_stamp DESC;'
            cursor.execute(sql_query)
            posts = cursor.fetchall()
            if len(posts) != 0:
                props = [desc[0] for desc in cursor.description]
                posts_list = []
                for post in posts:
                    posts_list.append(dict(zip(props,post)))
                return posts_list
            return posts
        except:
            print ('Something went wrong fetching all the posts in the get_all_posts method.')
            return None
    @staticmethod
    def author(author_id):
        try:
            user = User(id=author_id)
            return user
        except:
            print ("Something went wrong while retrieving the posts' author.")
            return None
            

    def _check_post(self):
        if self.id is not None:
            post_dict = self._check(self.tablename,'id',self.id)
        elif self.author_id is not None:
            post_dict = self._check(self.tablename,'author_id',self.author_id)
        else:
            print ('No unique identifier was provided to check for role in database.')
            return False
        if post_dict is None:
            return False
        else:
            self.id = post_dict['id']
            self.body = post_dict['body']
            self.time_stamp = post_dict['time_stamp']
            self.author_id = post_dict['author_id']
            return True
    
    def insert(self):
        if self.in_db is False:
            primary_key = self._insert(self.tablename,body=self.body,
                time_stamp=self.time_stamp,author_id=self.author_id)
            if primary_key is not None:
                self.id = primary_key
                self.in_db = True
        else:
            print ('The post was already in the database.')