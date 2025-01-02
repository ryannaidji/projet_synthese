import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, redirect, url_for, flash, abort, request, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from decorators import role_required
from models import mock_diagnostics
from models import db, Patient, User
from datetime import datetime

from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///patients.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your_secret_key'  # Replace with a strong secret key

# Initialize Flask-Login
db.init_app(app)  # Initialize db with the app 
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Redirect users to 'login' if not logged in

@app.route('/create-admin')
def create_admin():
    # Check if the admin user already exists
    existing_admin = User.query.filter_by(username='admin').first()
    if existing_admin:
        return "Admin user already exists!"

    # Create an admin user
    hashed_password = generate_password_hash('adminpassword', method='pbkdf2:sha256')  # Make sure to change the password
    admin = User(username='admin', email='admin@example.com', password=hashed_password, role='admin')

    db.session.add(admin)
    db.session.commit()

    return "Admin user created successfully!"

# Drop all tables
#with app.app_context():
#    db.drop_all()

# Recreate the tables
#with app.app_context():
#    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def create_tables():
    db.create_all()

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def landing():
    return render_template('landing.html')

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, current_user
#from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('upload_form'))
        else:
            flash('Invalid credentials', 'danger')

    return render_template('login.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.errorhandler(403)
def forbidden(e):
    return render_template("403.html"), 403

@app.route('/upload_form')
@login_required
@role_required("admin","doctor","nurse")
def upload_form():
    patients = Patient.query.all()
    return render_template('upload.html', patients=patients)

@app.route('/predict', methods=['POST'])
def upload_file():
    if 'username' not in session:
        return redirect(url_for('login'))

    if 'file' not in request.files:
        return render_template('upload.html', error="No file part")

    file = request.files['file']

    if file.filename == '':
        return render_template('upload.html', error="No selected file")

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Placeholder for brain tumor detection logic
        # Replace with model prediction logic
        result = "Tumor detected" if "tumor" in filename.lower() else "No tumor detected"

        return render_template('result.html', image_url=filepath,probability=50, result=result, patient_name="John Doe")

    return render_template('upload.html', error="Invalid file type")

from flask import request, render_template, redirect, url_for, flash
from models import User, db
from werkzeug.security import generate_password_hash

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'nurse')  # Default to 'user' if no role is provided
        confirm_password = request.form['confirm_password']

        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
           return render_template('register.html', error="Username already exists.")

        if password != confirm_password:
            return render_template('register.html', error="Passwords do not match.")

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()

        return render_template('register.html', success="Registration successful! You can now log in.",title_text="User Registration", action_url=url_for('register'), button_text="Register")
    
    return render_template('register.html',action_url=url_for('register'), button_text="Register", title_text="User Registration")

@app.route('/admin/users/add', methods=['GET','POST'])
@login_required
@role_required("admin")
def add_user():
    return render_template('register.html', action_url=url_for('register'), button_text="Add User", title_text="Add New User")


@app.route('/admin/diagnostics', methods=['GET'])
@login_required
@role_required("admin","doctor","nurse")
def diagnostics():
    
    return render_template('diagnostics.html', diagnostics=mock_diagnostics)

@app.route('/admin/patients')
@login_required
@role_required("admin","doctor","nurse")
def admin_patients():
    patients = Patient.query.all()
    return render_template('admin_patients.html', patients=patients)

@app.route("/admin/patients/add", methods=["GET", "POST"])
@login_required
def add_patient():
    if request.method == "POST":
        name = request.form["name"]
        dob = datetime.strptime(request.form["dob"], '%Y-%m-%d').date()
        gender = request.form["gender"]
        address = request.form.get("address")
        phone = request.form.get("phone")

        new_patient = Patient(name=name, dob=dob, gender=gender, address=address, phone=phone)
        db.session.add(new_patient)
        db.session.commit()
        flash("Patient added successfully!")
        return redirect(url_for("admin_patients"))

    return render_template("add_patient.html")

@app.route("/patients/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_patient(id):
    patient = Patient.query.get_or_404(id)

    if request.method == "POST":
        patient.name = request.form["name"]
        patient.dob = datetime.strptime(request.form["dob"], '%Y-%m-%d').date()
        patient.gender = request.form["gender"]
        patient.address = request.form.get("address")
        patient.phone = request.form.get("phone")

        db.session.commit()
        flash("Patient updated successfully!")
        return redirect(url_for("admin_patients"))

    return render_template("add_patient.html", patient=patient, is_edit=True)

@app.route("/patients/delete/<int:id>", methods=["POST"])
@login_required
def delete_patient(id):
    patient = Patient.query.get_or_404(id)
    db.session.delete(patient)
    db.session.commit()
    flash("Patient deleted successfully!")
    return redirect(url_for("admin_patients"))

@app.route("/admin/diagnostics/delete/<int:id>", methods=["POST"])
@login_required
@role_required("admin","doctor")
def delete_diagnostic(id):
    diagnostic = Diagnostic.query.get_or_404(id)
    db.session.delete(patient)
    db.session.commit()
    flash("Diagnostic deleted successfully!")
    return redirect(url_for("admin_diagnostics"))


@app.route('/admin/users')
@login_required
@role_required("admin")
def admin_users():
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@role_required("admin")
def edit_user(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        if request.form['password']:
            hashed_password = generate_password_hash(request.form['password'])
            user.password = hashed_password
        user.role = request.form['role']
        db.session.commit()
        return redirect(url_for('admin_users'))  # Redirect to the user management page
    # Render the registration form pre-filled with the user's data
    return render_template(
        'register.html',
        user=user,
        is_edit=True,
        action_url=url_for('edit_user', user_id=user.id),
        button_text="Update User",
        title_text="Edit User"
    )


@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@login_required
@role_required("admin")
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully.", "success")
    return redirect(url_for('admin_users'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)

