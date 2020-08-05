from flask import Flask, render_template, session, redirect
from flask_sqlalchemy import SQLAlchemy, request
from werkzeug import secure_filename
from flask_mail import Mail
import json
import os
import math
from datetime import datetime
with open(r'C:\Users\vicky shaw\IdeaProjects\flask\templates\config.json', 'r') as c:
    params = json.load(c)["params"]
local_server = True

app = Flask(__name__)
app.secret_key = 'super secrer key'
app.config['UPLOAD_FOLDER'] = params['upload_location']
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME='prasadvicky231@gmail.com',
    MAIL_PASSWORD='shubham123'

)
mail = Mail(app)
if (local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
db = SQLAlchemy(app)


class Contacts(db.Model):
    # name,phone_no,msg,date,email,sno
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(50), nullable=False)


class Posts(db.Model):
    # name,phone_no,msg,date,email,sno
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=False, nullable=False)
    slug = db.Column(db.String(23), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    tagline = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(12), nullable=True)


@app.route("/")
def index():
    posts = Posts.query.filter_by().all()
    # [0:params['no of posts']]
    last=math.ceil(len(posts)/int(params['no of posts']))
    page=request.args.get('page')

    if(not str(page).isnumeric()):
        page=1
    page=int(page)
    posts=posts[(page-1)*int(params['no of posts']):(page-1)*int(params['no of posts'])+int(params['no of posts'])]
    if(page==1):
        prev_num="#"
        next_num="/?page="+str(page+1)
    elif (page==last):
        prev_num="/?page="+str(page-1)
        next_num="#"
    else:
        prev_num="/?page="+str(page-1)
        next_num="/?page="+str(page+1)
        


    # Pagination logic 
    # first page 
    #    prev=nothing
    #    next=page+1
    # midddle
    #    prev=page-1
    #    next=page+1
    # End
    #    prev=page-1
    #    next=nothing
    return render_template('index.html', params=params, posts=posts,prev_num=prev_num,next_num=next_num)


@app.route("/about")
def about():
    return render_template('about.html', params=params)


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    # playing with the dashboard>>>>
    if ('user' in session and session['user'] == params['admin_user']):
        posts = Posts.query.all()
        return render_template('dashboard.html', params=params, posts=posts)

    if request.method == 'POST':
        # redirect to the admin pannel
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if (username == params['admin_user'] and userpass == params['admin_password']):
            # set the session variable
            session['user'] = username
            posts = Posts.query.all()
            return render_template('dashboard.html', params=params, posts=posts)
    else:
        return render_template('new.html', params=params)

 # uploader


@app.route("/uploader", methods=['GET', 'POST'])
def uploader():
    if ('user' in session and session['user'] == params['admin_user']):
        if request.method == 'POST':
            f = request.files['file1']
            f.save(os.path.join(
                app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            return "uploaded succesfully"


@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')


@app.route("/delete/<string:sno>", methods=['GET', 'POST'])
def delete(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if (request.method == 'POST'):
        # add entry to the database
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        # entry
        # name,phone_no,msg,date,email,sno
        entry = Contacts(name=name, phone_num=phone,
                         msg=message, email=email, date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        mail.send_message('new message from blog',
                          sender=email, recipients=[
                              'prasadvicky231@gmail.com'],
                          body=message+'\n'+phone
                          )

    return render_template('contact.html', params=params)


@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()

    return render_template('post.html', params='params', post=post)
# editing post through the (editbutton)
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        if request.method == 'POST':
            title = request.form.get('title')
            slug = request.form.get('slug')
            content = request.form.get('content')
            tagline = request.form.get('tagline')
            img_file = request.form.get('img_file')
            date = request.form.get('date')
            if sno == '0':
                post = Posts(title=title, slug=slug, content=content,
                             tagline=tagline, img_file=img_file, date=datetime.now())
                db.session.add(post)
                db.session.commit()
                # parts to be modified later
            else:
                post = Posts.query.filter_by(sno=sno)
                post.title = title
                post.slug = slug
                post.content = content
                post.tagline = tagline
                post.img_file = img_file
                post.date = date
                db.session.commit()
                return redirect('/edit/' + sno)
        post = Posts.query.filter_by(sno=sno)
        return render_template('edit.html', params=params, post=post)


app.run(debug=True)
