from datetime import datetime
from flask import render_template,session,redirect,url_for,g,flash,current_app,request
from . import main
from .forms import NameForm
from ..db.config import Config,Database
from ..db.RoleModel import Permissions
from threading import Thread
from flask_mail import Message
import os
from .. import mail
from ..db.UserModel import User

@main.app_context_processor
def inject_permissions():
    return dict(Permissions=Permissions)

@main.before_request
def open_db_connection():
    db = Database(Config)
    db.get_db()

@main.teardown_request
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()


@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        try:
            # user = User(email="elvishernandezdev@gmail.com",username="Elvis",password="123456")
            # user.insert()

            user = User(username='Elvis')
            print ('The user is a member since: ',user.last_seen)
            user.ping()

            print ('This is the new last_seen user field: ',user.last_seen)



            if user.in_db is False:
                session['known'] = False
                print('The user was not found')
            else:
                print('The user was found')
                session['known'] = True

        except:
            print ('The connection was unsuccessful')
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you changed your name!')
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('.index'))

    return render_template('index.html', form=form, name=session.get('name'),
                            known=session.get('known',False))

# @main.route('/user/<name>')
# def user(name):
#     return render_template('user.html', name=name)

@main.route('/user/<username>')
def user(username):
    print ('This is the usernname thats being passed throug the view function: ',username)
    user = User(username=username)
    if user.in_db is False:
        return render_template('404.html')
    else:
        return render_template('user.html',user=user)