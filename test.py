from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os


app = Flask(__name__)
sql_uri = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_DATABASE_URI'] = sql_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()

db.init_app(app)

@app.route('/')
def index():

    return "Hello World!"