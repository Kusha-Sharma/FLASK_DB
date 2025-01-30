from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import re
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect('database/database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']
        plz = request.form['plz']
        password = generate_password_hash(request.form['password'])

        with get_db_connection() as conn:
            try:
                conn.execute('INSERT INTO users (username, address, email, pincode, password, current_balance) VALUES (?, ?, ?, ?, ?, ?)',
                             (name, address, email, plz, password, 100))
                conn.commit()
                flash('Registration successful! You can now login.')
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash('Email already exists!')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        with get_db_connection() as conn:
            user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['email'] = user['email']
            flash('Login successful! Redirecting...')
            return redirect(url_for('restaurants'))
        else:
            flash('Invalid email or password!')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/restaurants')
def restaurants():
    if 'user_id' in session:
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        user_postcode = user['pincode']
        user_balance = user['current_balance']
        current_time = datetime.now().strftime('%H:%M:%S')  # Convert current time to string
        restaurants = conn.execute('''
            SELECT * FROM restaurants 
            WHERE delivery_postcode = ? 
            AND ? BETWEEN opening_hours_start AND opening_hours_end
        ''', (user_postcode, current_time)).fetchall()
        conn.close()
        return render_template('restaurants.html', restaurants=restaurants, user_balance=user_balance)
    else:
        flash("You need to log in first!")
        return redirect(url_for('login'))

@app.route('/restaurants/menu/<int:restaurant_id>')
def restaurant_menu(restaurant_id):
    conn = get_db_connection()
    restaurant = conn.execute('SELECT * FROM restaurants WHERE id = ?', (restaurant_id,)).fetchone()
    menu_items = conn.execute('SELECT * FROM menu_items WHERE restaurant_id = ?', (restaurant_id,)).fetchall()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    user_balance = user['current_balance']
    conn.close()
    return render_template('menu.html', restaurant=restaurant, menu_items=menu_items, user_balance=user_balance)

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

        with get_db_connection() as conn:
            try:
                conn.execute('INSERT INTO restaurants (restaurant_name, email, phone, address, plz, password, balance) VALUES (?, ?, ?, ?, ?, ?, ?)',
                             (restaurant_name, email, phone, address, plz, password, 0))
                conn.commit()
                flash('Registration successful!')
                return redirect(url_for('partner'))
            except sqlite3.IntegrityError:
                flash('Email already exists!')
    return redirect(url_for('partner'))

@app.route('/partner/login', methods=['POST'])
def partner_login():
    if request.method == 'POST':
        email = request.form['login-email']
        password = request.form['login-password']
        
        with get_db_connection() as conn:
            user = conn.execute('SELECT * FROM restaurants WHERE email = ?', (email,)).fetchone()
        
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
    restaurant_name = restaurant['restaurant_name']
    
    if request.method == 'POST':
        opening_hours_start = request.form['opening_hours_start']
        opening_hours_end = request.form['opening_hours_end']
        delivery_postcode = request.form['delivery_postcode']
        description = request.form['description']
        
        # Handle file upload
        if 'photo' in request.files:
            file = request.files['photo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                restaurant_folder = os.path.join(app.config['UPLOAD_FOLDER'], restaurant_name)
                if not os.path.exists(restaurant_folder):
                    os.makedirs(restaurant_folder)
                file.save(os.path.join(restaurant_folder, filename))
                conn.execute('UPDATE restaurants SET photo_url = ? WHERE id = ?', (filename, session['user_id']))
        
        conn.execute('UPDATE restaurants SET opening_hours_start = ?, opening_hours_end = ?, delivery_postcode = ?, description = ? WHERE id = ?',
                     (opening_hours_start, opening_hours_end, delivery_postcode, description, session['user_id']))
        conn.commit()
        flash('Information updated successfully!')
    
    restaurant = conn.execute('SELECT * FROM restaurants WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    
    return render_template('dashboard.html', restaurant=restaurant)

@app.route('/partner/make_menu', methods=['GET', 'POST'])
def make_menu():
    if 'user_id' not in session:
        return redirect(url_for('partner'))

    conn = get_db_connection()
    restaurant = conn.execute('SELECT * FROM restaurants WHERE id = ?', (session['user_id'],)).fetchone()
    restaurant_name = restaurant['restaurant_name']

    if request.method == 'POST':
        item_id = request.form.get('id')
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        photo = request.files['photo']
        photo_url = None

        restaurant_folder = os.path.join(app.config['UPLOAD_FOLDER'], restaurant_name)
        if not os.path.exists(restaurant_folder):
            os.makedirs(restaurant_folder)

        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(restaurant_folder, filename))
            photo_url = filename

        if item_id:
            if photo_url:
                conn.execute('UPDATE menu_items SET name = ?, description = ?, price = ?, photo_url = ? WHERE id = ? AND restaurant_id = ?',
                             (name, description, price, photo_url, item_id, session['user_id']))
            else:
                conn.execute('UPDATE menu_items SET name = ?, description = ?, price = ? WHERE id = ? AND restaurant_id = ?',
                             (name, description, price, item_id, session['user_id']))
        else:
            conn.execute('INSERT INTO menu_items (restaurant_id, name, description, price, photo_url) VALUES (?, ?, ?, ?, ?)',
                         (session['user_id'], name, description, price, photo_url))
        conn.commit()
        flash('Menu item saved successfully!')

    menu_items = conn.execute('SELECT * FROM menu_items WHERE restaurant_id = ?', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('MakeMenu.html', menu_items=menu_items, restaurant_name=restaurant_name)

@app.route('/partner/delete_menu_item/<int:item_id>', methods=['POST'])
def delete_menu_item(item_id):
    if 'user_id' not in session:
        return redirect(url_for('partner'))

    conn = get_db_connection()
    conn.execute('DELETE FROM menu_items WHERE id = ? AND restaurant_id = ?', (item_id, session['user_id']))
    conn.commit()
    conn.close()
    flash('Menu item deleted successfully!')
    return redirect(url_for('make_menu'))

@app.route('/order_history')
def order_history():
    return render_template('OrderHistory.html')

@app.route('/about')
def about():
    return render_template('aboutUS.html')

if __name__ == '__main__':
    app.run(debug=True)
