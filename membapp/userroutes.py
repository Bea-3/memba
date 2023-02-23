import os,random,string,json,requests
#import 3rd party
from flask import render_template,request,redirect,flash,session,url_for
from werkzeug.security import generate_password_hash,check_password_hash
from sqlalchemy import or_
#import from local files
from membapp import app,db
from membapp.models import User,Party,Topics,Contact,Comments,Lga,State,Donation,Payment
from membapp.forms import ContactForm

#A function that will generate a random sample using ascii
def generate_name():
    filename = random.sample(string.ascii_lowercase,10) #will return a list
    return ''.join(filename) #join every member of the list filename together with seperator ''. (no space)


# custom_case = ['a','b','c']

#create the routes
@app.route("/")
def home():
    contact = ContactForm()
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1.0/listall")
        if response:
            rspjson = json.loads(response.text)
        else:
            rspjson = dict()
    except:
        rspjson = dict()
    return render_template('user/home.html',contact=contact,rspjson=rspjson)



@app.route("/check_username", methods=["POST", "GET"])
def check_username():
    if request.method == "GET":
        return "Please complete the form normally"
    else:
        email = request.form.get('email')
        userinfo = db.session.query(User).filter(User.user_email==email).first()
        if userinfo == None:
            sendback = {'status':1, 'feedback':'Email is available'}
            return json.dumps(sendback)
        else:
            sendback = {'status':0, 'feedback':'You have registered already, Click <a href=''>here</a> to login'}
            return json.dumps(sendback)

@app.route("/signup")
def user_signup():
    data=db.session.query(Party).all()
    return render_template("user/signup.html",data=data)
    #TO DO: let signup submit by POST to/register below

#This is where the signup form will be submitted.. follow the example of the admin sign up that we did in the morning
@app.route("/register", methods=['POST'])
def register():
    party=request.form.get('partyid')
    email=request.form.get('email')
    pwd=request.form.get('pwd')
    hashed_pwd = generate_password_hash(pwd)
    if party !='' and email !='' and pwd !='':
         #insert into database using ORM method
        u=User(user_fullname='',user_email=email,user_pwd=hashed_pwd,user_partyid=party)
        #add to session
        db.session.add(u)
        db.session.commit()
        #to get the id of the record that has just been inserted
        userid=u.user_id
        session['user']=userid
        return redirect(url_for('user_login'))
    else:
        flash('You must complete all the fields to signup')
        return redirect(url_for('user_signup'))
        #TO DO: retrieve all the form data and insert into User Table
        #set a session session['user']= keep the email
        #redirect them to profile/dashboard

@app.route('/login', methods=['POST','GET'])
def user_login():
    if session.get('user') != None:
        return redirect(url_for('user_dashboard'))
    else:
        if request.method =='GET':
            return render_template("user/login.html")
        else:
            #retrieve the form data
            email=request.form.get('email')
            pwd=request.form.get('pwd')
            #run a query to know if the username exists on the database
            deets=db.session.query(User).filter(User.user_email==email).first()
            if deets != None:   #<user>
                pwd_indb=deets.user_pwd
                #compare the password coming from the form with the hashed password in the db
                chk=check_password_hash(pwd_indb,pwd)
                #if the password check above is right, we should log them in
                #by keeping their details(user-ID) in session['user']
                #AND REDIRECT THEM TO THE user_dashboard
                if chk:
                    id = deets.user_id
                    session['user']=id
                    return redirect(url_for('user_dashboard'))
                else:
                    flash('invalid password')
                    return redirect(url_for('user_login'))
            else:
                return redirect(url_for('user_login'))

@app.route('/dashboard')
def user_dashboard():
    #protect this route so that only logged in user can get here
    if session.get('user') != None:
        #retrieve the details of the logged in user
        id=session['user']
        deets=db.session.query(User).get(id)
        return render_template('user/dashboard.html',deets=deets)
    else:
        return redirect(url_for('user_login'))

@app.route('/logout')
def user_logout():
    #pop the session and redirect to home page
    if session.get('user') !=None:
        session.pop('user', None)
    return redirect('/')

@app.route('/profile',methods=['POST','GET'])
def user_profile():
    id = session['user']
    if id == None:#means not logged in
        return redirect(url_for('user_login'))
    else:
        if request.method == 'GET':
            # deets=db.session.query(User).get(id)
            deets=db.session.query(User).filter(User.user_id==id).first()
            allstates =State.query.all()
            allparties=Party.query.all()
            return render_template('user/profile.html',deets=deets,allstates=allstates,allparties=allparties)
        else:#form was submited
            fullname=request.form.get('fullname')
            phone=request.form.get('phone')
            #update the db using ORM method
            userobj=db.session.query(User).get(id)
            userobj.user_fullname=fullname
            userobj.user_phone=phone
            db.session.commit()
            flash('Profile Updated!')
            return redirect("/profile")

@app.route('/profile/picture',methods=['POST','GET'])
def profile_picture():
    if session.get('user')==None:
        return redirect('/user_login')
    else:
        if request.method=='GET':
            return render_template('user/profile_picture.html')
        else:
            #retrieve the file
            file = request.files['pix'] 
            #to know the filename
            filename = file.filename #original filename
            filetype = file.mimetype
            allowed =['.png', '.jpg','.jpeg']

            if filename !='':
                name,ext =os.path.splitext(filename) 
                if ext.lower() in allowed:
                    newname = generate_name()+ext
                    file.save("membapp/static/uploads/"+newname)
                    #this will upload the picture and save it as picture.png, save it as the original filename

                    userpic = db.session.query(User).get(session['user'])
                    userpic.user_pix = newname
                    db.session.commit()
                    flash("Picture Uploaded")
                    return redirect(url_for('user_dashboard'))
                    # return "File Uploaded" + file.mimetype
                else:
                    return "File extension not allowed"
            else:
                flash("please choose a file")
                return "please choose a file"

#@app.route("/demo")
#def demo():
    # data =db.session.query(User,Party).join(Party).all()
    # data = db.session.query(User.user_fullname, Party.party_name, Party.party_contact,Party.party_shortcode).join(Party).all()
    #data = User.query.join(Party).add_columns(Party).filter(Party.party_name=='Labour Party').all()
    #data = User.query.join(Party).filter(Party.party_name !='Labour Party').add_columns(Party).all()
    #data = User.query.join(Party).filter(User.user_fullname.like('%hen%')).add_columns(Party).all()
    #data = User.query.join(Party).filter(User.user_fullname.ilike('%car%')).add_columns(Party).all()
    #data = User.query.join(Party).filter(User.user_fullname.in_(['hen'])).add_columns(Party).all()
    #data = User.query.join(Party).filter(~User.user_fullname.in_([])).add_columns(Party).all()
    #data = User.query.join(Party).filter(User.user_pix!=None).add_columns(Party).all()
    #data = User.query.join(Party).filter((Party.party_id==1) | (Party.party_id==4)).add_columns(Party).all()
    #data = User.query.join(Party).filter(or_(Party.party_id==1, Party.party_id==4)).add_columns(Party).all()
    #data = db.session.query(Party).filter(Party.party_id==4).first()
    #the above instance represents instance of Party Class, it will give us access to all the variables inside the class table columns + relationship
    #data=db.session.query(User).get(1) #<User 1>
    #return render_template('user/test.html', data=data)

@app.route("/blog")
def content():
    articles = db.session.query(Topics).filter(Topics.topic_status=='1').all()
    return render_template("user/blog.html",articles=articles)

@app.route("/newtopic", methods=["POST","GET"])
def newtopic():
    #check if logged in
    if session.get('user') !=None:
        if request.method == "GET":
            return render_template("user/newtopic.html")
        else:
            content = request.form.get("content")
            if len(content) > 0:
                #step1- create an instance
                t = Topics(topic_title=content, topic_userid=session['user'])
                db.session.add(t)
                db.session.commit()
                if t.topic_id:
                    flash("Post successfully submitted for approval")
                else:
                    flash("Oops,something went wrong.Please try again")
            else:
                flash("You cannot submit an empty post")
            return redirect('/blog')
    else:
        return redirect(url_for('user_login'))

@app.route('/blog/<id>/')
def blog_details(id):
    #different methods of fetching data from the db.
    # blog_deets = db.session.query(Topics).get(id)
    blog_deets=Topics.query.get_or_404(id)
    # blog_deets=db.session.query(Topics).filter(Topics.topic_id==id).first()
    return render_template('user/blog_details.html',blog_deets=blog_deets)

@app.route('/sendcomment/')
def sendcomment():
    id = session['user']
    if id == None:
        return "comment cannot be posted until you are logged in"
    else:
        usermessage = request.args.get('message')
        topic =request.args.get('topicid')
        c = Comments(comment_text=usermessage,comment_topicid=topic,comment_userid=id)
        db.session.add(c)
        db.session.commit()
        commenter = c.commentby.user_fullname
        dateposted = c.comment_date
        sendback = f"<br><i>{usermessage}</i> <br><pre>by {commenter} on {dateposted}</pre>"
        return sendback

@app.route('/contact', methods=["POST","GET"])
def contact_us():
    #creating an instance of the class so that we have access to all the members inside it.
    contact = ContactForm()
    if request.method == "GET":
        return render_template("user/contact_us.html",contact=contact)
    else:
        if contact.validate_on_submit(): #True
            #retrieve form data and insert into db
            email = request.form.get('email')
            upload = contact.screenshot.data #or request.files.get('screenshot)
            msg = contact.message.data
            c=Contact(msg_email=email,msg_content=msg,)
            db.session.add(c)
            db.session.commit()
            flash("Thank you for contacting us")
            return redirect(url_for('contact_us'))
        else:
            return render_template("user/contact_us.html",contact=contact)

@app.route("/ajaxcontact",methods=['POST'])
def contact_ajax():
    form = ContactForm()
    if form.validate_on_submit():
        email = request.form.get('email')
        msg = request.form.get('msg')
        #insert into database and send the feedback to Ajax/Javascript
        return f"{email} and {msg}"
    else:
        return "You need to complete the form"

@app.route('/load_lga/<stateid>')
def load_lga(stateid):
    lgas = db.session.query(Lga).filter(Lga.lga_stateid==stateid).all()
    data2send = "<select class='form-select border-success'>"
    for s in lgas:
        data2send = data2send+"<option>"+s.lga_name +"</option>"
    
    data2send = data2send + "</select>"

    return data2send

# @app.route("/demo",methods=['POST','GET'])
# # @csrf.exempt
# def demo():
#     if request.method =='GET':     
        
#         return render_template("user/test.html")
#     else:
#         #retrieve form data 
#         file = request.files.get('pix')
#         picture_name = file.filename
#         file.save("membapp/static/uploads/"+picture_name)
#         return f'{picture_name}'

@app.route('/donate', methods=["POST","GET"])
def donate():
    if session.get('user') != None:
        deets = User.query.get(session.get('user'))
    else:
        deets=None

    if request.method == 'GET':
        return render_template('user/donation_form.html',deets=deets)
    else:
        amount = request.form.get('amount')
        fullname = request.form.get('fullname')
        d = Donation(don_donor=fullname, don_amt=amount,don_userid=session.get('user'))
        db.session.add(d) ; db.session.commit()
        session['donation_id'] = d.don_id
        #generate ref no and insert into payment table
        refno = int(random.random()*100000000)
        session['reference'] = refno
        return redirect('/confirm')

@app.route('/confirm',methods=["GET","POST"])
def confirm():
    #the condition for them to get to this route is if session donation id is set.
    #but note that users and non users are allowed to donate so session userid will not be present
    if session.get('donation_id') != None:
        if request.method == "GET":
            #we need to have access to the details of the donation.
            donor = db.session.query(Donation).get(session['donation_id'])
            return render_template('user/confirm.html',donor=donor,refno=session['reference'])
        else:
            p = Payment(pay_donid=session.get('donation_id'),pay_ref=session['reference'])
            db.session.add(p); db.session.commit()

            don = Donation.query.get(session.get('donation_id')) #details of the donation
            donor_name = don.don_donor
            amount = don.don_amt * 100
            headers={"Content-Type": "application/json", "Authorization":"Bearer sk_test_264295ada248947036c4c180892981f219d7e270"}
            data={"amount":amount, "reference":session['reference'], "email":donor_name}

            response = requests.post('https://api.paystack.co/transaction/initialize', headers=headers, data=json.dumps(data))
            rspjson = json.loads(response.text)
            if rspjson['status'] == True:
                url = rspjson['data']['authorization_url']
                return redirect(url)
            else:
                return redirect('/confirm')
    else:
        return redirect('/donate')

@app.route('/paystack')
def paystack():
    refid = session.get('reference')
    if refid == None:
        return redirect('/')
    else:
        #connect to paystack verify
        headers={"Content-Type": "application/json", "Authorization":"Bearer sk_test_264295ada248947036c4c180892981f219d7e270"}
        verifyurl = "https://api.paystack.co/transaction/verify/"+str(refid)
        response = requests.get(verifyurl,headers=headers)
        rspjson = json.loads(response.text)
        if rspjson['status']==True:
            #payment was successful
            return rspjson
        else:
            #payment was not successful 
            return "payment was not successful"