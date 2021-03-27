from flask import Flask
app = Flask(__name__)
from flask import render_template, url_for
app.debug = True

@app.route('/')
def hello():
    return render_template('login.html')

