from datetime import datetime
from flask import render_template,session,redirect,url_for,g,flash,current_app,request
from . import main
from .forms import NameForm,EditProfileForm,EditProfileAdminForm,PostForm
from ..db.config import Config,Database
from ..db.RoleModel import Permissions
from ..pagination import Pagination
from threading import Thread
from flask_login import login_required,current_user
from flask_mail import Message
from ..decorators import admin_required
import os
from math import floor
from .. import mail,login_manager
from ..db.UserModel import User
from ..db.PostModel import Post

@main.app_context_processor
def inject_permissions():
    return dict(Permissions=Permissions,User=User)


@main.before_app_request
def open_db_connection():
    db = Database(Config)
    db.get_db()

@main.teardown_request
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permissions.WRITE) and form.validate_on_submit():
        post = Post(body=form.body.data,author_id=current_user.id)
        post.insert()
        return redirect(url_for('.index'))

    posts_per_page = current_app.config.get('POSTS_PER_PAGE',None)
    total_posts = Post.count()
    if total_posts is not None:
        total_pages = floor(total_posts/posts_per_page)
    else:
        flash('Sorry about that, there seems to have been a momentary error.')
        return redirect(url_for('.index'))
    page = request.args.get('page',1,type=int)
    posts = Post.posts_by_page(page,posts_per_page)
    pagination = Pagination(pages=total_pages,page=page)
    
    
    return render_template('index.html',form=form,posts=posts,pagination=pagination)


@main.route('/user/<username>')
def user(username):
    user = User(username=username.lower())
    if user.in_db is False:
        return render_template('404.html')
    else:
        posts = user.posts()
        return render_template('user.html',user=user,current_time=datetime.utcnow(),posts=posts)

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