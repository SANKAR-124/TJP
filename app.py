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
    Jid=db.Column(db.Integer,db.ForeignKey('JOURNEY.Jid'),nullable=False)
    place_name=db.Column(db.String(50),nullable=False)
    visit_order=db.Column(db.Integer,nullable=False,unique=True)
    visit_status=db.Column(db.String(10),nullable=False)
    is_main=db.Column(db.Boolean,default=False)
    map=db.Column(db.String(255),nullable=True)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)

class TRAVEL_LOG(db.Model):
    __tablename__='TRAVEL_LOG'
    Lid=db.Column(db.Integer,primary_key=True)
    Did=db.Column(db.Integer,db.ForeignKey('DESTINATION.Did'),nullable=False)
    note_text=db.Column(db.Text,nullable=True)
    photo_path=db.Column(db.String(255),nullable=True)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)

class REMINDER(db.Model):
    __tablename__='REMINDER'
    Rid=db.Column(db.Integer,primary_key=True)
    Did=db.Column(db.Integer,db.ForeignKey('DESTINATION.Did'),nullable=False)
    rem_text=db.Column(db.String(255),nullable=True)
    status=db.Column(db.SmallInteger,default=0)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)

class BUDGET(db.Model):
    __tablename__='BUDGET'
    Bid=db.Column(db.Integer,primary_key=True)
    Jid=db.Column(db.Integer,db.ForeignKey('JOURNEY.Jid'),nullable=False)
    t_b_amount=db.Column(db.Float)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)

class EXPENSE(db.Model):
    __tablename__='EXPENSE'
    Eid=db.Column(db.Integer,primary_key=True)
    Jid=db.Column(db.Integer,db.ForeignKey('JOURNEY.Jid'),nullable=False)
    amount=db.Column(db.Decimal,nullable=False)
    description=db.Column(db.Text,nullable=True)
    expense_date=db.Column(db.DateTime,nullable=False)
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

@app.route('/journey/<int:Jid>')
@login_required
def view_journey(Jid):
    target_journey=db.session.get(JOURNEY,Jid)
    if not target_journey or target_journey.User_ID != current_user.User_ID:
        flash("Access denied or Journey not found.", "error")
        return redirect(url_for('dashboard'))
    saved_destinations=DESTINATION.query.filter_by(Jid=Jid).all()
    return render_template('journey.html',JOURNEY=target_journey,DESTINATION=saved_destinations)

@app.route('/add_destination/<int:Jid>',methods=['POST'])
@login_required
def add_destination(Jid):
    try:
        place_name=request.form.get('place_name')
        visit_order=int(request.form.get('visit_order'))
        visit_status=request.form.get('visit_status')
        is_main=(request.form.get('is_main')=='1')
        if is_main is True:
            old_main=DESTINATION.query.filter_by(Jid=Jid,is_main=True).first()
            if old_main:
                old_main.is_main=False
        new_destination=DESTINATION(Jid=Jid,place_name=place_name,visit_order=visit_order,visit_status=visit_status,is_main=is_main)
        db.session.add(new_destination)
        db.session.commit()
        return jsonify(success=True, message="Destination added successfully")
    except Exception as e:
        db.session.rollback()
        print(f"DATABASE ERROR: {e}")
        return jsonify(success=False, message="An error occurred while adding the destination")
@app.route('/edit_journey/<int:Jid>',methods=['POST'])
@login_required
def edit_journey(Jid):
    target_journey=db.session.get(JOURNEY,Jid)
    if not target_journey:
        return jsonify(success=False,message="Journey not found")
    target_journey=db.session.get(JOURNEY,target_journey.Jid)
    if not target_journey or target_journey.User_ID != current_user.User_ID:
        return jsonify(success=False, message="Access denied")
    try:
        target_journey.J_name=request.form.get('J_name')
        target_journey.start_date_str=request.form.get('start_date')
        target_journey.end_date_str=request.form.get('end_date')
        target_journey.description=request.form.get('description')
        
        # Convert date strings to datetime objects
        target_journey.start_date=datetime.strptime(target_journey.start_date_str, '%Y-%m-%d')
        target_journey.end_date=datetime.strptime(target_journey.end_date_str, '%Y-%m-%d')
        db.session.commit()
        return jsonify(success=True,message="Journey edited successfully")
    except Exception as e:
        db.session.rollback()
        print(f"DATABASE ERROR {e}")
        return jsonify(success=False,message="An error occurred while updating the journey")
    


@app.route('/edit_destination/<int:Did>',methods=['POST'])
@login_required
def edit_destination(Did):
    target_dest=db.session.get(DESTINATION,Did)
    if not target_dest:
        return jsonify(success=False, message="Destination not found")
    
    # Check if the destination's journey belongs to the current user
    target_journey=db.session.get(JOURNEY,target_dest.Jid)
    if not target_journey or target_journey.User_ID != current_user.User_ID:
        return jsonify(success=False, message="Access denied")
    
    try:
        target_dest.place_name=request.form.get('place_name')
        target_dest.visit_order=int(request.form.get('visit_order'))
        target_dest.visit_status=request.form.get('visit_status')
        target_dest.is_main=(request.form.get('is_main')=='1')
        target_dest.map=request.form.get('map')
        
        if target_dest.is_main is True:
            old_main=DESTINATION.query.filter_by(Jid=target_dest.Jid,is_main=True).first()
            if old_main and old_main.Did != Did:
                old_main.is_main=False
        
        db.session.commit()
        return jsonify(success=True, message="Destination edited successfully")
    except Exception as e:
        db.session.rollback()
        print(f"DATABASE ERROR {e}")
        return jsonify(success=False, message="An error occurred while updating the destination")

@app.route('/delete_destination/<int:Did>',methods=['POST'])
@login_required
def delete_destination(Did):
    target=db.session.get(DESTINATION,Did)
    db.session.delete(target)
    db.session.commit()
    return jsonify(success=True,message="Destination deleted successfully")
@app.route('/delete_journey/<int:Jid>',methods=['POST'])
@login_required
def delete_journey(Jid):
    target_journey=db.session.get(JOURNEY,Jid)
    db.session.delete(target_journey)
    db.session.commit()
    return jsonify(success=True,message="Journey deleted successfully")
@app.route('/toggle_status/<int:Did>',methods=['POST'])
@login_required
def toggle_status(Did):
    target_toggle=db.session.get(DESTINATION,Did)
    # target_toggle.visit_status=request.form.get('visit_status')
    target_toggle.visit_status='visited' if target_toggle.visit_status=='planned' else 'planned'
    db.session.commit()
    return jsonify(success=True,new_status=target_toggle.visit_status)

@app.route('/destination/<int:Did>')
@login_required
def view_destination(Did):
    target_dest=db.session.get(DESTINATION,Did)
    target_journey=db.session.get(JOURNEY,target_dest.Jid)
    if not target_journey or target_journey.User_ID != current_user.User_ID:
        flash("Access denied", "error")
        return redirect(url_for('dashboard'))
    logs=TRAVEL_LOG.query.filter_by(Did=Did).all()
    return render_template("destination.html",destination=target_dest,logs=logs)

@app.route('/travel_log/<int:Did>',methods=['GET','POST'])
@login_required
def travel_log(Did):
    target_dest=db.session.get(DESTINATION,Did)
    if not target_dest:
        return jsonify(success=False,message="Destination not found")

    target_journey=db.session.get(JOURNEY,target_dest.Jid)
    if not target_journey or target_journey.User_ID!=current_user.User_ID:
        return jsonify(success=False,message="Access denied")

    try:
        note=request.form.get('note')
        photo_path=request.form.get('photo_path')
        new_log=TRAVEL_LOG(Did=Did,note_text=note,photo_path=photo_path)
        db.session.add(new_log)
        db.session.commit()
        return jsonify(success=True,message="Log added successfully")
    except Exception as e:
        db.session.rollback()
        print(f"DATABASE ERROR: {e}")
        return jsonify(success=False,message="An error occurred while adding the log")

if __name__=="__main__":
    app.run(debug=True)
