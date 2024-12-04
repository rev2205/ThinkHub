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
    projects = db.relationship('Project',backref='student',lazy=True)

    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

    def __repr__(self):
        return f'<Student {self.full_name}>'
# search the email in the database first, if it already exists the alert the user that the email already exists else commit 
class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    dept = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(50), nullable=False)
    domain_of_exp = db.Column(db.String(50), nullable=False)
    projects = db.relationship('Project',backref='teacher',lazy=True)

    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self,password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Teacher {self.full_name}>'
class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer,primary_key=True)
    project_name = db.Column(db.String(100), nullable=False)
    project_description = db.Column(db.Text, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'),nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'),nullable=True)

    def __repr__(self):
        return f'<Project {self.project_name}>'
    

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

        if Student.query.filter_by(email=email).first():
            flash("Email already exists. Please login or use a different email.","error")
            return redirect(url_for('register_student'))
        
        if Student.query.filter_by(reg_no=registration_number).first():
            flash("Regestration number already exists!!","error")
            return redirect(url_for('register_student'))

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

        flash("Registration successfull. Please login.","success")
        return redirect(url_for('login'))
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

        if Teacher.query.filter_by(email=email).first():
            flash("Email alrady exists. Pleaase use a different email or try login.","error")
            return redirect(url_for('register_teacher'))

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
        flash("Registration succesfull. Please login.","success")
        return redirect(url_for('login'))

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
            if role == 'student':
                return redirect(url_for('student_dashboard'))
            else:
                return redirect(url_for('teacher_dashboard'))
        else:
            flash('Invalid email or password or role','error')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/student_dashborad', methods=['GET','POST'])
def student_dashboard():
    if 'user_id' in session and session.get('role') == 'student':
        student = Student.query.get(session['user_id'])
        if request.method == 'POST':
            project_name = request.form['project_name']
            project_description = request.form['project_description']
            new_project = Project(project_name=project_name,project_description=project_description,student=student)
            db.session.add(new_project)
            db.session.commit()
            flash("project added succesfully","success")
        projects = Project.query.filter_by(student_id = student.id).all()
        return render_template('student_dashboard.html',student=student, projects=projects)
    flash("Please login first!","error")
    return redirect(url_for('login'))

@app.route('/teacher_dashboard', methods=['GET','POST'])
def teacher_dashboard():
    if 'user_id' in session and session.get('role') == 'teacher':
        teacher = Teacher.query.get(session['user_id'])
        if request.method == 'POST':
            project_name = request.form['project_name']
            project_description = request.form['project_description']
            new_project = Project(project_name=project_name, project_description=project_description,teacher=teacher)
            db.session.add(new_project)
            db.session.commit()
            flash("project added succesfully!","success")
        projects = Project.query.filter_by(teacher_id=teacher.id).all()
        return render_template('teacher_dashboard.html',teacher=teacher, projects=projects)
    
    flash("pleade try login","error")
    return redirect(url_for('login'))

@app.route('/find', methods=['GET','POST'])
def find():
    
    if request.method == "POST":
        domain = request.form['domain']
        role = request.form['role']

        results = []
        if role == "Student":
            students = Student.query.filter_by(interested_domain=domain).all()
            for student in students:
                projects = Project.query.filter_by(student_id=student.id).all()
                results.append({
                    'name' : student.full_name,
                    'branch' : student.branch,
                    'email' : student.email,
                    'projects' : [{'name' : project.project_name,'desc':project.project_description} for project in projects]
                })
        elif role == "Teacher":
            teachers = Teacher.query.filter_by(domain_of_exp=domain).all()
            for teacher in teachers:
                projects = Project.query.filter_by(teacher_id = teacher.id).all()
                results.append({
                    'name' : teacher.full_name,
                    'branch' : teacher.dept,
                    'email' : teacher.email,
                    'projects' : [{'name' : project.project_name, 'desc' : project.project_description} for project in projects]
                })
        return render_template('find.html',results=results,domain=domain, role=role)
    return render_template('find.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!!","success")
    return redirect(url_for('login'))

# Only create tables if the database file doesn't exist
if not os.path.exists('thinkhub.db'):
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
