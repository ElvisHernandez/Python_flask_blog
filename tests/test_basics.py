import unittest
from flask import current_app
from app import create_app

class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        pass

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.asserTrue(current_app.config['TESTING'])