from flask import Flask, render_template,jsonify, request, redirect, url_for, flash, session
import os
import json
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash,generate_password_hash
from datetime import datetime,UTC
from sqlalchemy import or_
from flask_login import LoginManager,login_user,logout_user,login_required,current_user,UserMixin
from werkzeug.utils import secure_filename

app=Flask(__name__)
app.secret_key="tja"

UPLOAD_FOLDER=os.path.join('static','UPLOADS')
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER,exist_ok=True)

allowed_extensions={'jpg','jpeg','png','gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in allowed_extensions

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
    sex=db.Column(db.String(10),default='Not Specified')
    profile_photo_path=db.Column(db.String(255),nullable=True)
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
    t_b_amount=db.Column(db.Float,nullable=False)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)

class EXPENSE(db.Model):
    __tablename__='EXPENSE'
    Eid=db.Column(db.Integer,primary_key=True)
    Jid=db.Column(db.Integer,db.ForeignKey('JOURNEY.Jid'),nullable=False)
    amount=db.Column(db.DECIMAL(10,2),nullable=False)
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
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    else:
        return render_template('index.html')

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
    total_pending_reminders=0
    total_budget_tracked=0

    journeys_data=[]
    today = datetime.utcnow()

    for journey in user_records:
        budget=BUDGET.query.filter_by(Jid=journey.Jid).first()
        if budget:
            total_budget_tracked+=budget.t_b_amount
        
        destinations=DESTINATION.query.filter_by(Jid=journey.Jid).all()
        for dest in destinations:
            pending_count=REMINDER.query.filter_by(Did=dest.Did,status=0).count()
            total_pending_reminders+=pending_count
        if journey.end_date<today:
            status='completed'
        elif journey.Start_date>today:
            status='upcoming'
        else:
            status='In Progress'
        
        journeys_data.append({
            'Jid': journey.Jid,
            'J_name': journey.J_name,
            'Start_date': journey.Start_date.strftime('%b %d, %Y'),
            'end_date': journey.end_date.strftime('%b %d, %Y'),
            'description': journey.description,
            'status': status
        })
    journeys_json=json.dumps(journeys_data)

    return render_template('dashboard.html',records=user_records,journeys_json=journeys_json,total_reminders=total_pending_reminders,total_budget=total_budget_tracked)

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
    user_records=JOURNEY.query.filter_by(User_ID=current_user.User_ID).all()
    if not target_journey or target_journey.User_ID != current_user.User_ID:
        flash("Access denied or Journey not found.", "error")
        return redirect(url_for('dashboard'))
    saved_destinations=DESTINATION.query.filter_by(Jid=Jid).all()
    
    # Fetch all pending reminders for destinations in this journey
    pending_reminders = []
    for destination in saved_destinations:
        reminders = REMINDER.query.filter_by(Did=destination.Did, status=0).all()
        for reminder in reminders:
            pending_reminders.append({
                'Rid': reminder.Rid,
                'Did': destination.Did,
                'destination_name': destination.place_name,
                'rem_text': reminder.rem_text,
                'status': reminder.status
            })
    budget=BUDGET.query.filter_by(Jid=Jid).first()
    expenses=EXPENSE.query.filter_by(Jid=Jid).order_by(EXPENSE.expense_date.desc()).all()
    total_spent=sum(float(exp.amount) for exp in expenses)
    remaining=(budget.t_b_amount-total_spent)if budget else 0
    
    return render_template('journey.html',JOURNEY=target_journey,DESTINATION=saved_destinations,REMINDERS=pending_reminders,BUDGET=budget,EXPENSES=expenses,TOTAL_SPENT=total_spent,REMAINING= remaining,user_records=user_records)

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
    target_dest = db.session.get(DESTINATION, Did)
    
    if not target_dest:
        flash("Destination not found", "error")
        return redirect(url_for('dashboard'))
        
    target_journey = db.session.get(JOURNEY, target_dest.Jid)
    if not target_journey or target_journey.User_ID != current_user.User_ID:
        flash("Access denied", "error")
        return redirect(url_for('dashboard'))
        
    logs = TRAVEL_LOG.query.filter_by(Did=Did).order_by(TRAVEL_LOG.created_at.desc()).all()
    
    for log in logs:
        if log.photo_path:
            try:
                log.photos = json.loads(log.photo_path) 
            except json.JSONDecodeError:
                # Fallback for old logs
                log.photos = [log.photo_path]
            
            # Normalize paths so both old and new photos work perfectly with Flask's url_for
            clean_photos = []
            for p in log.photos:
                if p.startswith('static/'):
                    clean_photos.append(p.replace('static/', '', 1))
                else:
                    clean_photos.append(p)
            log.photos = clean_photos
        else:
            log.photos = []

    reminders = REMINDER.query.filter_by(Did=Did).all()
    
    return render_template("destination.html", DESTINATION=target_dest, logs=logs, reminders=reminders)

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
        saved_photo_paths=[]
        # 1. Grab the LIST of files sent from the frontend
        files = request.files.getlist('log_photos')
        
        # 2. Loop through them and save each one
        for idx, file in enumerate(files):
            if file and file.filename != '' and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                # Added 'idx' to the filename so multiple files in the same second don't overwrite each other
                date_str = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                new_filename = f"log_dest{Did}_{date_str}_{idx}.{ext}"
                
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
                file.save(save_path)
                
                # Keep track of the saved path
                saved_photo_paths.append(f"UPLOADS/{new_filename}") # Storing relative path for cleaner DB

        # 3. Convert the list of paths into a JSON string
        photo_path_json = json.dumps(saved_photo_paths) if saved_photo_paths else None

        new_log = TRAVEL_LOG(Did=Did, note_text=note, photo_path=photo_path_json)
        db.session.add(new_log)
        db.session.commit()
        return jsonify(success=True, message="Log added successfully")
    except Exception as e:
        db.session.rollback()
        print(f"DATABASE ERROR: {e}")
        return jsonify(success=False,message="An error occurred while adding the log")

@app.route('/add_reminder/<int:Did>',methods=['POST'])
@login_required
def add_reminder(Did):
    target_dest=db.session.get(DESTINATION,Did)
    if not target_dest:
        return jsonify(success=False,message="Destination not found")
    target_journey=db.session.get(JOURNEY,target_dest.Jid)
    if not target_journey or target_journey.User_ID!=current_user.User_ID:
        return jsonify(success=False,message="Access denied")
    rem_text=request.form.get('rem_text')
    status=request.form.get('status')
    new_reminder=REMINDER(Did=Did,rem_text=rem_text,status=0)
    db.session.add(new_reminder)
    db.session.commit()
    return jsonify(success=True,message="Reminder added successfully")
    
@app.route('/toggle_reminder/<int:Rid>', methods=['POST'])
@login_required
def toggle_reminder(Rid):
    try:
        rem_toggle = db.session.get(REMINDER, Rid)
        
        if not rem_toggle:
            return jsonify(success=False, message="Reminder not found"), 404

        # THE FLIP (Boolean)
        if rem_toggle.status == 0:
            rem_toggle.status = 1
        else:
            rem_toggle.status = 0
        
        db.session.commit()
        return jsonify(success=True, new_status=rem_toggle.status)

    except Exception as e:
        db.session.rollback()
        print(f"ERROR: {e}")
        return jsonify(success=False), 500

@app.route('/get_journey_reminders/<int:Jid>')
@login_required
def get_journey_reminders(Jid):
    target_journey=db.session.get(JOURNEY,Jid)
    if not target_journey or target_journey.User_ID != current_user.User_ID:
        return jsonify(success=False, message="Access denied"), 403
    
    saved_destinations=DESTINATION.query.filter_by(Jid=Jid).all()
    
    # Fetch all pending reminders for destinations in this journey
    pending_reminders = []
    for destination in saved_destinations:
        reminders = REMINDER.query.filter_by(Did=destination.Did, status=0).all()
        for reminder in reminders:
            pending_reminders.append({
                'Rid': reminder.Rid,
                'Did': destination.Did,
                'destination_name': destination.place_name,
                'rem_text': reminder.rem_text,
                'status': reminder.status
            })
    
    return jsonify(success=True, reminders=pending_reminders)

# --- DELETE TRAVEL LOG ---
@app.route('/delete_log/<int:Lid>', methods=['POST'])
@login_required
def delete_log(Lid):
    target_log = db.session.get(TRAVEL_LOG, Lid)
    if not target_log:
        return jsonify(success=False, message="Log not found"), 404
        
    # Climb the tree: Log -> Destination -> Journey
    target_dest = db.session.get(DESTINATION, target_log.Did)
    target_journey = db.session.get(JOURNEY, target_dest.Jid)
    
    # Gatekeeper check
    if not target_journey or target_journey.User_ID != current_user.User_ID:
        return jsonify(success=False, message="Access denied"), 403
        
    try:
        if target_log.photo_path:
            file_path=os.path.join(app.root_path,target_log.photo_path)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as file_error:
                    print(f"Could not delete physical file: {file_error}")


        db.session.delete(target_log)
        db.session.commit()
        return jsonify(success=True, message="Log and photo deleted successfully")
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, message="Database error"), 500

# --- DELETE REMINDER ---
@app.route('/delete_reminder/<int:Rid>', methods=['POST'])
@login_required
def delete_reminder(Rid):
    target_rem = db.session.get(REMINDER, Rid)
    if not target_rem:
        return jsonify(success=False, message="Reminder not found"), 404
        
    # Climb the tree: Reminder -> Destination -> Journey
    target_dest = db.session.get(DESTINATION, target_rem.Did)
    target_journey = db.session.get(JOURNEY, target_dest.Jid)
    
    if not target_journey or target_journey.User_ID != current_user.User_ID:
        return jsonify(success=False, message="Access denied"), 403
        
    try:
        db.session.delete(target_rem)
        db.session.commit()
        return jsonify(success=True, message="Reminder deleted successfully")
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, message="Database error"), 500
    
# --- SET BUDGET ---
@app.route('/add_budget/<int:Jid>', methods=['POST'])
@login_required
def add_budget(Jid):
    target_journey = db.session.get(JOURNEY, Jid)
    if not target_journey or target_journey.User_ID != current_user.User_ID:
        return jsonify(success=False, message="Access denied"), 403

    # Rule: Only ONE budget per journey
    existing_budget = BUDGET.query.filter_by(Jid=Jid).first()
    if existing_budget:
        return jsonify(success=False, message="Budget already exists!"), 400

    amount = request.form.get('amount', type=float)
    if not amount or amount <= 0:
        return jsonify(success=False, message="Amount must be greater than 0"), 400

    try:
        new_budget = BUDGET(Jid=Jid, t_b_amount=amount)
        db.session.add(new_budget)
        db.session.commit()
        return jsonify(success=True, message="Budget set successfully")
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, message="Database error"), 500

# --- ADD EXPENSE ---
@app.route('/add_expense/<int:Jid>', methods=['POST'])
@login_required
def add_expense(Jid):
    target_journey = db.session.get(JOURNEY, Jid)
    if not target_journey or target_journey.User_ID != current_user.User_ID:
        return jsonify(success=False, message="Access denied"), 403

    # Ensure a budget exists first
    budget = BUDGET.query.filter_by(Jid=Jid).first()
    if not budget:
        return jsonify(success=False, message="Please set a budget first!"), 400

    amount = request.form.get('amount', type=float)
    if not amount or amount <= 0:
        return jsonify(success=False, message="Amount must be greater than 0"), 400

    description = request.form.get('description')
    expense_date_str = request.form.get('expense_date')
    
    # If the user didn't pick a date, default to right now
    expense_date = datetime.strptime(expense_date_str, '%Y-%m-%d') if expense_date_str else datetime.utcnow()

    try:
        new_expense = EXPENSE(Jid=Jid, amount=amount, description=description, expense_date=expense_date)
        db.session.add(new_expense)
        db.session.commit()
        return jsonify(success=True, message="Expense added successfully")
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, message="Database error"), 500

# --- DELETE EXPENSE ---
@app.route('/delete_expense/<int:Eid>', methods=['POST'])
@login_required
def delete_expense(Eid):
    target_expense = db.session.get(EXPENSE, Eid)
    if not target_expense:
        return jsonify(success=False, message="Expense not found"), 404

    # Verify Journey Ownership directly from the expense
    target_journey = db.session.get(JOURNEY, target_expense.Jid)
    if not target_journey or target_journey.User_ID != current_user.User_ID:
        return jsonify(success=False, message="Access denied"), 403

    try:
        db.session.delete(target_expense)
        db.session.commit()
        return jsonify(success=True)
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, message="Database error"), 500

# --- PROFILE PAGE ---
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

# --- UPLOAD PROFILE PHOTO ---
@app.route('/upload_profile_photo', methods=['POST'])
@login_required
def upload_profile_photo():
    try:
        if 'profile_photo' not in request.files:
            return jsonify(success=False, error='No file provided')
        
        file = request.files['profile_photo']
        
        if file.filename == '':
            return jsonify(success=False, error='No file selected')
        
        if not allowed_file(file.filename):
            return jsonify(success=False, error='Invalid file type. Allowed: JPG, PNG, GIF')
        
        # Delete old profile photo if exists
        if current_user.profile_photo_path:
            old_path = os.path.join(app.root_path, current_user.profile_photo_path)
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except:
                    pass
        
        # Generate new filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        date_str = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        new_filename = f"{current_user.User_ID}_{date_str}.{ext}"
        
        # Save file
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        file.save(save_path)
        
        # Update database
        photo_path = f"static/UPLOADS/{new_filename}"
        current_user.profile_photo_path = photo_path
        db.session.commit()
        
        return jsonify(success=True, photo_path=photo_path)
    
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, error=str(e)), 500

# --- UPDATE PROFILE ---
@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    try:
        data = request.get_json()
        
        # Update name
        if 'name' in data and data['name'].strip():
            current_user.Name = data['name'].strip()
        
        # Update age
        if 'age' in data and data['age']:
            age = int(data['age'])
            if 1 <= age <= 120:
                current_user.age = age
            else:
                return jsonify(success=False, error='Invalid age. Must be between 1 and 120')
        else:
            current_user.age = None
        
        # Update sex
        if 'sex' in data:
            valid_sex_values = ['Not Specified', 'Male', 'Female', 'Other']
            if data['sex'] in valid_sex_values:
                current_user.sex = data['sex']
            else:
                current_user.sex = 'Not Specified'
        
        db.session.commit()
        return jsonify(success=True, message='Profile updated successfully')
    
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, error=str(e)), 500
    

@app.route('/edit_budget/<int:Jid>',methods=['POST'])
@login_required
def edit_budget(Jid):
    target_journey=db.session.get(JOURNEY,Jid)
    if not target_journey or target_journey.User_ID != current_user.User_ID:
        return jsonify(success=False,message="Access denied"),403
    
    existing_budget=BUDGET.query.filter_by(Jid=Jid).first()
    if not existing_budget:
        return jsonify(success=False,message="Budget does not exist!"),400
    amount=request.form.get('amount',type=float)
    if not amount or amount<=0:
        return jsonify(success=False,message="Amount must be greater than 0"),400
    try:
        existing_budget.t_b_amount=amount
        db.session.commit()
        return jsonify(success=True,message="Budget updated successfully")
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False,message="Database error"),500


    
    
    
if __name__=="__main__":
    app.run(debug=True)
