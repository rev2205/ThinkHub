import os
from flask import Flask, url_for, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configure the SQLite database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///thinkhub.db'
app.config['SECRET_KEY'] = 'myproject'
db = SQLAlchemy(app)

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    branch = db.Column(db.String(40), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    reg_no = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)  # New password field
    interested_domain = db.Column(db.String(200), nullable=True)  # New interested domain field
    phone = db.Column(db.String(15), nullable=False)
    cgpa = db.Column(db.Float, nullable=False)

    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

    def __repr__(self):
        return f'<Student {self.full_name}>'

class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    dept = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(50), nullable=False)
    domain_of_exp = db.Column(db.String(50), nullable=False)

    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self,password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Teacher {self.full_name}>'

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/register_student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        full_name = request.form['full_name']
        branch = request.form['branch']
        sem = request.form['semester']
        registration_number = request.form['reg_num']
        email = request.form['email']
        password = request.form['password']  # Capture password
        interested_domain = request.form['interested_domain']  # Capture interested domain
        phone = request.form['phone']
        cgpa = request.form['cgpa']

        new_student = Student(
            full_name=full_name,
            branch=branch,
            semester=sem,
            reg_no=registration_number,
            email=email,
            interested_domain=interested_domain,
            phone=phone,
            cgpa=cgpa
        )
        new_student.set_password(password)

        db.session.add(new_student)
        db.session.commit()

        flash('Student registered successfully!!!','Success')

        return redirect(url_for('index'))
    return render_template('student_login.html')

@app.route('/register_teacher', methods=['GET', 'POST'])
def register_teacher():
    if request.method == 'POST':
        name = request.form['full_name']
        dept = request.form['dept']
        teach_id = request.form['teacher_id']
        email = request.form['mail']
        password = request.form['password']
        domain_of_exp = request.form['domain_of_expertise']

        new_teacher = Teacher(
            full_name=name,
            dept=dept,
            teacher_id=teach_id,
            email=email,
            domain_of_exp=domain_of_exp
        )
        new_teacher.set_password(password)

        db.session.add(new_teacher)
        db.session.commit()

        flash('Teacher registered succesfully','Success')

        return redirect(url_for('index'))
    return render_template('teacher_login.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        if role == 'student':
            user = Student.query.filter_by(email=email).first()
        elif role == 'teacher':
            user = Teacher.query.filter_by(email=email).first()
        else:
            flash("Invalid role selected!",'error')
            return redirect(url_for('login'))

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['role'] = role
            flash("Login successfull!",'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password','error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return f"Welcome to the dashboard, {session['role']} user!!"
    else:
        flash("Please login in first",'error')
        return redirect(url_for('login'))

# Only create tables if the database file doesn't exist
if not os.path.exists('thinkhub.db'):
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
