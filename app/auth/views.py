from flask import render_template,redirect,request,url_for,flash,g
from flask_login import login_user,logout_user,login_required
from . import auth
from ..db.UserModel import User
from ..db.config import Database,Config
from .forms import LoginForm
from .forms import RegistrationForm
from psycopg2 import Error

@auth.teardown_request
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

@auth.before_request
def init_db_session():
    db = Database(Config)
    db.get_db()

@auth.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            # db = Database(Config)
            # conn = db.get_db()
            user = User(email=form.email.data)

            # print ('''This is the result of calling the 
            # verify_password method: ''',user.verify_password(form.password.data))

            if user.in_db is True and user.verify_password(form.password.data):
                login_user(user,form.remember_me.data)
                next = request.args.get('next')
                if next is None or not next.startswith('/'):
                    next = url_for('main.index')
                return redirect(next)
            flash('Invalid username or password.')
        except Error as e:
            print ('There was a problem connecting to the database: ',e)
    return render_template('auth/login.html',form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been signed out.')
    return redirect(url_for('main.index'))

@auth.route('/register',methods=['GET','POST'])
def register():
    form = RegistrationForm()
    print ('I am getting this far??????????????')
    if form.validate_on_submit():
        try:
            user = User(email=form.email.data,
                        role_id = 3,
                        password = form.password.data,
                        username=form.username.data)
            user.insert()
            flash('You can now login.')
            return redirect(url_for('auth.login'))
        except Error as e:
            print ('There was an error registering the user: ',e)
    return render_template('auth/register.html',form=form)
    