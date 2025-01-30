from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class Diagnostic(db.Model):
    __tablename__ = "diagnostics"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    analysis_link = db.Column(db.String(255), nullable=False)  # Date of Birth
    prediction = db.Column(db.String(255), nullable=False)
    reviewed_comment = db.Column(db.String(255), nullable=True)
    review_status = db.Column(db.Boolean,nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
#    patient = relationship("Patient")
    user = relationship("User")

from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    fullname = db.Column(db.String(100), nullable=True, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # e.g., 'admin', 'doctor', 'nurse'
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

