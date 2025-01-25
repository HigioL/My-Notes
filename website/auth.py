#This file typically handles authentication routes, such as login, logout, and registration.
#  You can interact with the database here to create new users or authenticate existing ones.

from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)   

#This route is responsible for handling the login page.
#  It checks if the user exists in the database and if the password is correct.
#   If the user exists and the password is correct, the user is redirected to the home page.

@auth.route('/login' ,methods=['GET', 'POST']) 
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in successfully!", category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash("Incorrect password, try again.", category='error')
        else:
            flash("Email does not exist", category='error')
    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        first_name = request.form.get('first_name', '').strip()
        password1 = request.form.get('password1', '').strip()
        password2 = request.form.get('password2', '').strip()

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
           flash("Email already exists", category='error')  
        elif not email:
           flash("Email cannot be empty", category='error')
        elif len(email) < 4:
            flash("Email must be greater than 4 characters", category='error')
        elif not first_name:
            flash("First Name cannot be empty", category='error')
        elif len(first_name) < 2:
            flash("First Name must be greater than 2 characters", category='error')
        elif password1 != password2:
            flash("Passwords do not match, try again", category='error')
        elif len(password1) < 8:
            flash("Password must be at least 8 characters", category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash("Account created!", category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)