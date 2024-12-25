import sqlite3
conn = sqlite3.connect('database.db')
print('connected successfully to db')

conn.execute('create table if not exists Users(username TEXT, address TEXT, email TEXT, pincode TEXT, password TEXT,current balance TEXT )')
conn.execute('create table if not exists Restaurant(restaurantName TEXT, address TEXT, email TEXT, zipcode TEXT, password TEXT)')
conn.execute('create table if not exists Items(fooditems TEXT, description TEXT, price TEXT)')
conn.execute('create table if not exists PaymentHistory( username TEXT, Restaurant TEXT, UserBalance TEXT, RestaurantBalance TEXT, Liferplatz TEXT)')
conn.execute('create table if not exists Progress(RestaurantName TEXT, orderedItems TEXT, quantity TEXT, Status TEXT)')
conn.execute('drop table students ')
print('created table')
conn.close()
