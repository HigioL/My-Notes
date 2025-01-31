from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import re  # For email validation

auth = Blueprint('auth', __name__)

# Helper function to validate email format
def is_valid_email(email):
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex, email) is not None

@auth.route('/login', methods=['GET', 'POST'])
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
    flash("You have been logged out.", category='success')
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
        elif not is_valid_email(email):
            flash("Invalid email format", category='error')
        elif not first_name:
            flash("First Name cannot be empty", category='error')
        elif len(first_name) < 2:
            flash("First Name must be greater than 2 characters", category='error')
        elif password1 != password2:
            flash("Passwords do not match, try again", category='error')
        elif len(password1) < 8:
            flash("Password must be at least 8 characters", category='error')
        else:
            try:
                new_user = User(
                    email=email,
                    first_name=first_name,
                    password=generate_password_hash(password1, method='pbkdf2:sha256')
                )
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=True)
                flash("Account created!", category='success')
                return redirect(url_for('views.home'))
            except Exception as e:
                db.session.rollback()
                flash("An error occurred while creating your account. Please try again.", category='error')

    return render_template("sign_up.html", user=current_user)