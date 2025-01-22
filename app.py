import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from supabase import create_client, Client
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from flask import Flask

# Flask Setup
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # Secret key for sessions and CSRF
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')  # PostgreSQL URI from Supabase
db = SQLAlchemy(app)

# Initialize Supabase Client
supabase_url = os.getenv('SUPABASE_URL')  # Your Supabase URL
supabase_key = os.getenv('SUPABASE_KEY')  # Your Supabase Key
supabase: Client = create_client(supabase_url, supabase_key)

# Form for Login and Registration
class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')

class RegisterForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        # Check in Supabase Database
        user = supabase.table('users').select('username', 'password').eq('username', username).execute()
        if user and check_password_hash(user['password'], password):
            return redirect(url_for('index'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = generate_password_hash(form.password.data)
        # Add user to Supabase Database
        supabase.table('users').insert({"username": username, "password": password}).execute()
        flash('Registration successful', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
