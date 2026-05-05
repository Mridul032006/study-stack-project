from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from collections import Counter
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback-key")

# ✅ DATABASE FIXED PATH
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static/uploads')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# ================= LOGIN =================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# ================= MODELS =================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))  # hashed password


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    subject = db.Column(db.String(100))
    filename = db.Column(db.String(200))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ================= ROUTES =================

@app.route('/')
def home():
    return redirect('/browse')


# REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash("All fields are required")
            return redirect('/register')

        if User.query.filter_by(username=username).first():
            flash("User already exists")
            return redirect('/register')

        hashed_password = generate_password_hash(password)

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please login.")
        return redirect('/login')

    return render_template('register.html')


# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash("All fields are required")
            return redirect('/login')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password")

    return render_template('login.html')


# LOGOUT
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


# DASHBOARD
@app.route('/dashboard')
@login_required
def dashboard():
    notes = Note.query.filter_by(user_id=current_user.id)\
        .order_by(Note.created_at.desc()).limit(5).all()

    all_notes = Note.query.filter_by(user_id=current_user.id).all()

    dates = [
        note.created_at.strftime("%d %b")
        for note in all_notes if note.created_at
    ]

    date_count = Counter(dates)

    labels = list(date_count.keys())
    values = list(date_count.values())

    return render_template(
        'dashboard.html',
        notes=notes,
        labels=labels,
        values=values
    )


# BROWSE
@app.route('/browse')
@login_required
def browse():
    notes = Note.query.all()
    return render_template('browse.html', notes=notes)


# UPLOAD
@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        title = request.form['title']
        description = request.form['description']
        subject = request.form['subject']
        file = request.files['file']

        if not title or not subject:
            flash("Title and subject are required")
            return redirect('/upload')

        if file:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            new_note = Note(
                title=title,
                description=description,
                subject=subject,
                filename=filename,
                user_id=current_user.id
            )

            db.session.add(new_note)
            db.session.commit()

            return redirect(url_for('dashboard'))

    return render_template("upload.html")


# MY NOTES
@app.route('/mynotes')
@login_required
def mynotes():
    notes = Note.query.filter_by(user_id=current_user.id).all()
    return render_template('my_notes.html', notes=notes)


# DELETE
@app.route('/delete/<int:id>')
@login_required
def delete(id):
    note = Note.query.get(id)

    if note and note.user_id == current_user.id:
        db.session.delete(note)
        db.session.commit()

    return redirect('/mynotes')


# SUBJECT NOTES
@app.route("/subject/<subject_name>")
@login_required
def subject_notes(subject_name):
    notes = Note.query.filter_by(subject=subject_name).all()
    return render_template("subject_notes.html", notes=notes, subject=subject_name)


# OPEN FILE
@app.route('/open/<filename>')
@login_required
def open_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# DOWNLOAD FILE
@app.route('/download/<filename>')
@login_required
def download_file(filename):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename,
        as_attachment=True
    )


# ================= RUN =================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)