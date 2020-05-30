from flask import render_template,redirect,request,url_for,flash,g
from flask_login import login_user,logout_user,login_required,current_user
from . import auth
from ..db.UserModel import User
from ..db.config import Database,Config
from .forms import LoginForm,RegistrationForm,\
UpdatePasswordForm,PasswordResetEmailForm,ResetPasswordForm, EmailUpdateForm
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

@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.blueprint != 'auth' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


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
    if form.validate_on_submit():
        try:
            user = User(email=form.email.data,
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
    db = Database(Config)
    g.db = db.connection()
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    g.db.close()
    return redirect(url_for('main.index'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/confirm')
@login_required
def resend_confirmation():
    print ('This is in the resend_confirmation email view function')
    token = current_user.generate_confirmation_token()
    send_email(current_user.email,'Confirm Your Account',
        'auth/email/confirm',user=current_user,token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))

@auth.route('/update_password',methods=['GET','POST'])
@login_required
def update_password():
    form = UpdatePasswordForm()
    if form.validate_on_submit():
        db = Database(Config)
        g.db = db.connection()
        try: 
            current_user.password = form.new_password.data
            new_prop = {'password_hash': current_user.password_hash}
            current_user.update(new_prop)
        except:
            print ('Something went wrong while updating the password')
        finally:
            flash("You've sucessfully updated your password!")
            g.db.close()
            return redirect(url_for('main.index'))

    return render_template('auth/update_password.html', form=form)

@auth.route('/reset_password',methods=['GET','POST'])
def send_reset_password_email():
    form = PasswordResetEmailForm()
    if form.validate_on_submit():
        try:
            user = User(email=form.email.data)
            if user.in_db:
                token = user.generate_confirmation_token()
                send_email(user.email,'Password Reset Link',
                'auth/email/reset_password',user=user,token=token)
                flash('Your password reset email has been sent!')
            else:
                flash('No such email exists in our database')
                return redirect(url_for('auth.send_reset_password_email'))
        except:
            print ('Something went wrong sending the password reset email')
    return render_template('auth/password_email_reset.html',form=form)

@auth.route('/reset_password/<username>/<token>',methods=['GET','POST'])
def reset_password(username,token):
    try:
        form = ResetPasswordForm()
        db = Database(Config)
        g.db = db.connection()
        user = User(username=username)
        if form.validate_on_submit():
            user.password = form.new_password.data
            new_prop = {"password_hash":user.password_hash}
            user.update(new_prop)
            flash('Your password has been successfully reset!')
            return redirect(url_for('main.index'))

        if user.confirm(token):
            return render_template('auth/reset_password.html',form=form)
        else:
            flash('Invalid or expired token.')
            return redirect(url_for('auth.send_reset_password_email'))
    except:
        print ('Something went wrong resetting the password')

@auth.route('/update_email',methods=['GET','POST'])
@login_required
def send_update_email():
    form = EmailUpdateForm()
    if form.validate_on_submit():
        token = current_user.generate_confirmation_token()
        send_email(form.email.data,'Email Update Confirmation Link',
            'auth/email/update_email',new_email=form.email.data,token=token)
        flash('A confirmation link was sent to the new email you entered.')
        form.email.data = ''
    return render_template('auth/Email_update.html',form=form)

@auth.route('/update_email/<email>/<token>')
@login_required
def update_email(email,token):
    if current_user.confirm(token):
        db = Database(Config)
        g.db = db.connection()
        new_prop = {'email':email}
        current_user.update(new_prop)
        flash('Your email has been successfully updated!')
    else:
        flash('Invalid or expired token.')
    return redirect(url_for('main.index'))