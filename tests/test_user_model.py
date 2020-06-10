import unittest
from flask import g
from app import create_app
from app.db.config import Database
from app.db.UserModel import User
import time


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db = Database()
        setattr(g,'db',db.connection())

    def tearDown(self):
        if g.db is not None:
            g.db.close()

    def test_password_setter(self):
        u = User(username='testUser',password='TestPassword')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(username='TestUser',password='TestPassword')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(username='testUser',password='TestPassword')
        self.assertTrue(u.verify_password('TestPassword'))
        self.assertFalse(u.verify_password('RandomPassword'))

    def test_password_salts_are_random(self):
        u = User(username='TestUser1',password="TestPassword")
        u2 = User(username='TestUser2',password='TestPassword')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_valid_confirmation_token(self):
        u = User(id=1,username='TestUser',password="TestPassword")
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))

    def test_invalid_confirmation_token(self):
        u1 = User(id=1,username="TestUser1",password="TestPassword1")
        u2 = User(id=2,username="TestUser2",password="TestPassword2")
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm(token))

    def test_expired_confirmation_token(self):
        u = User(username='TestUser',password="TestPassword")
        token = u.generate_confirmation_token(1)
        time.sleep(2)
        self.assertFalse(u.confirm(token))
    
