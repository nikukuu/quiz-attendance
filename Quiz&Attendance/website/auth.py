from flask import Blueprint

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return "You must be logged in to view this page"

@auth.route('/logout')
def logout():
    return "You have been logged out"

@auth.route('/sign-up')
def sign_up():
    return "Account created!"