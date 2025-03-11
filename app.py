from flask import Flask, render_template, request, redirect, url_for, flash, session
import pandas as pd
import os
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key

# Database setup
USERS_DB = 'users.csv'
DONATIONS_DB = 'donations.csv'
VOLUNTEERS_DB = 'volunteers.csv'

def init_db():
    # Create users database if it doesn't exist
    if not os.path.exists(USERS_DB):
        df = pd.DataFrame(columns=['id', 'username', 'email', 'password', 'created_at'])
        df.to_csv(USERS_DB, index=False)
        print("Users database initialized.")
    
    # Create donations database if it doesn't exist
    if not os.path.exists(DONATIONS_DB):
        df = pd.DataFrame(columns=['id', 'user_id', 'name', 'email', 'amount', 'message', 'created_at'])
        df.to_csv(DONATIONS_DB, index=False)
        print("Donations database initialized.")
    
    # Create volunteers database if it doesn't exist
    if not os.path.exists(VOLUNTEERS_DB):
        df = pd.DataFrame(columns=['id', 'user_id', 'name', 'email', 'phone', 'skills', 'availability', 'created_at'])
        df.to_csv(VOLUNTEERS_DB, index=False)
        print("Volunteers database initialized.")

def get_users():
    if os.path.exists(USERS_DB):
        return pd.read_csv(USERS_DB)
    return pd.DataFrame(columns=['id', 'username', 'email', 'password', 'created_at'])

def save_users(df):
    df.to_csv(USERS_DB, index=False)

def get_donations():
    if os.path.exists(DONATIONS_DB):
        return pd.read_csv(DONATIONS_DB)
    return pd.DataFrame(columns=['id', 'user_id', 'name', 'email', 'amount', 'message', 'created_at'])

def save_donation(df):
    df.to_csv(DONATIONS_DB, index=False)

def get_volunteers():
    if os.path.exists(VOLUNTEERS_DB):
        return pd.read_csv(VOLUNTEERS_DB)
    return pd.DataFrame(columns=['id', 'user_id', 'name', 'email', 'phone', 'skills', 'availability', 'created_at'])

def save_volunteers(df):
    df.to_csv(VOLUNTEERS_DB, index=False)

# Initialize database
init_db()

@app.route('/')
def home():
    if 'user_id' in session:
        # Get username from database
        users = get_users()
        user = users[users['id'] == session['user_id']]
        if not user.empty:
            username = user.iloc[0]['username']
            return render_template('dashboard.html', username=username)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        users = get_users()
        user = users[users['email'] == email]
        
        if not user.empty and check_password_hash(user.iloc[0]['password'], password):
            session['user_id'] = user.iloc[0]['id']
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Form validation
        if not all([username, email, password, confirm_password]):
            flash('All fields are required', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        
        # Check if email already exists
        users = get_users()
        if not users[users['email'] == email].empty:
            flash('Email already registered', 'danger')
            return render_template('register.html')
        
        # Create new user
        new_user = {
            'id': str(uuid.uuid4()),
            'username': username,
            'email': email,
            'password': generate_password_hash(password),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Add to dataframe and save
        users = pd.concat([users, pd.DataFrame([new_user])], ignore_index=True)
        save_users(users)
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/donation', methods=['GET', 'POST'])
def donation():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        amount = request.form['amount']
        message = request.form['message']
        
        # Form validation
        if not all([name, email, amount]):
            flash('Name, email and amount are required', 'danger')
            return render_template('donation.html')
        
        # Create new donation
        new_donation = {
            'id': str(uuid.uuid4()),
            'user_id': session['user_id'],
            'name': name,
            'email': email,
            'amount': amount,
            'message': message,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Add to dataframe and save
        donations = get_donations()
        donations = pd.concat([donations, pd.DataFrame([new_donation])], ignore_index=True)
        save_donation(donations)
        
        return redirect(url_for('donation_success'))
    
    return render_template('donation.html')

@app.route('/donation/success')
def donation_success():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('donation_success.html')

@app.route('/volunteer', methods=['GET', 'POST'])
def volunteer():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        skills = request.form['skills']
        availability = request.form['availability']
        
        # Form validation
        if not all([name, email, phone, availability]):
            flash('Name, email, phone, and availability are required', 'danger')
            return render_template('volunteer.html')
        
        # Create new volunteer
        new_volunteer = {
            'id': str(uuid.uuid4()),
            'user_id': session['user_id'],
            'name': name,
            'email': email,
            'phone': phone,
            'skills': skills,
            'availability': availability,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Add to dataframe and save
        volunteers = get_volunteers()
        volunteers = pd.concat([volunteers, pd.DataFrame([new_volunteer])], ignore_index=True)
        save_volunteers(volunteers)
        
        return redirect(url_for('volunteer_success'))
    
    return render_template('volunteer.html')

@app.route('/volunteer/success')
def volunteer_success():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('volunteer_success.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

# Create templates directory and files
if not os.path.exists('templates'):
    os.makedirs('templates')

# Login template
with open('templates/login.html', 'w') as f:
    f.write('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #f5f5f5;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .form-container {
            max-width: 450px;
            margin: 80px auto;
            padding: 30px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
        }
        .form-header {
            text-align: center;
            margin-bottom: 25px;
            color: #4A55A2;
        }
        .form-control {
            margin-bottom: 15px;
            border-radius: 5px;
            padding: 12px;
            border: 1px solid #ddd;
        }
        .btn-primary {
            background-color: #4A55A2;
            border: none;
            border-radius: 5px;
            padding: 12px;
            width: 100%;
            font-weight: bold;
            margin-top: 10px;
        }
        .btn-primary:hover {
            background-color: #3A446E;
        }
        .register-link {
            text-align: center;
            margin-top: 20px;
        }
        .alert {
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="form-container">
            <div class="form-header">
                <h2>Login</h2>
                <p>Welcome back! Please login to your account.</p>
            </div>
            
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }}">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <form method="POST">
                <div class="mb-3">
                    <input type="email" class="form-control" id="email" name="email" placeholder="Email Address" required>
                </div>
                <div class="mb-3">
                    <input type="password" class="form-control" id="password" name="password" placeholder="Password" required>
                </div>
                <button type="submit" class="btn btn-primary">Login</button>
            </form>
            
            <div class="register-link">
                <p>Don't have an account? <a href="{{ url_for('register') }}">Register here</a></p>
            </div>
        </div>
    </div>
</body>
</html>
''')

# Register template
with open('templates/register.html', 'w') as f:
    f.write('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Register</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #f5f5f5;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .form-container {
            max-width: 450px;
            margin: 80px auto;
            padding: 30px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
        }
        .form-header {
            text-align: center;
            margin-bottom: 25px;
            color: #4A55A2;
        }
        .form-control {
            margin-bottom: 15px;
            border-radius: 5px;
            padding: 12px;
            border: 1px solid #ddd;
        }
        .btn-primary {
            background-color: #4A55A2;
            border: none;
            border-radius: 5px;
            padding: 12px;
            width: 100%;
            font-weight: bold;
            margin-top: 10px;
        }
        .btn-primary:hover {
            background-color: #3A446E;
        }
        .login-link {
            text-align: center;
            margin-top: 20px;
        }
        .alert {
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="form-container">
            <div class="form-header">
                <h2>Create Account</h2>
                <p>Please fill in the form to create your account.</p>
            </div>
            
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }}">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <form method="POST">
                <div class="mb-3">
                    <input type="text" class="form-control" id="username" name="username" placeholder="Username" required>
                </div>
                <div class="mb-3">
                    <input type="email" class="form-control" id="email" name="email" placeholder="Email Address" required>
                </div>
                <div class="mb-3">
                    <input type="password" class="form-control" id="password" name="password" placeholder="Password" required>
                </div>
                <div class="mb-3">
                    <input type="password" class="form-control" id="confirm_password" name="confirm_password" placeholder="Confirm Password" required>
                </div>
                <button type="submit" class="btn btn-primary">Register</button>
            </form>
            
            <div class="login-link">
                <p>Already have an account? <a href="{{ url_for('login') }}">Login here</a></p>
            </div>
        </div>
    </div>
</body>
</html>
''')

# Dashboard template - updated with donation and volunteering options
with open('templates/dashboard.html', 'w') as f:
    f.write('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #f5f5f5;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .dashboard-container {
            max-width: 800px;
            margin: 80px auto;
            padding: 30px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
        }
        .dashboard-header {
            text-align: center;
            margin-bottom: 25px;
            color: #4A55A2;
        }
        .hello-world {
            text-align: center;
            font-size: 3rem;
            font-weight: bold;
            color: #4A55A2;
            margin: 30px 0;
        }
        .options-container {
            display: flex;
            justify-content: space-around;
            margin: 40px 0;
        }
        .option-card {
            width: 45%;
            padding: 20px;
            text-align: center;
            background: #f8f9fa;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.05);
            transition: transform 0.3s ease;
        }
        .option-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        .option-icon {
            font-size: 3rem;
            margin-bottom: 15px;
            color: #4A55A2;
        }
        .btn-primary {
            background-color: #4A55A2;
            border: none;
            border-radius: 5px;
            padding: 8px 16px;
            font-weight: bold;
            margin-top: 15px;
        }
        .btn-primary:hover {
            background-color: #3A446E;
        }
        .btn-danger {
            background-color: #dc3545;
            border: none;
            border-radius: 5px;
            padding: 8px 16px;
            font-weight: bold;
        }
        .btn-danger:hover {
            background-color: #bb2d3b;
        }
        .alert {
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="dashboard-container">
            <div class="dashboard-header">
                <h2>Welcome, {{ username }}!</h2>
                <p>You have successfully logged in to your account.</p>
            </div>
            
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }}">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <div class="hello-world">
                Hello World
            </div>
            
            <div class="options-container">
                <div class="option-card">
                    <div class="option-icon">💰</div>
                    <h3>Make a Donation</h3>
                    <p>Support our cause by making a donation of any amount.</p>
                    <a href="{{ url_for('donation') }}" class="btn btn-primary">Donate Now</a>
                </div>
                
                <div class="option-card">
                    <div class="option-icon">🤝</div>
                    <h3>Volunteer</h3>
                    <p>Contribute your time and skills to help our organization.</p>
                    <a href="{{ url_for('volunteer') }}" class="btn btn-primary">Volunteer</a>
                </div>
            </div>
            
            <div class="text-center mt-4">
                <a href="{{ url_for('logout') }}" class="btn btn-danger">Logout</a>
            </div>
        </div>
    </div>
</body>
</html>
''')

# Donation Form Template
with open('templates/donation.html', 'w') as f:
    f.write('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Make a Donation</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #f5f5f5;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .form-container {
            max-width: 600px;
            margin: 80px auto;
            padding: 30px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
        }
        .form-header {
            text-align: center;
            margin-bottom: 25px;
            color: #4A55A2;
        }
        .form-control {
            margin-bottom: 15px;
            border-radius: 5px;
            padding: 12px;
            border: 1px solid #ddd;
        }
        .btn-primary {
            background-color: #4A55A2;
            border: none;
            border-radius: 5px;
            padding: 12px;
            width: 100%;
            font-weight: bold;
            margin-top: 10px;
        }
        .btn-primary:hover {
            background-color: #3A446E;
        }
        .btn-secondary {
            background-color: #6c757d;
            border: none;
            border-radius: 5px;
            padding: 12px;
            font-weight: bold;
            margin-top: 10px;
        }
        .btn-secondary:hover {
            background-color: #5a6268;
        }
        .back-link {
            text-align: center;
            margin-top: 20px;
        }
        .alert {
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="form-container">
            <div class="form-header">
                <h2>Make a Donation</h2>
                <p>Your support helps us make a difference. Thank you!</p>
            </div>
            
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }}">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <form method="POST">
                <div class="mb-3">
                    <label for="name" class="form-label">Full Name</label>
                    <input type="text" class="form-control" id="name" name="name" required>
                </div>
                <div class="mb-3">
                    <label for="email" class="form-label">Email Address</label>
                    <input type="email" class="form-control" id="email" name="email" required>
                </div>
                <div class="mb-3">
                    <label for="amount" class="form-label">Donation Amount ($)</label>
                    <input type="number" class="form-control" id="amount" name="amount" min="1" step="1" required>
                </div>
                <div class="mb-3">
                    <label for="message" class="form-label">Message (Optional)</label>
                    <textarea class="form-control" id="message" name="message" rows="3"></textarea>
                </div>
                <div class="row">
                    <div class="col">
                        <a href="{{ url_for('home') }}" class="btn btn-secondary w-100">Cancel</a>
                    </div>
                    <div class="col">
                        <button type="submit" class="btn btn-primary">Donate Now</button>
                    </div>
                </div>
            </form>
            
            <div class="back-link">
                <a href="{{ url_for('home') }}">Back to Dashboard</a>
            </div>
        </div>
    </div>
</body>
</html>
''')

# Donation Success Template
with open('templates/donation_success.html', 'w') as f:
    f.write('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Donation Successful</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #f5f5f5;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .success-container {
            max-width: 600px;
            margin: 80px auto;
            padding: 30px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        .success-icon {
            font-size: 5rem;
            color: #28a745;
            margin-bottom: 20px;
        }
        .success-header {
            color: #4A55A2;
            margin-bottom: 20px;
        }
        .btn-primary {
            background-color: #4A55A2;
            border: none;
            border-radius: 5px;
            padding: 12px 30px;
            font-weight: bold;
            margin-top: 20px;
        }
        .btn-primary:hover {
            background-color: #3A446E;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="success-container">
            <div class="success-icon">✅</div>
            <div class="success-header">
                <h2>Thank You for Your Donation!</h2>
            </div>
            <p>Your generous contribution has been recorded successfully.</p>
            <p>We will notify you with the details of how your donation is being used.</p>
            <p>Thank you for your support!</p>
            <a href="{{ url_for('home') }}" class="btn btn-primary">Return to Dashboard</a>
        </div>
    </div>
</body>
</html>
''')

# Volunteer Form Template
# Volunteer Form Template
with open('templates/volunteer.html', 'w') as f:
    f.write('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Volunteer Registration</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #f5f5f5;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .form-container {
            max-width: 600px;
            margin: 80px auto;
            padding: 30px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
        }
        .form-header {
            text-align: center;
            margin-bottom: 25px;
            color: #4A55A2;
        }
        .form-control {
            margin-bottom: 15px;
            border-radius: 5px;
            padding: 12px;
            border: 1px solid #ddd;
        }
        .btn-primary {
            background-color: #4A55A2;
            border: none;
            border-radius: 5px;
            padding: 12px;
            width: 100%;
            font-weight: bold;
            margin-top: 10px;
        }
        .btn-primary:hover {
            background-color: #3A446E;
        }
        .btn-secondary {
            background-color: #6c757d;
            border: none;
            border-radius: 5px;
            padding: 12px;
            font-weight: bold;
            margin-top: 10px;
        }
        .btn-secondary:hover {
            background-color: #5a6268;
        }
        .back-link {
            text-align: center;
            margin-top: 20px;
        }
        .alert {
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="form-container">
            <div class="form-header">
                <h2>Volunteer Registration</h2>
                <p>Join our team and make a difference!</p>
            </div>
            
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }}">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <form method="POST">
                <div class="mb-3">
                    <label for="name" class="form-label">Full Name</label>
                    <input type="text" class="form-control" id="name" name="name" required>
                </div>
                <div class="mb-3">
                    <label for="email" class="form-label">Email Address</label>
                    <input type="email" class="form-control" id="email" name="email" required>
                </div>
                <div class="mb-3">
                    <label for="phone" class="form-label">Phone Number</label>
                    <input type="tel" class="form-control" id="phone" name="phone" required>
                </div>
                <div class="mb-3">
                    <label for="skills" class="form-label">Skills & Experience</label>
                    <textarea class="form-control" id="skills" name="skills" rows="3"></textarea>
                </div>
                <div class="mb-3">
                    <label for="availability" class="form-label">Availability</label>
                    <select class="form-control" id="availability" name="availability" required>
                        <option value="">Select your availability</option>
                        <option value="Weekdays">Weekdays</option>
                        <option value="Weekends">Weekends</option>
                        <option value="Evenings">Evenings</option>
                        <option value="Flexible">Flexible</option>
                    </select>
                </div>
                <div class="row">
                    <div class="col">
                        <a href="{{ url_for('home') }}" class="btn btn-secondary w-100">Cancel</a>
                    </div>
                    <div class="col">
                        <button type="submit" class="btn btn-primary">Register as Volunteer</button>
                    </div>
                </div>
            </form>
            
            <div class="back-link">
                <a href="{{ url_for('home') }}">Back to Dashboard</a>
            </div>
        </div>
    </div>
</body>
</html>
''')
    
if __name__ == '__main__':
    app.run(debug=True)