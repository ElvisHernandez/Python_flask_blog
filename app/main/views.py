from datetime import datetime
from flask import render_template, session, redirect, url_for,g,flash, current_app
from . import main
from .forms import NameForm
from ..db.config import Config,Database,check_user
from threading import Thread
from flask_mail import Message
import os
from .. import mail

@main.teardown_request
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()

    if form.validate_on_submit():
        try:
            db = Database(Config)
            conn = db.get_db()
            is_in_db = check_user(form.name.data,conn)
            if is_in_db is False:
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

@main.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)