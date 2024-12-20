import sqlite3
conn = sqlite3.connect('database.db')
print('connected successfully to db')

conn.execute('create table students(name TEXT, addr, TEXT )')
print('created table')
conn.close()
