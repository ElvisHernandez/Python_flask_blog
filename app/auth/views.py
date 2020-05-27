from flask import render_template,redirect,request,url_for,flash,g
from flask_login import login_user,logout_user,login_required,current_user
from . import auth
from ..db.UserModel import User
from ..db.config import Database,Config
from .forms import LoginForm
from .forms import RegistrationForm
from psycopg2 import Error
from ..email import send_email

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
            user = User(email=form.email.data)

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
            token = user.generate_confirmation_token()
            send_email(user.email,'Confirm Your Account',
                'auth/email/confirm',user=user,token=token)

            flash('A confirmation email has been sent to the email you provided.')
            return redirect(url_for('main.index'))
        except Error as e:
            print ('There was an error registering the user: ',e)
    return render_template('auth/register.html',form=form)
    
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))