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
class JOURNEY(db.Model):
    __tablename__='JOURNEY'
    Jid=db.Column(db.Integer,primary_key=True)
    J_name=db.Column(db.String(50),nullable=False)
    Start_date=db.Column(db.DateTime,nullable=False)
    end_date=db.Column(db.DateTime,nullable=False)
    description=db.Column(db.Text,nullable=True)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)
    User_ID=db.Column(db.Integer,db.ForeignKey('USER.User_ID'),nullable=False)

class DESTINATION(db.Model):
    __tablename__='DESTINATION'
    Did=db.Column(db.Integer,primary_key=True)
    Jid=db.Column(db.Integer,db.ForeignKey('fk_journey_desti'))
    place_name=db.Column(db.String(50),nullable=False)
    visit_order=db.Column(db.Integer,nullable=False,unique=True)
    visit_status=db.Column(db.String(10),nullable=False)
    is_main=db.Column(db.Boolean,default=False)
    map=db.Column(db.String(255),nullable=True)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)



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
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_records=JOURNEY.query.filter_by(User_ID=current_user.User_ID).all()
    return render_template('dashboard.html',records=user_records)

@app.route('/create_journey',methods=['GET','POST'])
@login_required
def create_journey():
    if request.method=='POST':
        J_name=request.form.get('J_name')
        start_date_str=request.form.get('start_date')
        end_date_str=request.form.get('end_date')
        description=request.form.get('description')
        
        # Convert date strings to datetime objects
        start_date=datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date=datetime.strptime(end_date_str, '%Y-%m-%d')
        
        new_journey=JOURNEY(J_name=J_name,Start_date=start_date,end_date=end_date,description=description,User_ID=current_user.User_ID)
        db.session.add(new_journey)
        db.session.commit()
        return jsonify(success=True, message="Journey created successfully")
    else:
        return render_template('c_journey.html')


if __name__=="__main__":
    app.run(debug=True)
