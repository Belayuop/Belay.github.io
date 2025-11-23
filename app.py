from flask import Flask, request, redirect, url_for, flash, render_template_string, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from flask_mail import Mail, Message
import os, random, datetime

# ===== CONFIG =====
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///online_learning.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
if not os.path.exists('uploads'):
    os.makedirs('uploads')

# Email config (Gmail example)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'youremail@gmail.com'  # replace
app.config['MAIL_PASSWORD'] = 'yourpassword'         # replace

# ===== INIT =====
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
mail = Mail(app)

# ===== MODELS =====
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(10))  # 'admin' or 'student'
    verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(6))
    assignments = db.relationship('Assignment', backref='student', lazy=True)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    description = db.Column(db.Text)
    files = db.Column(db.Text)  # comma-separated filenames
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    assignments = db.relationship('Assignment', backref='course', lazy=True)

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    filename = db.Column(db.String(200))
    submitted_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# ===== LOGIN =====
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ===== ROUTES =====

# Home
@app.route('/')
def index():
    return render_template_string("""
    <h1>Welcome to Online Learning Platform</h1>
    <a href="/register">Register</a> | <a href="/login">Login</a>
    """)

# Register
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']
        code = str(random.randint(100000,999999))
        user = User(name=name,email=email,password=password,role=role,verification_code=code)
        db.session.add(user)
        db.session.commit()
        # Send verification email
        msg = Message('Verify Email', sender=app.config['MAIL_USERNAME'], recipients=[email])
        msg.body = f"Your verification code: {code}"
        mail.send(msg)
        flash('Registered! Check email for code.')
        return redirect('/verify')
    return render_template_string("""
    <h2>Register</h2>
    <form method="POST">
    <input name="name" placeholder="Full Name" required><br>
    <input name="email" placeholder="Email" required><br>
    <input type="password" name="password" placeholder="Password" required><br>
    <select name="role">
        <option value="student">Student</option>
        <option value="admin">Admin</option>
    </select><br>
    <button type="submit">Register</button>
    </form>
    """)

# Verify Email
@app.route('/verify', methods=['GET','POST'])
def verify():
    if request.method=='POST':
        email = request.form['email']
        code = request.form['code']
        user = User.query.filter_by(email=email).first()
        if user and user.verification_code==code:
            user.verified = True
            db.session.commit()
            flash('Verified! You can login.')
            return redirect('/login')
        flash('Invalid code')
    return render_template_string("""
    <h2>Verify Email</h2>
    <form method="POST">
    <input name="email" placeholder="Email" required><br>
    <input name="code" placeholder="6-digit Code" required><br>
    <button type="submit">Verify</button>
    </form>
    """)

# Login
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('User not found')
        elif not user.verified:
            flash('Verify email first')
        elif check_password_hash(user.password, password):
            login_user(user)
            return redirect('/dashboard')
        else:
            flash('Wrong password')
    return render_template_string("""
    <h2>Login</h2>
    <form method="POST">
    <input name="email" placeholder="Email" required><br>
    <input type="password" name="password" placeholder="Password" required><br>
    <button type="submit">Login</button>
    </form>
    """)

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

# Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    courses = Course.query.all()
    return render_template_string("""
    <h2>Welcome {{user.name}} ({{user.role}})</h2>
    {% if user.role=='admin' %}
        <a href="/upload">Upload Course</a><br>
    {% endif %}
    <a href="/courses">View Courses</a><br>
    {% if user.role=='student' %}
        <a href="/my-assignments">My Assignments</a><br>
    {% endif %}
    <a href="/logout">Logout</a>
    """, user=current_user, courses=courses)

# View Courses
@app.route('/courses')
@login_required
def courses():
    courses = Course.query.all()
    return render_template_string("""
    <h2>Courses</h2>
    {% for c in courses %}
        <h3>{{c.title}}</h3>
        <p>{{c.description}}</p>
        {% if c.files %}
            Files:
            {% for f in c.files.split(',') %}
                <a href="{{url_for('download_file', filename=f)}}">{{f}}</a><br>
            {% endfor %}
        {% endif %}
        {% if user.role=='student' %}
            <a href="/submit-assignment/{{c.id}}">Submit Assignment</a>
        {% endif %}
    {% endfor %}
    <a href="/dashboard">Back</a>
    """, courses=courses, user=current_user)

# Download file
@app.route('/uploads/<filename>')
@login_required
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Upload Course (Admin only)
@app.route('/upload', methods=['GET','POST'])
@login_required
def upload_course():
    if current_user.role != 'admin':
        return "Access Denied"
    if request.method=='POST':
        title = request.form['title']
        description = request.form['description']
        files = request.files.getlist('files')
        filenames = []
        for f in files:
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
            filenames.append(f.filename)
        course = Course(title=title, description=description, files=','.join(filenames), created_by=current_user.id)
        db.session.add(course)
        db.session.commit()
        flash('Course uploaded')
    return render_template_string("""
    <h2>Upload Course</h2>
    <form method="POST" enctype="multipart/form-data">
    <input name="title" placeholder="Course Title" required><br>
    <textarea name="description" placeholder="Course Description"></textarea><br>
    <input type="file" name="files" multiple><br>
    <button type="submit">Upload</button>
    </form>
    <a href="/dashboard">Back</a>
    """)

# Submit Assignment (Student only)
@app.route('/submit-assignment/<int:course_id>', methods=['GET','POST'])
@login_required
def submit_assignment(course_id):
    if current_user.role != 'student':
        return "Access Denied"
    course = Course.query.get_or_404(course_id)
    if request.method=='POST':
        file = request.files['assignment']
        filename = f"{current_user.id}_{course_id}_{file.filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        assignment = Assignment(student_id=current_user.id, course_id=course_id, filename=filename)
        db.session.add(assignment)
        db.session.commit()
        flash('Assignment submitted')
        return redirect('/my-assignments')
    return render_template_string("""
    <h2>Submit Assignment for {{course.title}}</h2>
    <form method="POST" enctype="multipart/form-data">
    <input type="file" name="assignment" required><br>
    <button type="submit">Submit</button>
    </form>
    <a href="/courses">Back</a>
    """, course=course)

# View My Assignments (Student)
@app.route('/my-assignments')
@login_required
def my_assignments():
    if current_user.role != 'student':
        return "Access Denied"
    assignments = Assignment.query.filter_by(student_id=current_user.id).all()
    return render_template_string("""
    <h2>My Assignments</h2>
    {% for a in assignments %}
        <p>{{a.course.title}} - <a href="{{url_for('download_file', filename=a.filename)}}">{{a.filename}}</a> ({{a.submitted_at}})</p>
    {% endfor %}
    <a href="/dashboard">Back</a>
    """, assignments=assignments)

# Run App
if __name__=='__main__':
    db.create_all()
    app.run(debug=True)
