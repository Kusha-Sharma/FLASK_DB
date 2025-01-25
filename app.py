from flask import Flask, render_template, request, redirect, url_for, flash, session

import sqlite3
import re
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect('database/restaurant.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form['name']
            email = request.form['email']
            address = request.form['address']
            plz = request.form['plz']
            password = request.form['password']
            
            # Basic validation
            if not all([name, email, address, plz, password]):
                flash('All fields are required!')
                return render_template('register.html')
            
            # Email validation
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                flash('Please enter a valid email address!')
                return render_template('register.html')
            
            # PLZ validation (assuming it should be numeric)
            if not plz.isdigit():
                flash('PLZ should contain only numbers!')
                return render_template('register.html')
            
            # Connect to database
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            
            # Check if email already exists
            cursor.execute('SELECT * FROM Users WHERE email = ?', (email,))
            if cursor.fetchone():
                conn.close()
                flash('Email already registered!')
                return render_template('register.html')
            
            # Insert new user with initial balance of 100
            cursor.execute('''INSERT INTO Users 
                            (username, address, email, pincode, password, current) 
                            VALUES (?, ?, ?, ?, ?, ?)''',
                            (name, address, email, plz, password, '100'))
            
            conn.commit()
            conn.close()
            
            flash('Registration successful! You can now login.')
            return redirect(url_for('login'))
            
        except sqlite3.Error as e:
            flash(f'Database error: {str(e)}')
            return render_template('register.html')
        
        except Exception as e:
            flash(f'An error occurred: {str(e)}')
            return render_template('register.html')
    
    # If GET request, show the registration form
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    print(" Login page accessed!")  # Debugging

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        print(f" Received Login Request: email={email}, password={password}")

        if not email or not password:
            flash(" Email and password are required!")
            return render_template('login.html')

        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()

            # Fetch user from database
            cursor.execute("SELECT * FROM Users WHERE email = ?", (email,))
            user = cursor.fetchone()
            conn.close()

            print(f" User fetched from database: {user}")

            if user and user[4] == password:  # Remove password hashing temporarily for debugging
                session['user_id'] = user[0]
                session['email'] = user[3]

                print(f" SUCCESS: User {session['user_id']} logged in!")
                flash(" Login successful! Redirecting...")
                return redirect(url_for('restaurants'))
            else:
                print(" ERROR: Incorrect email or password")
                flash(" Incorrect email or password!")
                return render_template('login.html')

        except sqlite3.Error as e:
            print(f" DATABASE ERROR: {str(e)}")
            flash(f" Database error: {str(e)}")
            return render_template('login.html')

    return render_template('login.html')


@app.route('/restaurants')
def restaurants():
    if 'user_id' in session:
        print(f" User {session['user_id']} accessed restaurants page.")
        return render_template('restaurants.html')
    else:
        flash(" You need to log in first!")
        return redirect(url_for('login'))


@app.route('/partner', methods=['GET'])
def partner():
    return render_template('partner.html')

@app.route('/partner/register', methods=['POST'])
def partner_register():
    if request.method == 'POST':
        restaurant_name = request.form['restaurant-name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        plz = request.form['plz']
        password = generate_password_hash(request.form['password'])

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO restaurants (restaurant_name, email, phone, address, plz, password) VALUES (?, ?, ?, ?, ?, ?)',
                         (restaurant_name, email, phone, address, plz, password))
            conn.commit()
            flash('Registration successful!')
            return redirect(url_for('partner'))
        except sqlite3.IntegrityError:
            flash('Email already exists!')
        finally:
            conn.close()
    return redirect(url_for('partner'))

@app.route('/partner/login', methods=['POST'])
def partner_login():
    if request.method == 'POST':
        email = request.form['login-email']
        password = request.form['login-password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM restaurants WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']  # Store user ID in session
            flash('Logged in successfully!')
            return redirect(url_for('partner_dashboard'))
        else:
            flash('Invalid email or password!')
            return redirect(url_for('partner'))

@app.route('/partner/dashboard', methods=['GET', 'POST'])
def partner_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('partner'))
    
    conn = get_db_connection()
    restaurant = conn.execute('SELECT * FROM restaurants WHERE id = ?', (session['user_id'],)).fetchone()
    
    if request.method == 'POST':
        opening_hours_start = request.form['opening_hours_start']
        opening_hours_end = request.form['opening_hours_end']
        opening_hours = f"{opening_hours_start} to {opening_hours_end}"
        delivery_postcode = request.form['delivery_postcode']
        
        # Handle file upload
        if 'photo' in request.files:
            file = request.files['photo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                conn.execute('UPDATE restaurants SET photo_url = ? WHERE id = ?', (filename, session['user_id']))
        
        conn.execute('UPDATE restaurants SET opening_hours = ?, delivery_postcode = ? WHERE id = ?',
                     (opening_hours, delivery_postcode, session['user_id']))
        conn.commit()
        flash('Information updated successfully!')
    
    restaurant = conn.execute('SELECT * FROM restaurants WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    
    return render_template('dashboard.html', restaurant=restaurant)

@app.route('/make_menu')
def make_menu():
    return render_template('MakeMenu.html')

@app.route('/order_history')
def order_history():
    return render_template('OrderHistory.html')

@app.route('/about')
def about():
    return render_template('aboutUS.html')

if __name__ == '__main__':
    app.run(debug=True)
