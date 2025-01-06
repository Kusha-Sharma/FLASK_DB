from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

def get_db_connection():
    conn = sqlite3.connect('database/restaurant.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')

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
        user = conn.execute('SELECT * FROM restaurants WHERE email = ?', 
                          (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']  # Store user ID in session
            flash('Logged in successfully!')
            return redirect(url_for('partner_dashboard'))
        else:
            flash('Invalid email or password!')
            return redirect(url_for('partner'))

@app.route('/partner/dashboard', methods=['GET'])
def partner_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('partner'))
        
    conn = get_db_connection()
    restaurant = conn.execute('SELECT * FROM restaurants WHERE id = ?', 
                            (session['user_id'],)).fetchone()
    conn.close()
    
    return render_template('dashboard.html', restaurant=restaurant)

@app.route('/about')
def about():
    return render_template('aboutUS.html')

if __name__ == '__main__':
    app.run(debug=True)
