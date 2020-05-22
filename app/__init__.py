from flask import Flask, render_template, g, current_app
from flask_bootstrap import Bootstrap
from flask_mail import Mail, Message
from flask_moment import Moment
from config import config
from threading import Thread

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

from .db.config import Config,Database