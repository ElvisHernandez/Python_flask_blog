from flask import Flask, render_template, session, redirect, url_for, flash, g
from flask_bootstrap import Bootstrap
from datetime import datetime
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_mail import Mail, Message
from threading import Thread
import os

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)
app.config['SECRET_KEY'] = 'MYSECRETKEY'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
mail = Mail(app)

app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin <flasky@gmail.com>'


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    # msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
    # mail.send(msg)


def get_db():
    from db.config import Config, Database

    if not hasattr(g, 'db'):
        db = Database(Config)
        g.db = db.connection()
    return g.db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()


def check_user(user, db_connection):
    cursor = db_connection.cursor()
    sql_query = '''SELECT * FROM users WHERE username = %s;'''
    cursor.execute(sql_query, (user,))
    result = cursor.fetchall()
    if len(result) == 0:
        sql_insert = '''INSERT INTO users (username,role_id)
                        VALUES (%s, %s);'''
        cursor.execute(sql_insert, (user, 3))
        db_connection.commit()
        send_email(os.environ.get('ADMIN_EMAIL'),
                   'New User', 'mail/new_user', name=user)
        # print('This is the user: ', result)
        return False
    else:
        # print('This is the user: ', result[0][1])
        return True


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    # print('This is the name that the form is recording: ', form.name.data)

    if form.validate_on_submit():
        db = get_db()
        if db is not None:
            is_in_db = check_user(form.name.data, db)
            if is_in_db is False:
                session['known'] = False
                print('The user was not found')
            else:
                print('The user was found')
                session['known'] = True
        else:
            print("The connection was unsuccessful")

        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you changed your name!')
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'),
                           known=session.get('known', False))


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')

