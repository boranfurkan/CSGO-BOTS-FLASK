from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from .models import User
from website.db.db import db

# Initialize blueprint - a way to organize different routes
auth = Blueprint('auth', __name__)


# Route for login
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Retrieve the email and password from the form
        email = request.form.get('email')
        password = request.form.get('password')

        # Find the user by email
        user = User.query.filter_by(email=email).first()
        if user:
            # Check the password
            if check_password_hash(user.password, password):
                # Login the user
                login_user(user, remember=True)
                flash('Successfully Logged In', category='success')
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    # Render the login template
    return render_template("login.html", user=current_user)


# Route for logout
@auth.route('/logout')
@login_required
def logout():
    # Logout the user
    logout_user()
    flash('Successfully Logged Out', category='success')
    return redirect(url_for('auth.login'))


# Route for sign up
@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        # Retrieve the email, first name, and passwords from the form
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # Find the user by email
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            # Create a new user
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='scrypt'))
            db.session.add(new_user)
            db.session.commit()
            # Login the new user
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.configs'))

    # Render the sign-up template
    return render_template("sign_up.html", user=current_user)
