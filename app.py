from flask import Flask, request, redirect, url_for, flash, render_template, session, send_from_directory, jsonify
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
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

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

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500))
    options = db.Column(db.Text)  # comma-separated options
    answer = db.Column(db.String(200))

class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    score = db.Column(db.Integer)
    taken_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# ===== LOGIN =====
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ===== ROUTES =====

@app.route('/')
def index():
    return render_template("index.html")  # Use templates folder instead of inline HTML

# ===== AI Chatbot Endpoint =====
@app.route('/chatbot', methods=['POST'])
@login_required
def chatbot():
    user_msg = request.json.get("message")
    # Replace with your AI logic; here simple echo:
    bot_reply = f"BelayBot says: You typed '{user_msg}'"
    return jsonify({"response": bot_reply})

# ===== Quiz Routes =====
@app.route('/quizzes')
@login_required
def quizzes():
    all_quizzes = Quiz.query.all()
    return render_template("quizzes.html", quizzes=all_quizzes)

@app.route('/submit-quiz', methods=['POST'])
@login_required
def submit_quiz():
    score = 0
    for key, value in request.form.items():
        quiz = Quiz.query.get(int(key))
        if quiz.answer.strip().lower() == value.strip().lower():
            score += 1
    result = QuizResult(student_id=current_user.id, score=score)
    db.session.add(result)
    db.session.commit()
    flash(f"You scored {score} out of {Quiz.query.count()}")
    return redirect(url_for('quizzes'))

# ===== Courses, Upload, Assignment =====
@app.route('/courses')
@login_required
def courses():
    courses = Course.query.all()
    return render_template("courses.html", courses=courses, user=current_user)

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
            safe_name = f"{datetime.datetime.utcnow().timestamp()}_{f.filename}"
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], safe_name))
            filenames.append(safe_name)
        course = Course(title=title, description=description, files=','.join(filenames), created_by=current_user.id)
        db.session.add(course)
        db.session.commit()
        flash('Course uploaded successfully!')
    return render_template("upload_course.html")

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
        flash('Assignment submitted!')
        return redirect(url_for('my_assignments'))
    return render_template("submit_assignment.html", course=course)

@app.route('/my-assignments')
@login_required
def my_assignments():
    assignments = Assignment.query.filter_by(student_id=current_user.id).all()
    return render_template("my_assignments.html", assignments=assignments)

# ===== File Downloads =====
@app.route('/uploads/<filename>')
@login_required
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# ===== Email Verification, Register, Login, Logout =====
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
        flash('Registered! Check your email for verification code.')
        return redirect(url_for('verify'))
    return render_template("register.html")

@app.route('/verify', methods=['GET','POST'])
def verify():
    if request.method=='POST':
        email = request.form['email']
        code = request.form['code']
        user = User.query.filter_by(email=email).first()
        if user and user.verification_code==code:
            user.verified = True
            db.session.commit()
            flash('Verified! You can login now.')
            return redirect(url_for('login'))
        flash('Invalid code!')
    return render_template("verify.html")

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('User not found!')
        elif not user.verified:
            flash('Verify your email first!')
        elif check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Wrong password!')
    return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ===== Dashboard =====
@app.route('/dashboard')
@login_required
def dashboard():
    courses = Course.query.all()
    return render_template("dashboard.html", user=current_user, courses=courses)

# ===== RUN =====
if __name__=='__main__':
    db.create_all()
    app.run(debug=True)


