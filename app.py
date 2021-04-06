from flask import Flask
app = Flask(__name__)
from flask import Flask, flash, render_template, request, g,session, redirect, url_for, escape
import sqlite3
import os

DATABASE='./cw.db'
app.debug = True
app.secret_key=os.urandom(12)

#copypasta
def get_db():
    db=getattr(g,'_database',None)
    if db is None:
        db=g._database=sqlite3.connect(DATABASE)
    db.row_factory = make_dicts
    return db

#copypasta
def make_dicts(cursor,row):
    return dict((cursor.description[idx][0], value)
                for idx,value in enumerate(row))

#copypasta
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


#copypasta
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

#new function, executes operations that modify the database
def modify_db(query, args=(), one=False):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    cur.close()

#helper func
def get_user_and_pass(user: str):
    return query_db('select password,username from accounts where username=?',(user,));

#helper func
def get_marks(user: str):
    return query_db('select a1,a2,a3,midterm,final,lab from marks where utorid=?',(user,));

#helper func
def create_remark_request(user: str,reason: str, a1, a2, a3, midterm, lab, final):
    return query_db('insert into remarks values(?,?,?,?,?,?,?,?)',(user,reason,a1,a2,a3,midterm,lab,final));

#helper func
def create_feedback(instructor: str, likeinstructor: str, improveinstructor: str, likelabs: str, improvelabs: str):
    return modify_db('insert into feedback values(?,?,?,?,?)',(instructor,likeinstructor,improveinstructor,likelabs,improvelabs));

#helper func
def all_instructors():
    return query_db('select utorid from accounts where instructor=true');

#helper func
def get_feedback_for_instructor(instructor: str):
    return query_db('select likeinstructor, improveinstructor, likelabs, improvelabs from feedback where instructorid = ?',(instructor,));

#helper func
def get_all_marks():
    return query_db('select utorid, a1,a2,a3,midterm,final,lab from marks');

#helper func
def update_marks(user: str,a1,a2,a3,midterm,lab,final):
    return query_db('update marks set a1=?, a2=?, a3=?, midterm=?, final=?, lab=? where utorid = ?',(a1,a2,a3,midterm,lab,final,user));

#helper func
def get_remark_requests():
    return query_db('select utorid, reason,a1,a2,a3,midterm,lab,final from remarks');

###-----------------------Flask code---------------------###

#add query for adding user

#This directs the user to index or login depending on whether they are logged in
@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('index.html')

@app.route('/newAccount')
def newAccount():
    return render_template('makeAccount.html')

#checks if username/pass are correct and sets session accordingly
@app.route('/login', methods=['POST'])
def do_login():
    upass = get_user_and_pass(request.form['username']);
    #sending password across internet lolololol+no salting/hashing
    print(upass)
    if len(upass) != 0 and request.form['password'] == upass[0]["password"] :
        session['utorid'] = request.form['username'];
        session['instructor'] = True if session['utorid'] in list(map(lambda x: list(x.values())[0], all_instructors())) else False
        session['logged_in'] = True
    else:
        #here for testing
        session['logged_in'] = False
        flash('wrong password!')
    return redirect('/');

#inserts new feedback into database
@app.route('/feedback', methods=['POST'])
def feed_me():
    if session['logged_in'] == False:
        return redirect('/');
    f = request.form.to_dict()
    inst=f["instructors"]
    q1=f['first_quest']
    q2=f['second_quest']
    q3=f['third_quest']
    q4=f['fourth_quest']
    q5=f['long_feedbck']
    #def create_feedback(instructor: str, likeinstructor: str, improveinstructor: str, likelabs: str, improvelabs: str):
    create_feedback(inst,q1,q2,q3,q4)
    return normal("student_feedback");

#Renders the feedback localhost:5000/feedback url
@app.route('/feedback')
def feedback_page():
    if session['logged_in'] == False:
        return redirect('/');
    instructors = all_instructors();
    #turns instructors into a list of instructors like [instructor1,instructor2]
    names = list(map(lambda x: list(x.values())[0], instructors))
    user = session["utorid"]
    print(user)
    if (user in names):
        return view_instructor_feedbck()
    else:
        return render_template('student_feedback.html', names=names)


#Logs out user
@app.route('/logout', methods=['POST'])
def do_logout():
    #security vulnerability here lololol
    session['logged_in'] = False
    return redirect('/')

@app.route('/login', methods=['GET'])
def loginpage():
    return home()

#page to display after logging out(redirection)
@app.route('/logout', methods=['GET'])
def after_logout():
    return home()

@app.route('/newAccount')
def makeAccount():
    return render_template('makeAccount.html')

@app.route('/instructor_feedbck')
def view_instructor_feedbck():
    if 'logged_in' not in session or session['logged_in'] == False:
        return redirect('/');
    user = session['utorid'];
    hate = get_feedback_for_instructor(user);
    return render_template('instructor_feedback.html', feedback=hate, name=user)

@app.route('/listremarks')
def viewremarks():
    if 'logged_in' not in session or session['logged_in'] == False:
        return redirect('/');
    requests = get_remark_requests()
    print(requests)
    return render_template('listremarks.html', feedback=requests)

@app.route('/viewmarks')
def viewmarks():
    if 'logged_in' not in session or session['logged_in'] == False:
        return redirect('/');
    user = session['utorid'];
    marks = get_all_marks();
    print(marks)
    return render_template('studmarks.html', marks=marks, user=user)

@app.route('/studviewgrades')
def viewstdmarks():
    if 'logged_in' not in session or session['logged_in'] == False:
        return redirect('/');
    user = session['utorid'];
    marks = get_marks(user);
    print(marks)
    return render_template('viewgrades.html', mark=marks[0], user=user)

#Gatekeeps content depending on if they are logged in or not
@app.route('/<page>.html')
def normal(page=None):
    if 'logged_in' in session and session['logged_in'] == True:
        return render_template(page+'.html')
    else:
        return redirect('/');
