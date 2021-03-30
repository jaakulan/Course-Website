from flask import Flask
app = Flask(__name__)
from flask import Flask, flash, render_template, request, g,session, redirect, url_for, escape
import sqlite3

DATABASE='./cw.db'
app.debug = True
app.secret_key=b'abbas'

def get_db():
    db=getattr(g,'_database',None)
    if db is None:
        db=g._database=sqlite3.connect(DATABASE)
    return db

def make_dicts(cursor,row):
    return dict((cursor.description[idx][0], value)
                for idx,value in enumerate(row))

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def get_user_and_pass(user: str):
    return query_db('select password,username from accounts where username=?',(user,));

def get_marks(user: str):
    return query_db('select a1,a2,a3,midterm,final,lab from marks where utorid=?',(user,));

def create_remark_request(user: str,reason: str, a1, a2, a3, midterm, lab, final):
    return query_db('insert into remarks values(?,?,?,?,?,?,?,?)',(user,reason,a1,a2,a3,midterm,lab,final));

def create_feedback(instructor: str, likeinstructor: str, improveinstructor: str, likelabs: str, improvelabs: str):
    return query_db('insert into feedback values(?,?,?,?,?)',(instructor,likeinstructor,improveinstructor,likelabs,improvelabs));

def all_instructors():
    return query_db('select utorid from accounts where instructor=true');

def get_feedback_for_instructor(instructor: str):
    return query_db('select likeinstructor, improveinstructor, likelabs, improvelabs from feedback where instructorid = ?',(instructor,));

def get_all_marks(user: str):
    return query_db('select utorid, a1,a2,a3,midterm,final,lab from marks');

def update_marks(user: str,a1,a2,a3,midterm,lab,final):
    return query_db('update marks set a1=?, a2=?, a3=?, midterm=?, final=?, lab=? where utorid = ?',(a1,a2,a3,midterm,lab,final,user));

def get_remark_requests():
    return query_db('select utorid, reason,a1,a2,a3,midterm,lab,final from remarks');

#add query for adding user
@app.route('/')
def home():
    db = get_db();
    db.row_factory = make_dicts
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return "Hello Boss!"
        session['logged_in'] = False
    db.close();

@app.route('/login', methods=['POST'])
def do_login():
    upass = get_user_and_pass(request.form['username']);
    print(upass)
    if len(upass) != 0 and request.form['password'] == upass[0][1] :
        session['logged_in'] = True
    else:
        session['logged_in'] = False
        flash('wrong password!')
    return home()

#@app.route('/<page>.html')
#def normal(page=None):
#    return render_template(page+'.html')
