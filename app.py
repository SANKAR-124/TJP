from flask import Flask, render_template,jsonify, request, redirect, url_for, flash
import os
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash,generate_password_hash
from datetime import datetime,UTC



app=Flask(__name__)
app.secret_key="tja"

app.config['SQLALCHEMY_DATABASE_URI']=os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:1246@localhost/tjp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)

class User(db.Model):
    __tablename__='USER'
    User_ID=db.Column(db.Integer,primary_key=True)
    Name=db.Column(db.String(50),nullable=False)
    User_name=db.Column(db.String(50),nullable=False,unique=True)
    Email_ID=db.Column(db.String(100),unique=True,nullable=False)
    password_hash=db.Column(db.String(255),nullable=False)
    age=db.Column(db.Integer)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)

    


@app.route('/')
def home():
    return jsonify(message="hello")

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=='POST':
        name=request.form.get('name')
        username=request.form.get('username')
        email=request.form.get('email')
        age=request.form.get('age')
        password=request.form.get('password')
        hashed_pass=generate_password_hash(password,method='pbkdf2:sha256',salt_length=8)
        user_exists=User.query.filter_by(User_name=username).first()
        if user_exists:
            flash("username already taken","error")
            return url_for('signup')
        new_user=User(User_name=username,Name=name,Email_ID=email,age=age,password_hash=hashed_pass)
        db.session.add(new_user)
        db.session.commit()
        return url_for('login')
    else:
        return render_template('signup.html')



if __name__=="__main__":
    app.run(debug=True)
