import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from supabase import create_client, Client
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Retrieve credentials
supabase_url = os.getenv("https://ezszgyrkgqzpsyjfvmxo.supabase.co")
supabase_key = os.getenv("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV6c3pneXJrZ3F6cHN5amZ2bXhvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNzUzMDkwMywiZXhwIjoyMDUzMTA2OTAzfQ.BUKe1-C4mLkqh9afZZeR4HOZ2wh_0IRn-IRw-3QCAUI")

# Check if keys are loaded correctly
if not supabase_url or not supabase_key:
    raise ValueError("SUPABASE_URL or SUPABASE_KEY is missing from environment variables")

# Initialize Supabase client
supabase: Client = create_client(supabase_url, supabase_key)

# Flask Setup
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SeyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV6c3pneXJrZ3F6cHN5amZ2bXhvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNzUzMDkwMywiZXhwIjoyMDUzMTA2OTAzfQ.BUKe1-C4mLkqh9afZZeR4HOZ2wh_0IRn-IRw-3QCAUI')  # Secret key for sessions and CSRF
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('postgresql://postgres:[YOUR-PASSWORD]@db.ezszgyrkgqzpsyjfvmxo.supabase.co:5432/postgres')  # PostgreSQL URI from Supabase
db = SQLAlchemy(app)

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
        if user.data and check_password_hash(user.data[0]['password'], password):
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
