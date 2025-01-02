mock_diagnostics = [
        {
            'id':'1',
            'date_of_prediction': '2024-12-01',
            'patient_name': 'John Doe',
            'image_id': 1,
            'prediction_probability': 87,
            'reviewed_comment': 'Possible tumor detected, further tests required.',
            'review_status': 'Reviewed',
            'doctor_name': 'Dr. Smith'
        },
        {
            'id':'2',
            'date_of_prediction': '2024-12-05',
            'patient_name': 'Jane Doe',
            'image_id': 2,
            'prediction_probability': 92,
            'reviewed_comment': 'High probability of benign tumor.',
            'review_status': 'Reviewed',
            'doctor_name': 'Dr. Johnson'
        },
        {
            'id':'3',
            'date_of_prediction': '2024-12-10',
            'patient_name': 'Mark Smith',
            'image_id': 3,
            'prediction_probability': 75,
            'reviewed_comment': 'Unclear results, further analysis needed.',
            'review_status': 'Not Reviewed',
            'doctor_name': 'Dr. Lee'
        }
]

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Diagnostic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(100), nullable=False)
    image_path = db.Column(db.Date, nullable=False)  # Date of Birth
    prediction = db.Column(db.String(10), nullable=False)
    reviewed_comment = db.Column(db.String(20), nullable=True)
    review_status = db.Column(db.String(100), nullable=False)
    doctor_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)  # Date of Birth
    gender = db.Column(db.String(10), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # e.g., 'admin', 'doctor', 'nurse'
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

