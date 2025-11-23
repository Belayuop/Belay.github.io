from flask import Flask, request, redirect, url_for, flash, render_template_string, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from flask_mail import Mail, Message
import os, random

# ===== CONFIG =====
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///online_learning.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
if not os.path.exists('uploads'):
    os.makedirs('uploads')

# Email config (use your Gmail)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'youremail@gmail.com'
app.config['MAIL_PASSWORD'] = 'yourpassword'

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
    role = db.Column(db.String(10))
    verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(6))

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    description = db.Column(db.Text)
    files = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

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
        # Send email
        msg = Message('Verify Email', sender=app.config['MAIL_USERNAME'], recipients=[email])
        msg.body = f"Your verification code: {code}"
        mail.send(msg)
        flash('Registered! Check email for code')
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
    return render_template_string("""
    <h2>Welcome {{user.name}} ({{user.role}})</h2>
    {% if user.role=='admin' %}
        <a href="/upload">Upload Course</a><br>
    {% endif %}
    <a href="/courses">View Courses</a><br>
    <a href="/logout">Logout</a>
    """, user=current_user)

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
            Files: {{c.files}}
        {% endif %}
    {% endfor %}
    <a href="/dashboard">Back</a>
    """, courses=courses)

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

# Run App
if __name__=='__main__':
    db.create_all()
    app.run(debug=True)
