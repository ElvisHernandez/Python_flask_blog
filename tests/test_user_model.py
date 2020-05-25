import unittest
from flask import g
from app import create_app
from app.db.config import Database,Config
from app.db.UserModel import User


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db = Database(Config)
        setattr(g,'db',db.connection())

    def tearDown(self):
        if g.db is not None:
            g.db.close()

    def test_password_setter(self):
        u = User('testUser',3,'123456')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User('testUser',3,'123456')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User('testUser',3,'123456')
        self.assertTrue(u.verify_password('123456'))
        self.assertFalse(u.verify_password('567893'))

    def test_password_salts_are_random(self):
        u = User('testUser',3,'123456')
        u2 = User('testUser2',3,'123456')
        self.assertTrue(u.password_hash != u2.password_hash)
        

    