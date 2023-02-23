from flask import render_template,redirect,flash,session,request,url_for
from sqlalchemy.sql import text
from sqlalchemy import desc
from werkzeug.security import generate_password_hash,check_password_hash
from membapp import app,db
from membapp.models import Party,Topics

@app.route('/admin/', methods=["POST","GET"])
def admin_home():
    if request.method =='GET':
        return render_template('admin/adminreg.html')
    else:
        #We use .get and the location so that incase the location doesnt exist, it doesn't throw an error
        username = request.form.get('username')
        pwd = request.form.get('pwd')
        #Convert the plain password to hashed value and insert into db
        hashed_pwd = generate_password_hash(pwd)
        #insert into database
        if username !="" or pwd !="":
            query = f"INSERT INTO admin SET admin_username='{username}',admin_pwd='{hashed_pwd}' "
            db.session.execute(text(query))
            db.session.commit()
            flash("Registration successful. Login Here")
            return redirect('/admin/')
        else:
            flash("Username and password must be supplied")
            return redirect('/admin/')

@app.route('/admin/login/', methods=["POST","GET"])
def login():
    if request.method =="GET":
        return render_template("admin/adminlogin.html")
    else:
        username = request.form.get('username')
        pwd = request.form.get("password")
        #writing select query
        query= f"SELECT * FROM admin WHERE admin_username='{username}' "
        result = db.session.execute(text(query))
        total = result.fetchone()
        if total:   #the username exists
            pwd_indb = total[2] #hashed pwd from the database
            #compare this hashed with the pwd coming from the form
            chk = check_password_hash(pwd_indb,pwd) #returns True or False
            if chk == True: #login is successful, save details in session
                session['loggedin']=username
                return redirect("/admin/dashboard")
            else:
                flash("Invalid Credentials")
                return redirect(url_for('login'))

        else:
            flash("Invalid Credentials")
            return redirect(url_for('login'))

#or non hashed password
# @app.route('/admin/login/', methods=["POST","GET"])
# def login():
#     if request.method =="GET":
#         return render_template("admin/adminlogin.html")
#     else:
#         username = request.form.get('username')
#         pwd = request.form.get("password")
#         #writing select query
#         query= f"SELECT * FROM admin WHERE admin_username='{username}' AND admin_pwd='{pwd}' "
#         result = db.session.execute(text(query))
#         total = result.fetchall()   #fetchone() or fetchmany(1)
#         if total:   #the login details are correct
#             #log him in by saving his details in session
#             session['loggedin']=username
#             return redirect("/admin/dashboard")
#         else:
#             flash("Invalid Credentials")
#             return redirect("/admin/login")



@app.route('/admin/dashboard')
def dashboard():
    if session.get('loggedin') != None:
        return render_template('admin/index.html')
    else:
        return redirect('/admin/login')

@app.route('/admin/logout')
def admin_logout():
    if session.get('loggedin') !=None:
        session.pop('loggedin',None) #clear the session and replace with none
    return redirect("/admin/login")

@app.route('/admin/party',methods=["POST", "GET"])
def admin_party():
    if session.get("loggedin") == None:
        return redirect('/login')
    else:
        if request.method == "GET":
            return render_template('admin/adminparty.html')
        else:
            pname = request.form.get('partyname')
            pcode = request.form.get('partycode')
            pcontact = request.form.get('partycontact')
            #insert into the party table using ORM method
            #step1: create an instance of party(ensure that Party is imported from models) obj=Classname(column1=value,column2=value)
            #step2: add to session
            #step3:commit the session
            p = Party(party_name=pname,party_shortcode=pcode,party_contact=pcontact)
            db.session.add(p)
            db.session.commit()
            flash("Party Added")
            return redirect(url_for('parties'))

@app.route('/admin/parties')
def parties():
    if session.get('loggedin') != None:
        #we will fetch from db using ORM method
        # data =db.session.query(Party).order_by(Party.party_shortcode).all()
        # data =db.session.query(Party).offset(2).all()
        #data =db.session.query(Party).order_by(Party.party_shortcode).limit(3).all()
        data =db.session.query(Party).order_by(desc(Party.party_shortcode)).all()
        #without importing,
        # data =db.session.query(Party).order_by(Party.party_shortcode.desc()).all()
        return render_template('admin/all_parties.html',data=data)
    else:
        return redirect('/admin/login')

@app.route('/admin/topics')
def all_topics():
    if session.get('loggedin') == None:#meaning the person is not logged in
        return redirect('/login')
    else:
        #topicdeets = db.session.query(Topics).all()
        topicdeets=Topics.query.all()
        return render_template("admin/alltopics.html",topicdeets=topicdeets)

@app.route('/admin/topics/delete/<id>')
def delete_post(id):
    #retrieve the topic as an object
    topicobj = Topics.query.get_or_404(id)
    db.session.delete(topicobj)
    db.session.commit()
    flash("Topic Sucessfully deleted")
    return redirect(url_for('all_topics'))

@app.route('/admin/topics/edit/<id>')
def edit_topic(id):
    if session.get('loggedin') !=None: #meaning the person IS LOGGED IN
        topic_deets = Topics.query.get(id)
        return render_template('admin/edit_topic.html',topic_deets=topic_deets)
    else:
        return redirect(url_for('login'))

@app.route('/admin/update_topic',methods=['POST','GET'])
def update_topic():
    if session.get('loggedin') !=None:
        newstatus = request.form.get('status')
        topicid = request.form.get('topicid')
        #To update, create an instance of object, set attribute to new value with the object, commit
        t = db.session.query(Topics).get(topicid)
        t.topic_status=newstatus
        db.session.commit()
        flash("Topic successfully updated!")
        return redirect("/admin/topics")
    else:
        return redirect(url_for('login'))