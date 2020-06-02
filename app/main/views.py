from datetime import datetime
from flask import render_template,session,redirect,url_for,g,flash,current_app,request
from . import main
from .forms import NameForm,EditProfileForm,EditProfileAdminForm
from ..db.config import Config,Database
from ..db.RoleModel import Permissions
from threading import Thread
from flask_login import login_required,current_user
from flask_mail import Message
from ..decorators import admin_required
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
            conn = g.db

            cursor = conn.cursor()
            sql_query = '''SELECT id,name FROM roles;'''
            cursor.execute(sql_query)
            results = cursor.fetchall()

            print ('These are the results of the query: ',results[0][1])

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
    # print ('This is the usernname thats being passed throug the view function: ',username)
    user = User(username=username.lower())
    if user.in_db is False:
        return render_template('404.html')
    else:
        return render_template('user.html',user=user,current_time=datetime.utcnow())

@main.route('/edit-profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data 
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        new_props = {
            'name': current_user.name,
            'location': current_user.location,
            'about_me': current_user.about_me
            }
        current_user.update(new_props)
        flash('Your profile has been updated!')
        return redirect(url_for('.user',username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html',form=form)

@main.route('/edit-profile/<int:primary_id>',methods=['GET','POST'])
@login_required
@admin_required
def edit_profile_admin(primary_id):
    user = User(id=primary_id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = form.role.data
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        new_props = {
            'email': user.email,
            'username': user.username,
            'confirmed': user.confirmed,
            'role_id': user.role,
            'name': user.name,
            'location': user.location,
            'about_me': user.about_me
        }
        user.update(new_props)
        flash('The profile has been updated.')
        return redirect(url_for('.user',username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html',form=form,user=user)