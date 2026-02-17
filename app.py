from flask import Flask, render_template,jsonify, request, redirect, url_for, flash, session
import os
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash,generate_password_hash
from datetime import datetime,UTC
from sqlalchemy import or_
from flask_login import LoginManager,login_user,logout_user,login_required,current_user,UserMixin


app=Flask(__name__)
app.secret_key="tja"

app.config['SQLALCHEMY_DATABASE_URI']=os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:1246@localhost/tjp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)


class User(UserMixin,db.Model):
    __tablename__='USER'
    User_ID=db.Column(db.Integer,primary_key=True)
    Name=db.Column(db.String(50),nullable=False)
    User_name=db.Column(db.String(50),nullable=False,unique=True)
    Email_ID=db.Column(db.String(100),unique=True,nullable=False)
    password_hash=db.Column(db.String(255),nullable=False)
    age=db.Column(db.Integer)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)
    def get_id(self):
        return str(self.User_ID)

login_manager=LoginManager(app)
login_manager.login_view='login'
@login_manager.user_loader
def load_user(User_ID):
    return User.query.get(int(User_ID))


@app.route('/')
def home():
    return jsonify(message="hello")

@app.route('/signup',methods=['GET','POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
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
            return redirect(url_for('signup'))
        new_user=User(User_name=username,Name=name,Email_ID=email,age=age,password_hash=hashed_pass)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    else:
        return render_template('signup.html')


@app.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method=='POST':
        login_id=request.form.get('login_id')
        user=User.query.filter(or_(User.User_name==login_id,User.Email_ID==login_id)).first()
        password=request.form.get('password')
        if user and check_password_hash(user.password_hash,password):
            # session["User_ID"]=user.User_ID
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash("username/email or password is wrong",'fail')
            return redirect(url_for('login'))
    else:
        return render_template('login.html')
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         login_id = request.form.get('login_id')
#         password = request.form.get('password')

#         # Debug 1: Check what came from the form
#         print(f"--- DEBUG START ---")
#         print(f"Form Login ID: {login_id}") 
#         print(f"Form Password: {password}")

#         # Search for user
#         user = User.query.filter(or_(User.User_name == login_id, User.Email_ID == login_id)).first()
        
#         # Debug 2: Check if user exists
#         if user:
#             print(f"User Found: {user.User_name}")
#             print(f"Stored Hash in DB: {user.password_hash}")
            
#             # Check password
#             is_correct = check_password_hash(user.password_hash, password)
#             print(f"Password Match Result: {is_correct}")
            
#             if is_correct:
#                 print("--- LOGIN SUCCESS ---")
#                 login_user(user)
#                 return redirect(url_for('dashboard'))
#             else:
#                 print("--- PASSWORD MISMATCH ---")
#                 flash("Password does not match", 'fail')
#         else:
#             print("--- USER NOT FOUND ---")
#             flash("User not found", 'fail')

#         return redirect(url_for('login'))

#     return render_template('login.html')
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


if __name__=="__main__":
    app.run(debug=True)
