from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for flashing messages

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

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/partner')
def partner():
    return render_template('partner.html')

@app.route('/about')
def about():
    return render_template('aboutUS.html')

if __name__ == '__main__':
    app.run(debug=True)
