import os
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from supabase import create_client, Client
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from dotenv import load_dotenv
from markupsafe import Markup

# Load environment variables
load_dotenv()

# Retrieve credentials
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

# Check if keys are loaded correctly
if not supabase_url or not supabase_key:
    raise ValueError("SUPABASE_URL or SUPABASE_KEY is missing from environment variables")

# Initialize Supabase client
supabase: Client = create_client(supabase_url, supabase_key)

# Flask Setup
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # Secret key for sessions and CSRF

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
    username = "User123"  # Replace with dynamic username
    return render_template('index.html', username=username)

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

@app.route('/logout')
def logout():
    flash("You have been logged out", "info")
    return redirect(url_for('login'))

@app.route('/api/routers')
def get_routers():
    routers = supabase.table('routers').select("*").execute()
    return jsonify(routers.data)

@app.route('/api/agents')
def get_agents():
    agents = supabase.table('agents').select("*").execute()
    return jsonify(agents.data)

@app.route('/api/assignments')
def get_assignments():
    assignments = supabase.table('assignments').select("*").execute()
    return jsonify(assignments.data)

# Run the app
if __name__ == '__main__':
    from waitress import serve  # More stable than Flask dev server
    serve(app, host="0.0.0.0", port=8080)
