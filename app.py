from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return "<h1>Login Page</h1>"

@app.route('/partner')
def partner():
    return "<h1>Become a Partner</h1>"

@app.route('/about')
def about():
    return "<h1>About Us</h1>"

if __name__ == '__main__':
    app.run(debug=True)
