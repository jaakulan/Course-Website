from flask import Flask
app = Flask(__name__)
from flask import Flask, flash, render_template, request, g,session, redirect, url_for, escape
import sqlite3
import os

DATABASE='./assignment3.db'
app.debug = True
app.secret_key=os.urandom(12)
app.secret_key='liam'

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

def newacct(pas,username,utorid,instructor):
    modify_db('insert into accounts values(?,?,?,?)', [pas,username,utorid,instructor])
    modify_db('insert into marks values(?,?,?,?,?,?,?)', [utorid,0,0,0,0,0,0])

#helper func
def get_user_and_pass(user: str):
    return query_db('select password,username from accounts where utorid=?',(user,));

#helper func
def get_marks(user: str):
    return query_db('select a1,a2,a3,midterm,final,lab from marks where utorid=?',[user],True);

#helper func
def create_remark_request(user: str,reason: str, a1, a2, a3, midterm, lab, final):
    return modify_db('insert into remarks values(?,?,?,?,?,?,?,?)',(user,reason,a1,a2,a3,midterm,lab,final));

#helper func
def create_feedback(instructor: str, likeinstructor: str, improveinstructor: str, likelabs: str, improvelabs: str):
    return modify_db('insert into feedback values(?,?,?,?,?)',(instructor,likeinstructor,improveinstructor,likelabs,improvelabs));

#helper func
def all_instructors():
    return query_db('select utorid from accounts where instructor=true');

def all_students():
    return query_db('select utorid from accounts where instructor=false');

#helper func
def get_feedback_for_instructor(instructor: str):
    return query_db('select likeinstructor, improveinstructor, likelabs, improvelabs from feedback where instructorid = ?',(instructor,));

#helper func
def get_all_marks():
    return query_db('select utorid, a1,a2,a3,midterm,final,lab from marks');

#helper func
def update_marks(user: str,a1,a2,a3,midterm,lab,final):
    return modify_db('update marks set a1=?, a2=?, a3=?, midterm=?, final=?, lab=? where utorid = ?',(a1,a2,a3,midterm,lab,final,user));

#helper func
def get_remark_requests():
    return query_db('select utorid, reason,a1,a2,a3,midterm,lab,final from remarks');

###-----------------------Flask code---------------------###

#add query for adding user

#This directs the user to index or login depending on whether they are logged in
@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html', wrongAccount = "",)
    else:
        return render_template('index.html', instructor = (session['instructor']),usrname=session['utorid'])

@app.route('/newAccount')
def newAccount():
    return render_template('makeAccount.html',usrname=session['utorid'], instructor = (session['instructor']))

@app.route('/makeacct', methods=['POST'])
def modifyaccts():
    usr = request.form['user']
    name = request.form['username']
    pas =request.form['pass']
    istructor = request.form['usr'] == 'instructor'
    newacct(pas,name,usr,istructor);
    #create grades section here

    return redirect('/');

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
        return render_template('login.html', wrongAccount = "Username or Password is Invalid!",usrname=session['utorid'], instructor = (session['instructor']))
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
    if (session['instructor']):
        return view_instructor_feedbck()
    else:
        names = list(map(lambda x: list(x.values())[0], all_instructors()))
        return render_template('student_feedback.html', names=names,usrname=session['utorid'], instructor = (session['instructor']))


#Logs out user
@app.route('/logout', methods=['POST'])
def do_logout():
    #security vulnerability here lololol
    session['logged_in'] = False
    return redirect('/')

@app.route('/newremark', methods=['POST'])
def newremark():
    usr = session['utorid'];
    reason = request.form['reason']
    a1 = request.form['assignment'] == "a1"

    a2 = request.form['assignment'] == "a2"

    a3 = request.form['assignment'] == "a3"

    midterm = request.form['assignment'] == "midterm"

    lab = request.form['assignment'] == "lab"

    final = request.form['assignment'] == "final"
    create_remark_request(usr,reason, a1, a2, a3, midterm, lab, final)
    print(usr,reason,a1,a2,a3,midterm,lab,final);
    return redirect('/newremark.html')


@app.route('/login', methods=['GET'])
def loginpage():
    return home()

#page to display after logging out(redirection)
@app.route('/logout', methods=['GET'])
def after_logout():
    return home()

@app.route('/newAccount')
def makeAccount():
    return render_template('makeAccount.html',usrname=session['utorid'], instructor = (session['instructor']))

@app.route('/instructor_feedback')
def view_instructor_feedbck():
    if 'logged_in' not in session or session['logged_in'] == False:
        return redirect('/');
    user = session['utorid'];
    hate = get_feedback_for_instructor(user);
    return render_template('instructor_feedback.html', feedback=hate, name=user,usrname=session['utorid'], instructor = (session['instructor']))

@app.route('/listremarks')
def viewremarks():
    if 'logged_in' not in session or session['logged_in'] == False:
        return redirect('/');
    requests = get_remark_requests()
    print(requests)
    return render_template('listremarks.html', feedback=requests,usrname=session['utorid'], instructor = (session['instructor']))

@app.route('/viewmarks')
def viewmarks():
    if 'logged_in' not in session or session['logged_in'] == False:
        return redirect('/');
    user = session['utorid'];
    marks = get_all_marks();
    print(marks)
    return render_template('studmarks.html', marks=marks, user=user,usrname=session['utorid'], instructor = (session['instructor']))

@app.route('/studviewgrades')
def viewstdmarks():
    if 'logged_in' not in session or session['logged_in'] == False:
        return redirect('/');
    user = session['utorid'];
    marks = get_marks(user);
    print(marks)
    return render_template('viewgrades.html', mark=marks, user=user,usrname=session['utorid'], instructor = (session['instructor']))

@app.route('/modifygrades', methods=["POST"])
def modifygrades():
    user = request.form['user'];
    a1 = request.form['a1'];
    a2 = request.form['a2'];
    a3 = request.form['a3'];
    midterm = request.form['midterm'];
    final = request.form['final'];
    lab = request.form['lab'];
    marks = get_marks(user)
    if (a1 == ""):
        a1 = marks['a1']
    if (a2 == ""):
        a2 = marks['a2']
    if (a3 == ""):
         a3=marks['a3']
    if (midterm == ""):
        midterm = marks['midterm']
    if (lab == ""):
        lab = marks['lab']
    if (final == ""):
        final = marks['final']
    print(a1,a2,a3,midterm,final,lab)
    #def update_marks(user: str,a1,a2,a3,midterm,lab,final):
    update_marks(user,a1,a2,a3,midterm,lab,final);
    return redirect('/editmarks');

@app.route('/getmarks', methods=['GET'])
def returnmarks():
    if 'logged_in' not in session or session['logged_in'] == False:
        return "go away"
    user = request.args.get('user')
    marks = get_marks(user);
    print(marks)
    return marks

@app.route('/editmarks')
def editmarks():
    if 'logged_in' not in session or session['logged_in'] == False:
        return redirect('/')
    user = session['utorid'];
    studlist = all_students();
    #if you need this explained you probably put the mouse on the computer screen
    studlist = list(map(lambda x: x['utorid'], studlist));
    std = studlist[0]
    marks = get_marks(std);
    print(marks)
    return render_template('editmarks.html', mark=marks, user=std, names=studlist,usrname=session['utorid'], instructor = (session['instructor']))

#Gatekeeps content depending on if they are logged in or not
@app.route('/<page>.html')
def normal(page=None):
    if 'logged_in' in session and session['logged_in'] == True:
        return render_template(page+'.html',usrname=session['utorid'], instructor = (session['instructor']))
    else:
        return redirect('/');
