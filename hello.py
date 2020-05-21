from flask import Flask, render_template, session, redirect, url_for, flash, g
from flask_bootstrap import Bootstrap
from datetime import datetime
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import sys

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)
app.config['SECRET_KEY'] = 'MYSECRETKEY'


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
        return False
    else:
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
