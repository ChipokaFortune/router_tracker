import os
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from supabase import create_client, Client
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from dotenv import load_dotenv

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
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Check user in Supabase
        response = supabase.table('users').select('username', 'password').eq('username', username).execute()
        user_data = response.data

        if user_data and check_password_hash(user_data[0]['password'], password):
            return redirect(url_for('index'))

        flash('Invalid credentials', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = generate_password_hash(form.password.data)

        # Add user to Supabase
        supabase.table('users').insert({"username": username, "password": password}).execute()
        flash('Registration successful', 'success')

        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)

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

<h1>Welcome, {{ username }}</h1>

<div class="container">
    <h1>Router Tracker</h1>
    <div class="actions">
        <a href="{{ url_for('add_router') }}" class="btn">Add Router</a>
        <a href="{{ url_for('add_agent') }}" class="btn">Add Agent</a>
        <a href="{{ url_for('assign_router') }}" class="btn">Assign Router</a>
        <a href="{{ url_for('return_router') }}" class="btn">Return Router</a>
    </div>
</div>
