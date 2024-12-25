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
    return render_template('login.html')

@app.route('/partner')
def partner():
    return render_template('partner.html')

@app.route('/about')
def about():
    return render_template('aboutUS.html')

if __name__ == '__main__':
    app.run(debug=True)
