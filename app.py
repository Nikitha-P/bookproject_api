from flask import Flask, jsonify, render_template, request, redirect, session
from models import *
from datetime import datetime
import os
from sqlalchemy import and_

app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]="postgresql://hiuhzcljbovvxi:58a916a44c5f136d24f70be0e318fce9c88ff033818d374f700a6c032c59f72e@ec2-44-194-54-123.compute-1.amazonaws.com:5432/dcgqhoef9cgne8"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False

app.secret_key = "abcd"
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/")
def index():
    if('email' in session):
        return render_template("dashboard.html",email=session['email'],fi=-1)
    return render_template("home.html")

@app.route("/register", methods=['GET','POST'])
def register():
    if request.method=="GET":
        return render_template("register.html")
    else:
        name=request.form.get('name')
        
        email=request.form.get('email')
        password=request.form.get('password')
        time1=datetime.now()
        print(name,email,password)
        r=Register(fname=name,email=email,password=password)
        db.session.add(r)
        # db.session.delete()
        db.session.commit()

        s=Register.query.all()
        # db.session.delete(s)
        # db.session.commit()
        # for i in s:
        #     print(f"{i.time}")
        
        return render_template("sample3.html",s=s)



@app.route("/login", methods=['GET','POST'])
def login():
    if('email' in session):
        return render_template("dashboard.html",email=session['email'],fi=-1)

    if request.method=="GET":
        return render_template("register.html")

    else:
        email1=request.form.get('email')
        password1=request.form.get('password')
        data=Register.query.all()
        # data = db.session.query(Register).filter(Register.email == email1)
        # sample=Register.query.filter_by(Register.email="abcd@gmail.com")
        e=0
        p=0
        for i in data:
            if i.email==email1:
                e=1
                if i.password==password1:
                    p=1
                    app.secret_key=i.email
                    session['email'] = app.secret_key
                    return redirect('/login/dashboard')
        if(e==0 and p==0):
            return render_template("register.html",e=0)
        if(e==1 and p==0):
            return render_template("register.html",p=0)



@app.route('/login/dashboard', methods=['GET','POST'])
def dashboard():
    if('email' in session and session['email'] ==app.secret_key):
        if request.method=="POST":
            d=request.form.get('isbn')
            # detail=Book.query.filter_by(isbn=d).all()
            print(d)
            val="%"+d+"%"
            b1=Book.query.filter(Book.isbn.like(val)).all()
            b2=Book.query.filter(Book.name.like(val)).all()
            b3=Book.query.filter(Book.author.like(val)).all()
            b4=Book.query.filter(Book.year.like(val)).all()
            b=b1+b2+b3+b4
           
            print(b)
            return render_template("dashboard.html",email=app.secret_key,l=b,fi=len(b))
        return render_template("dashboard.html",email=app.secret_key,fi=-1)


    return render_template("register.html")  



@app.route('/login/dashboard/bookdetails', methods=['GET','POST'])
def bookdetails():
    if('email' in session and session['email'] ==app.secret_key):
        if request.method=="POST":
            bdetails=request.form.get('detailbook')
            print(bdetails)
            detail=Book.query.filter_by(isbn=bdetails).all()
            l=Reviews.query.filter_by(isbn=bdetails).all()
            check=Reviews.query.filter(and_(Reviews.email == app.secret_key, Reviews.isbn == bdetails)).all()
            print(check)
            addsh=Shelf.query.filter(and_(Shelf.email == app.secret_key, Shelf.isbn == bdetails)).all()
            return render_template("bookdetails.html",bdetails=detail,clen=len(check),revlist=l,lenlist=len(l),Ulist=check,addl=len(addsh)) 

    return redirect('/login/dashboard')



@app.route('/login/dashboard/review', methods=['GET','POST'])
def review():
    if('email' in session and session['email'] ==app.secret_key):
        if request.method=="POST":
            re=request.form.get('review')
            reisbn=request.form.get('reisbn')
            star=request.form.get('star')
            l=Reviews.query.all()
            print(star)
            r=Reviews(id=len(l)+1,review=re,email=app.secret_key,isbn=reisbn,rating=star)
            db.session.add(r)
            db.session.commit()
            print(reisbn)
            l=Reviews.query.all()
            print(l)
            return redirect('/login/dashboard')
            
    return redirect('/login/dashboard')


@app.route('/login/shelf', methods=['GET','POST'])
def shelf():
    if('email' in session and session['email'] ==app.secret_key):
        m=Shelf.query.filter_by(email=app.secret_key).all()
        return render_template("shelf.html",m=m)
    return render_template("register.html")  

@app.route('/login/dashboard/shelfadd', methods=['GET','POST'])
def shelfadd():
    m=Shelf.query.all()
    reisbn=request.form.get('shelf')
    de=Book.query.filter_by(isbn=reisbn).all()
    print(de[0].name)
    r=Shelf(id=len(m)+1,isbn=reisbn,name=de[0].name,author=de[0].author,year=de[0].year,email=app.secret_key)
    db.session.add(r)
    db.session.commit()
    return redirect('/login/shelf')

@app.route('/login/dashboard/shelfdel', methods=['GET','POST'])
def shelfdel():
    reisbn=request.form.get('shelfd')
    r=Shelf.query.filter(and_(Shelf.email == app.secret_key, Shelf.isbn == reisbn)).delete()
    # db.session.add(r)
    db.session.commit()
    return redirect('/login/shelf')

@app.route('/logout')
def logout():
    session.pop('email')       
    return redirect('/login')


@app.route("/api/search", methods=["POST"])
def searchAPI():
    requestData=request.get_json()
    value=requestData.get("search")
    print(value)
    val="%"+value+"%"
    b1=Book.query.filter(Book.isbn.like(val)).all()
    b2=Book.query.filter(Book.name.like(val)).all()
    b3=Book.query.filter(Book.author.like(val)).all()
    b4=Book.query.filter(Book.year.like(val)).all()
    b=b1+b2+b3+b4
    print(b)
    b[0].isbn
    li=[]
    for book in b:
        diction={}
        diction["isbn"]=book.isbn
        diction["name"]=book.name
        diction["author"]=book.author
        diction["year"]=book.year
        li.append(diction)
    return jsonify({"books":li}),200

