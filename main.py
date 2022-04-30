from flask import Flask,session,render_template,request,redirect,g,url_for
import os
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy
import sqlite3
from sqlalchemy.ext.declarative import declarative_base


app=Flask(__name__)
app.secret_key = os.urandom(24)
engine = None
Base = declarative_base
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.sqlite3'

# class User(db.Model):
#     __tablename__ = 'user'
#     id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     username = db.Column(db.String, unique=False)
#     email = db.Column(db.String, unique=True)
#     password = db.Column(db.String(255))


# class Students(db.Model):
#     __tablename__ = 'student'
#     id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     name  = db.Column(db.String, unique = False)
#     age = db.Column(db.Integer, unique = False)
#     gender = db.Column(db.String, unique = False)



@app.route("/",methods=['GET','POST'])
def index():
    if request.method == 'POST':
        session.pop('user',None)
        if request.form['password']=='password':
            session['user']=request.form['username']
            return redirect(url_for('protected'))
    return render_template('index.html')


@app.route('/protected')
def protected():
    if g.user:
        return render_template('protected.html',user=session['user'])
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('protected.html',user=g.user)

@app.route('/add_student')
def addstudent():
    return render_template('addstudent.html')

@app.route('/add_student/newstudent',methods=['GET','POST'])
def add_student_new():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        elements = (name,age,gender)
        con = sqlite3.connect("test.sqlite3")
        cur = con.cursor()
        insert='''INSERT INTO verification_pending(name,age,gender) VALUES(?,?,?)'''
        cur.execute(insert,elements)
        con.commit()
        return redirect(url_for('addstudent'))
    return render_template('addstudentnew.html')

@app.route('/add_student/pendingdocs')
def pendingdocs():
    con = sqlite3.connect("test.sqlite3")
    cur = con.cursor()
    cur.execute("select * from verification_pending")
    ans = cur.fetchall()
    return render_template('pendingdocs.html',new_students = ans)

@app.route('/add_student/pendingdocs/<int:id>')
def movestage1(id):
    con = sqlite3.connect("test.sqlite3")
    cur = con.cursor()
    cur.execute("select * from verification_pending where new_id=?",(id,))
    ans = cur.fetchall()
    name = ans[0][1]
    age = ans[0][2]
    gender = ans[0][3]
    elements = (name,age,gender)
    insert='''INSERT INTO payment_pending(name,age,gender) VALUES(?,?,?)'''
    cur.execute(insert,elements)
    con.commit()
    cur.execute("delete from verification_pending where new_id=?",(id,))
    con.commit()
    return redirect(url_for('addstudent'))

 
@app.route('/add_student/pendingpay')
def addfinal():
    con = sqlite3.connect("test.sqlite3")
    cur = con.cursor()
    cur.execute("select * from payment_pending")
    ans = cur.fetchall()
    return render_template('pendingpay.html',new_students = ans)

@app.route('/add_student/pendingpay/<int:id>')
def movestage2(id):
    con = sqlite3.connect("test.sqlite3")
    cur = con.cursor()
    cur.execute("select * from payment_pending where new_id=?",(id,))
    ans = cur.fetchall()
    name = ans[0][1]
    age = ans[0][2]
    gender = ans[0][3]
    elements = (name,age,gender)
    insert='''INSERT INTO student(name,age,gender) VALUES(?,?,?)'''
    cur.execute(insert,elements)
    con.commit()
    cur.execute("delete from payment_pending where new_id=?",(id,))
    con.commit()
    return redirect(url_for('addstudent'))


@app.route('/add_teacher',methods=['GET','POST'])
def add_teacher():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        subject = request.form['subject']
        elements = (name,age,gender,subject)
        con = sqlite3.connect("test.sqlite3")
        cur = con.cursor()
        insert='''INSERT INTO teacher(name,age,gender,subject) VALUES(?,?,?,?)'''
        cur.execute(insert,elements)
        con.commit()
        return redirect(url_for('protected'))
    return render_template('addteacher.html')

@app.route('/add_course',methods=['GET','POST'])
def add_course():
    if request.method == 'POST':
        code = request.form['code']
        name = request.form['name']
        number_of_credits = request.form['number_of_credits']
        pre_req = request.form['pre_req']
        elements = (code,name,number_of_credits,pre_req)
        con = sqlite3.connect("test.sqlite3")
        cur = con.cursor()
        insert='''INSERT INTO course(code,name,number_of_credits,pre_req) VALUES(?,?,?,?)'''
        cur.execute(insert,elements)
        con.commit()
        return redirect(url_for('protected'))
    return render_template('addcourse.html')

@app.route('/remove_student')
def remove_student():
    con = sqlite3.connect("test.sqlite3")
    cur = con.cursor()
    cur.execute("select * from student")
    ans = cur.fetchall()
    return render_template('removestudent.html',student=ans)


@app.route('/remove_student/<student>',methods=['GET','POST'])
def remove_student_confirm(student):
    if request.method=='POST':
        if request.form['confirm']=="CONFIRM":
            con = sqlite3.connect("test.sqlite3")
            cur = con.cursor()
            cur.execute("delete from student where name=?",(student,))
            con.commit()
            return redirect(url_for('protected'))
    return render_template('removestudentconfirm.html',student=student)


@app.route('/remove_teacher')
def remove_teacher():
    con = sqlite3.connect("test.sqlite3")
    cur = con.cursor()
    cur.execute("select * from teacher")
    ans = cur.fetchall()
    return render_template('removeteacher.html',teacher=ans)


@app.route('/remove_teacher/<teacher>',methods=['GET','POST'])
def remove_teacher_confirm(teacher):
    if request.method=='POST':
        if request.form['confirm']=="CONFIRM":
            con = sqlite3.connect("test.sqlite3")
            cur = con.cursor()
            cur.execute("delete from teacher where name=?",(teacher,))
            con.commit()
            return redirect(url_for('protected'))
    return render_template('removeteacherconfirm.html',teacher=teacher)

@app.route('/remove_course')
def remove_course():
    con = sqlite3.connect("test.sqlite3")
    cur = con.cursor()
    cur.execute("select * from course")
    ans = cur.fetchall()
    return render_template('removecourse.html',course=ans)


@app.route('/remove_course/<course>',methods=['GET','POST'])
def remove_course_confirm(course):
    if request.method=='POST':
        if request.form['confirm']=="CONFIRM":
            con = sqlite3.connect("test.sqlite3")
            cur = con.cursor()
            cur.execute("delete from course where name=?",(course,))
            con.commit()
            return redirect(url_for('protected'))
    return render_template('removecourseconfirm.html',course=course)

@app.route('/view_student')
def viewstudent():
    con = sqlite3.connect("test.sqlite3")
    cur = con.cursor()
    cur.execute("select * from student")
    ans = cur.fetchall()
    return render_template('viewstudent.html',student = ans)

@app.route('/view_student/<int:sid>')
def viewparticularstudent(sid):
    con = sqlite3.connect("test.sqlite3")
    cur = con.cursor()
    cur.execute("select * from student where id=?",(sid,))
    ans = cur.fetchall()
    cur.execute("select * from student_course where sid=?",(sid,))
    ans2 = cur.fetchall()
    return render_template('viewstudentparticular.html',student = ans, student_course = ans2)


@app.route('/view_teacher')
def viewteacher():
    con = sqlite3.connect("test.sqlite3")
    cur = con.cursor()
    cur.execute("select * from teacher")
    ans = cur.fetchall()
    return render_template('viewteacher.html',teacher = ans)

@app.route('/view_teacher/<int:tid>')
def viewparticularteacher(tid):
    con = sqlite3.connect("test.sqlite3")
    cur = con.cursor()
    cur.execute("select * from teacher where id=?",(tid,))
    ans = cur.fetchall()
    cur.execute("select * from teacher_course where tid=?",(tid,))
    ans2 = cur.fetchall()
    return render_template('viewteacherparticular.html',teacher = ans,teacher_course = ans2)


@app.route('/view_course')
def viewcourse():
    con = sqlite3.connect("test.sqlite3")
    cur = con.cursor()
    cur.execute("select * from course")
    ans = cur.fetchall()
    return render_template('viewcourse.html',course = ans)

@app.route('/view_course/<code>')
def viewparticularcourse(code):
    con = sqlite3.connect("test.sqlite3")
    cur = con.cursor()
    cur.execute("select * from course where code=?",(code,))
    ans = cur.fetchall()
    return render_template('viewcourseparticular.html',course = ans)


@app.route('/student_course',methods=['GET','POST'])
def student_course():
    if request.method=='POST':
        sid = request.form['sid']  
        cid = request.form['cid']
        sem = request.form['sem']
        con = sqlite3.connect("test.sqlite3")
        cur = con.cursor()
        cur.execute("select * from course where code=?",(cid,))
        ans1 = cur.fetchall()
        cur.execute("select * from student where id=?",(sid,))
        ans2 = cur.fetchall()
        if ans1 == None or ans2 == None:
            return("Error course or student does not exist")
        else:
            elements = (sid,cid,ans1[0][1],sem)
            insert='''INSERT INTO student_course(sid,cid,cname,semester) VALUES(?,?,?,?)'''
            cur.execute(insert,elements)
            con.commit()
            return redirect(url_for('protected'))
    return render_template('assigncoursestudent.html')


@app.route('/teacher_course',methods=['GET','POST'])
def teacher_course():
    if request.method=='POST':
        tid = request.form['tid']  
        cid = request.form['cid']
        sem = request.form['sem']
        con = sqlite3.connect("test.sqlite3")
        cur = con.cursor()
        cur.execute("select * from course where code=?",(cid,))
        ans1 = cur.fetchall()
        cur.execute("select * from teacher where id=?",(tid,))
        ans2 = cur.fetchall()
        if ans1 == None or ans2 == None:
            return("Error course or teacher does not exist")
        else:
            elements = (tid,cid,ans1[0][1],sem)
            insert='''INSERT INTO teacher_course(tid,cid,cname,semester) VALUES(?,?,?,?)'''
            cur.execute(insert,elements)
            con.commit()
            return redirect(url_for('protected'))
    return render_template('assigncourseteacher.html')



@app.before_request
def before_request():
    g.user=None
    if 'user' in session:
        g.user = session['user']



if __name__=='__main__':
    app.run(debug=True)




