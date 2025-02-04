import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, redirect, url_for, flash, abort, request, session, jsonify, Response
from datetime import datetime, date
import requests
import json
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel
import prometheus_client
from  middleware import setup_metrics
import jwt

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"

CONTENT_TYPE_LATEST = str('text/plain; version=0.0.4; charset=utf-8')

app = Flask(__name__)
setup_metrics(app)

@app.route('/metrics')
def metrics():
    return Response(prometheus_client.generate_latest(), mimetype=CONTENT_TYPE_LATEST)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///patients.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

BACKEND_URL="http://localhost:9000/"  

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ""
    success = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        response = requests.post(f"{BACKEND_URL}/token", data={"username": username, "password": password})
        print(response.text)
        if response.status_code == 200:
            data = response.json()
            session["access_token"] = data["access_token"]
            session["username"] = username

            try:
                decoded_token = jwt.decode(data["access_token"], SECRET_KEY, algorithms=["HS256"])
                role = decoded_token.get("role","user")
            except jwt.ExpiredSignatureError:
                flash("Session Expired.", "error")
            except jwt.InvalidTokenError:
                flash("Invalid token","error")
                return redirect("/")

            session["role"] = role
            success = "Logged as "+username
            flash("Logged as "+username, "flash-message success")
            return redirect(url_for('landing'))
        flash("Unable to login","flash-message error")

    return render_template('login.html')

@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("access_token", None)
    flash("Bye! You are logged out.", "flash-message success")
    return redirect(url_for("landing"))

@app.route("/token", methods=["POST"])
def get_token():
    response = requests.post(BACKEND_URL+"/token/",data=request.form)
    return response.text

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'nurse')  # Default to 'user' if no role is provided
        confirm_password = request.form['confirm_password']
        disabled = False

        if not username or not email or not password:
            flash('All fields are required.', "flash-message error" )
            return render_template('register.html', action_url=url_for('register'),button_text="Register", title_text="User Registration", form_action=request.form['form_action'])

        if password != confirm_password:
            flash("Passwords do not match", "flash-message error")
            return render_template('register.html', action_url=url_for('register'),button_text="Register", title_text="User Registration", form_action=request.form['form_action'])

        response = requests.post(f"{BACKEND_URL}/api/users/register", json={"username": username, "fullname": fullname, "email": email, "role": role, "disabled": disabled, "password": password})
        if response.status_code == 200:
            if request.form.get('form_action') == "new":
               flash("Registration successful! Please log in.", "flash-message success")
               return redirect("/")
            elif request.form.get('form_action') == "add":
               flash("User added successfully", "flash-message succcess")
               return redirect(url_for("admin_users"))
        else:
            flash(response.json()["detail"], "error")

    return render_template('register.html',action_url=url_for('register'), button_text="Register", title_text="User Registration",form_action="new")

@app.errorhandler(403)
def forbidden(e):
    return render_template("403.html"), 403

@app.get("/health")
def root():
    return {"message": "The frontend is LIVE!!"}

########################################################################################################################
#######################################             USERS MANAGEMENT             #######################################
########################################################################################################################

@app.route('/admin/users')
def admin_users():
    if session.get("role") != "admin":
        flash("Access Denied: You are not authorized to view this page.", "flash-message error")
        return redirect(url_for("landing"))

    token = session.get("access_token")
    if not token:
        flash("Please log in", "flash-message warning")
        return redirect(url_for("login"))

    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(f"{BACKEND_URL}/api/users", headers=headers)

    if response.status_code == 401:
        flash("Permission denied", "flash-message error")
        return redirect(url_for("login")) 
    
    return render_template('admin_users.html', users=json.loads(response.text))


@app.route('/admin/users/add', methods=['GET','POST'])
def add_user():
    if session.get("role") != "admin":
        flash("Access Denied: You are not authorized to view this page.", "flash-message error")
        return redirect(url_for("landing"))
    return render_template('register.html', action_url=url_for('register'), button_text="Add User", title_text="Add New User", form_action="add")

@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if session.get("role") != "admin":
        flash("Access Denied: You are not authorized to view this page.", "flash-message error")
        return redirect(url_for("landing"))

    token = session.get("access_token")
    if not token:
        flash("Please log in", "flash-message warning")
        return redirect(url_for("login"))

    headers = {"Authorization": f"Bearer {token}"}

    response = requests.delete(f"{BACKEND_URL}/api/users/{user_id}", headers=headers)

    if response.status_code == 401:
       flash("Permission denied", "flash-message error")
       return redirect(url_for("admin_users"))

    if response.status_code == 200:
       response_json = response.json()
       flash(response_json["message"],"flash-message success")
       return redirect(url_for('admin_users'))

@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if session.get("role") != "admin":
        flash("Access Denied: You are not authorized to view this page.", "flash-message error")
        return redirect(url_for("landing"))

    token = session.get("access_token")
    if not token:
        flash("Please log in", "flash-message warning")
        return redirect(url_for("login"))

    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(f"{BACKEND_URL}/api/users/{user_id}", headers=headers)

    if response.status_code == 401:
       flash("Permission denied", "flash-message error")
       return redirect(url_for("admin_users"))


    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.fullname = request.form['fullname']
        if request.form['password']:
            hashed_password = generate_password_hash(request.form['password'])
            user.password = hashed_password
        user.role = request.form['role']
        return redirect(url_for('admin_users'))  # Redirect to the user management page

    return render_template(
        'register.html',
        user=response.json(),
        is_edit=True,
        action_url=url_for('edit_user', user_id=user_id),
        button_text="Update User",
        title_text="Edit User"
    )

#######################################################################################################################
#####################################             PATIENTS MANAGEMENT             #####################################
#######################################################################################################################

@app.route('/admin/patients')
def admin_patients():
    if session.get("role") not in ["admin","doctor", "nurse"]:
        flash("Access Denied: You are not authorized to view this page.", "flash-message error")
        return redirect(url_for("landing"))

    token = session.get("access_token")
    if not token:
        flash("Please log in", "flash-message warning")
        return redirect(url_for("login"))

    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(f"{BACKEND_URL}/api/patients", headers=headers)

    if response.status_code == 401:
        flash("Permission denied", "flash-message error")
        return redirect(url_for("login"))

    return render_template('admin_patients.html', patients=json.loads(response.text))

@app.route("/admin/patients/add", methods=["GET", "POST"])
def add_patient():
    if session.get("role") not in ["admin","doctor", "nurse"]:
        flash("Access Denied: You are not authorized to view this page.", "flash-message error")
        return redirect(url_for("landing"))

    token = session.get("access_token")
    if not token:
        flash("Please log in", "flash-message warning")
        return redirect(url_for("login"))

    headers = {"Authorization": f"Bearer {token}"}

    if request.method == "POST":
        data = {}
        data['name'] = request.form["name"]
        data['dob'] = request.form["dob"]
        data['gender'] = request.form["gender"]
        data['address'] = request.form.get("address")
        data['phone'] = request.form.get("phone")
        response = requests.post(BACKEND_URL+"/api/patients",data=json.dumps(data), headers=headers)
        if response.status_code == 401:
           flash("Permission denied", "flash-message error")
        if response.status_code == 200:
           flash("Patient added", "flash-message success")
        
        return redirect(url_for("admin_patients"))
    
    return render_template("add_patient.html")

@app.route("/patients/delete/<int:id>", methods=["POST"])
def delete_patient(id):
    if session.get("role") not in ["admin","doctor", "nurse"]:
        flash("Access Denied: You are not authorized to view this page.", "flash-message error")
        return redirect(url_for("landing"))

    token = session.get("access_token")
    if not token:
        flash("Please log in", "flash-message warning")
        return redirect(url_for("login"))

    headers = {"Authorization": f"Bearer {token}"}

    response = requests.delete(BACKEND_URL+"/api/patients/"+str(id), headers=headers)

    if response.status_code == 401:
       flash("Permission denied", "flash-message error")
       return redirect(url_for("admin_patients"))

    if response.status_code == 200:
       response_json = response.json()
       flash(response_json["message"],"flash-message success")
       return redirect(url_for('admin_patients'))

@app.route("/patients/edit/<int:id>", methods=["GET", "POST"])
def edit_patient(id):

    if session.get("role") != "admin":
        flash("Access Denied: You are not authorized to view this page.", "flash-message error")
        return redirect(url_for("landing"))

    token = session.get("access_token")
    if not token:
        flash("Please log in", "flash-message warning")
        return redirect(url_for("login"))

    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(f"{BACKEND_URL}/api/patients/{id}", headers=headers)

    if response.status_code == 401:
       flash("Permission denied", "flash-message error")
       return redirect(url_for("admin_users"))

    if request.method == "POST":
        data = {}
        data['name'] = request.form["name"]
        data['dob'] = request.form["dob"]
        data['gender'] = request.form["gender"]
        data['address'] = request.form.get("address")
        data['phone'] = request.form.get("phone")
        response = requests.put(BACKEND_URL+"/api/patients/"+str(id),data=json.dumps(data), headers=headers)
        if response.status_code == 401:
           flash("Permission denied", "flash-message error")
        if response.status_code == 200:
           flash("Patient updated", "flash-message success")

        return redirect(url_for("admin_patients"))

    return render_template("add_patient.html", patient=response.json(), is_edit=True)


#######################################################################################################################
#####################################             DIAGNOSTICS MANAGEMENT             ##################################
#######################################################################################################################

@app.route('/diagnostic/<int:diagnostic_id>', methods=['GET'])
def show_diagnostic(diagnostic_id):

    if session.get("role") not in ["admin","doctor", "nurse"]:
        flash("Access Denied: You are not authorized to view this page.", "flash-message error")
        return redirect(url_for("landing"))

    token = session.get("access_token")
    if not token:
        flash("Please log in", "flash-message warning")
        return redirect(url_for("login"))

    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(f"{BACKEND_URL}/api/diagnostics/{diagnostic_id}", headers=headers)
    patients = requests.get(f"{BACKEND_URL}/api/patients", headers=headers)
    users = requests.get(f"{BACKEND_URL}/api/users", headers=headers)
    users_json = json.loads(users.text)
    doctors = [user for user in users_json if user["role"] in ["doctor"]]

    if response.status_code == 401:
       flash("Permission denied", "flash-message error")
       return redirect(url_for("landing"))

    return render_template('result.html', diagnostic=response.json(), patients=json.loads(patients.text), doctors=doctors)

@app.route('/diagnostic/add', methods=['GET','POST'])
def create_diagnostic():
    if session.get("role") not in ["admin","doctor", "nurse"]:
        flash("Access Denied: You are not authorized to view this page.", "flash-message error")
        return redirect(url_for("landing"))

    token = session.get("access_token")
    if not token:
        flash("Please log in", "flash-message warning")
        return redirect(url_for("login"))

    headers = {"Authorization": f"Bearer {token}"}

    users = requests.get(f"{BACKEND_URL}/api/users", headers=headers)
    users_json = json.loads(users.text)
    doctors = [user for user in users_json if user["role"] in ["doctor"]]
    patients = requests.get(f"{BACKEND_URL}/api/patients", headers=headers)

    if request.method == "POST":

        if 'file' not in request.files:
          return render_template('upload.html', error="No file part")

        file = request.files['file']

        if file.filename == '':
          return render_template('upload.html', error="No selected file")

        if file and allowed_file(file.filename):
          filename = secure_filename(file.filename)
          filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
          file.save(filepath)
        else:
            return render_template('upload.html', error="Invalid file type")

        now = datetime.now()
        patient_id = request.form['patient']
        analysis_link = filepath
        comment = ""
        status = False
        doctor_id = request.form['doctor']

        result_prediction = "TBD"

        data = {}
        data['patient_id'] = patient_id
        data['analysis_link'] = filepath
        data['prediction'] = result_prediction
        data['reviewed_comment'] = comment
        data['review_status'] = status
        data['doctor_id'] = doctor_id

        response = requests.post(BACKEND_URL+"/api/diagnostics",data=json.dumps(data), headers=headers)
        if response.status_code == 401:
           flash("Permission denied", "flash-message error")
        if response.status_code == 200:
           flash("Diagnostic added", "flash-message success")

        diagnostics = requests.get(f"{BACKEND_URL}/api/diagnostics", headers=headers)

        return render_template('diagnostics.html', diagnostics=json.loads(diagnostics.text), patients=json.loads(patients.text), doctors=doctors)

    return render_template('upload.html', patients=json.loads(patients.text), doctors=doctors)

@app.route('/admin/diagnostics', methods=['GET'])
def diagnostics():
    if session.get("role") not in ["admin","doctor", "nurse"]:
        flash("Access Denied: You are not authorized to view this page.", "flash-message error")
        return redirect(url_for("landing"))

    token = session.get("access_token")
    if not token:
        flash("Please log in", "flash-message warning")
        return redirect(url_for("login"))

    headers = {"Authorization": f"Bearer {token}"}

    users = requests.get(f"{BACKEND_URL}/api/users", headers=headers)
    users_json = json.loads(users.text)
    doctors = [user for user in users_json if user["role"] in ["doctor"]]
    patients = requests.get(f"{BACKEND_URL}/api/patients", headers=headers)

    response = requests.get(f"{BACKEND_URL}/api/diagnostics", headers=headers)
    if response.status_code == 401:
        flash("Permission denied", "flash-message error")
        return redirect(url_for("login"))

    return render_template('diagnostics.html', diagnostics=json.loads(response.text), patients=json.loads(patients.text), doctors=doctors)

@app.route('/admin/diagnostic/edit/<int:diagnostic_id>', methods=['GET', 'POST'])
def edit_diagnostic(diagnostic_id):

    if session.get("role") not in [ "admin","doctor"]:
        flash("Access Denied: You are not authorized to view this page.", "flash-message error")
        return redirect(url_for("landing"))

    token = session.get("access_token")
    if not token:
        flash("Please log in", "flash-message warning")
        return redirect(url_for("login"))

    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(f"{BACKEND_URL}/api/diagnostics/{diagnostic_id}", headers=headers)

    if response.status_code == 401:
       flash("Permission denied", "flash-message error")
       return redirect(url_for("diagnostics"))

    diagnostic = json.loads(response.text)

    if request.method == "POST":
        review_status = request.form.get('review_status')
        is_reviewed = review_status == 'on'
        diagnostic["review_status"] = is_reviewed
        diagnostic["reviewed_comment"] = request.form["reviewed_comment"]
        print(diagnostic)
        response = requests.put(BACKEND_URL+"/api/diagnostics/"+str(diagnostic_id),data=json.dumps(diagnostic), headers=headers)
        if response.status_code == 401:
           flash("Permission denied", "flash-message error")
        if response.status_code == 200:
           flash("Patient updated", "flash-message success")

        return redirect(url_for("diagnostics"))

@app.route("/admin/diagnostics/delete/<int:id>", methods=["POST"])
def delete_diagnostic(id):
    if session.get("role") not in ["admin","doctor" ]:
        flash("Access Denied: You are not authorized to view this page.", "flash-message error")
        return redirect(url_for("landing"))

    token = session.get("access_token")
    if not token:
        flash("Please log in", "flash-message warning")
        return redirect(url_for("login"))

    headers = {"Authorization": f"Bearer {token}"}

    response = requests.delete(BACKEND_URL+"/api/diagnostics/"+str(id), headers=headers)

    if response.status_code == 401:
       flash("Permission denied", "flash-message error")

    if response.status_code == 200:
       response_json = response.json()
       flash(response_json["message"],"flash-message success")

    return redirect(url_for('diagnostics'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)

