from flask import Flask
app = Flask(__name__)
from flask import render_template, url_for
app.debug = True

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/newAccount')
def makeAccount():
    return render_template('makeAccount.html')
