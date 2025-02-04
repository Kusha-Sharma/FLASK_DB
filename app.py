from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
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

@app.route('/checkout', methods=['POST'])
def checkout():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401

    data = request.json
    total_price = data.get('total_price')
    restaurant_id = data.get('restaurant_id')
    # Expected format: [{"menu_item_id": id, "quantity": qty}]
    order_items = data.get('items')

    if not all([total_price, restaurant_id, order_items]):
        return jsonify({'success': False, 'message': 'Invalid request'}), 400

    conn = get_db_connection()
    try:
        # Start transaction
        conn.execute('BEGIN TRANSACTION')
        
        # Check user balance
        user = conn.execute('SELECT current_balance FROM users WHERE id = ?', 
                          (session['user_id'],)).fetchone()
        
        if user is None:
            conn.rollback()
            return jsonify({'success': False, 'message': 'User not found'}), 404

        if user['current_balance'] < total_price:
            conn.rollback()
            return jsonify({'success': False, 'message': 'Insufficient balance'}), 400
        
        # Create order
        cursor = conn.execute('''
            INSERT INTO orders (user_id, restaurant_id, total_amount, status)
            VALUES (?, ?, ?, ?)
        ''', (session['user_id'], restaurant_id, total_price, 'placed'))
        
        order_id = cursor.lastrowid

        # Add order items
        for item in order_items:
            # Get current price of menu item
            menu_item = conn.execute('''
                SELECT price FROM menu_items 
                WHERE id = ? AND restaurant_id = ?
            ''', (item['menu_item_id'], restaurant_id)).fetchone()
            
            if not menu_item:
                conn.rollback()
                return jsonify({'success': False, 'message': 'Invalid menu item'}), 400
            
            # Store order item with current price
            conn.execute('''
                INSERT INTO order_items (order_id, menu_item_id, quantity, price_at_time)
                VALUES (?, ?, ?, ?)
            ''', (order_id, item['menu_item_id'], item['quantity'], menu_item['price']))

        # Update user balance
        new_balance = round(user['current_balance'] - total_price, 2)
        conn.execute('UPDATE users SET current_balance = ? WHERE id = ?', 
                    (new_balance, session['user_id']))

        # Commit transaction
        conn.commit()
        
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        conn.close()
    
    return jsonify({
        'success': True, 
        'message': 'Order placed successfully',
        'order_id': order_id,
        'redirect_url': url_for('payment_success')
    })

@app.route('/payment_success')
def payment_success():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    user = conn.execute('SELECT current_balance FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()

    if user is None:
        return redirect(url_for('login'))

    return render_template('payment_success.html', user_balance=user['current_balance'])


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

@app.route('/partner/orders')
def partner_orders():
    if 'user_id' not in session:
        return redirect(url_for('partner'))
    
    conn = get_db_connection()
    try:
        # Get all orders for the restaurant with related information
        orders = conn.execute('''
            SELECT 
                o.id,
                o.total_amount,
                o.status,
                o.created_at,
                u.username,
                u.id as user_id
            FROM orders o
            JOIN users u ON o.user_id = u.id
            WHERE o.restaurant_id = ?
            ORDER BY 
                CASE 
                    WHEN o.status = 'placed' THEN 1
                    WHEN o.status = 'confirmed' THEN 2
                    WHEN o.status = 'rejected' THEN 3
                END,
                o.created_at DESC
        ''', (session['user_id'],)).fetchall()

        # Process each order
        orders_with_items = []
        for order in orders:
            # Convert SQLite Row to dictionary
            order_dict = dict(order)
            
            # Get items for this order
            items = conn.execute('''
                SELECT 
                    oi.quantity,
                    oi.price_at_time,
                    mi.name
                FROM order_items oi
                JOIN menu_items mi ON oi.menu_item_id = mi.id
                WHERE oi.order_id = ?
            ''', (order['id'],)).fetchall()
            
            # Convert items to list of dictionaries
            items_list = []
            for item in items:
                items_list.append({
                    'name': item['name'],
                    'quantity': item['quantity'],
                    'price': item['price_at_time']
                })
            
            # Add items list to order dictionary
            order_dict['items'] = items_list
            orders_with_items.append(order_dict)

    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")
        flash("An error occurred while fetching orders.")
        orders_with_items = []
    finally:
        conn.close()

    return render_template('OrderHistory.html', orders=orders_with_items)

@app.route('/partner/orders/<int:order_id>/update-status', methods=['POST'])
def update_order_status(order_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    new_status = request.json.get('status')
    
    if new_status not in ['confirmed', 'rejected']:
        return jsonify({'success': False, 'message': 'Invalid status'}), 400

    conn = get_db_connection()
    try:
        # Verify the order belongs to this restaurant
        order = conn.execute('''
            SELECT * FROM orders 
            WHERE id = ? AND restaurant_id = ? AND status = 'placed'
        ''', (order_id, session['user_id'])).fetchone()

        if not order:
            return jsonify({
                'success': False, 
                'message': 'Order not found or already processed'
            }), 404
        
        if new_status == 'confirmed':
            # Update restaurant balance
            restaurant = conn.execute('SELECT balance FROM restaurants WHERE id = ?', 
                                    (session['user_id'],)).fetchone()
            new_balance = round(restaurant['balance'] + (order['total_amount']*0.85), 2)
            conn.execute('UPDATE restaurants SET balance = ? WHERE id = ?', 
                        (new_balance, session['user_id']))
        
        if new_status == 'rejected':
            # Refund user balance
            user = conn.execute('SELECT current_balance FROM users WHERE id = ?', 
                             (order['user_id'],)).fetchone()
            new_balance = round(user['current_balance'] + order['total_amount'], 2)
            conn.execute('UPDATE users SET current_balance = ? WHERE id = ?', 
                        (new_balance, order['user_id']))

        # Update the order status
        conn.execute('''
            UPDATE orders 
            SET status = ? 
            WHERE id = ? AND restaurant_id = ?
        ''', (new_status, order_id, session['user_id']))
        
        conn.commit()
        return jsonify({
            'success': True,
            'message': f'Order {new_status} successfully'
        })
        
    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Database error occurred'
        }), 500
    finally:
        conn.close()

@app.route('/user/orders')
def user_orders():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    try:
        # Get user's current balance
        user = conn.execute('SELECT current_balance FROM users WHERE id = ?', 
                          (session['user_id'],)).fetchone()
        
        # Get all orders for the user with restaurant information
        orders = conn.execute('''
            SELECT 
                o.id,
                o.total_amount,
                o.status,
                o.created_at,
                r.restaurant_name,
                r.id as restaurant_id
            FROM orders o
            JOIN restaurants r ON o.restaurant_id = r.id
            WHERE o.user_id = ?
            ORDER BY o.created_at DESC
        ''', (session['user_id'],)).fetchall()

        # For each order, get its items
        orders_with_items = []
        for order in orders:
            items = conn.execute('''
                SELECT 
                    oi.quantity,
                    oi.price_at_time as price,
                    mi.name
                FROM order_items oi
                JOIN menu_items mi ON oi.menu_item_id = mi.id
                WHERE oi.order_id = ?
            ''', (order['id'],)).fetchall()
            
            # Convert to dictionary and add items
            order_dict = dict(order)
            order_dict['items'] = [dict(item) for item in items]
            orders_with_items.append(order_dict)

    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")
        flash("An error occurred while fetching your orders.")
        orders_with_items = []
        user = None
    finally:
        conn.close()

    return render_template('user_order_history.html', 
                         orders=orders_with_items,
                         user_balance=user['current_balance'] if user else 0)

if __name__ == '__main__':
    app.run(debug=True)
