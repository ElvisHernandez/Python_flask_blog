from random import randint
from faker import Faker 
from .UserModel import User
from .PostModel import Post
from .config import Database
from psycopg2 import DatabaseError

def initiate_db():
    db = Database()
    conn = db.get_db()
    return conn

def users(count=100):
    conn = initiate_db()
    fake = Faker()
    i = 0
    while i < count:
        u = User(email=fake.email(),
                 username=fake.user_name(),
                 password='password',
                 confirmed=True,
                 name=fake.name(),
                 location=fake.city(),
                 about_me=fake.text(),
                 member_since=fake.past_date())
        try:
            u.insert()
            i += 1
        except DatabaseError as e:
            print ('There was an error inserting user %s: ' % i, e)

def posts(count=100):
    conn = initiate_db()
    cursor = conn.cursor()
    fake = Faker()
    
    try:
        sql_query = 'SELECT COUNT(*),MIN(id) FROM users;'
        cursor.execute(sql_query)
        user_count,min_user_id = cursor.fetchone()
        
        for i in range(count):
            u = User(id=randint(min_user_id,user_count+min_user_id))
            p = Post(body=fake.text(),
                     time_stamp=fake.past_date(),
                     author_id=u.id)
            p.insert()
    except DatabaseError as e:
        print ('There was an error creating post %s: ' % i,e)
