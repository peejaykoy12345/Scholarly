import secrets, os
from flask import render_template, flash
from flask_login import current_user, login_required, logout_user, login_user
from Scholarly import app, db, bcrypt
from Scholarly.models import User, Notes
from Scholarly.forms import LoginForm, RegistrationForm, AccountForm
from PIL import Image

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

