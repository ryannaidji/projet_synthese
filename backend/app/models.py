from app.database import Base
from sqlalchemy import Column, Integer, String, Date, create_engine, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import date, datetime

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    dob = Column(Date, nullable=False)  # Date of Birth
    gender = Column(String(10), nullable=False)
    phone = Column(String(20), nullable=True)
    address = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.now())

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False, unique=True)
    fullname = Column(String(100), nullable=True, unique=True)
    email = Column(String(150), nullable=False, unique=True)
    hashed_password = Column(String(200), nullable=False)
    role = Column(String(50), nullable=False)  # e.g., 'admin', 'doctor', 'nurse'
    created_at = Column(DateTime, default=datetime.now())
    disabled = Column(Boolean, nullable=False,default=False)

class Diagnostic(Base):
    __tablename__ = "diagnostics"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    analysis_link = Column(String(255), nullable=False)  # Date of Birth
    prediction = Column(String(255), nullable=False)
    reviewed_comment = Column(String(255), nullable=True)
    review_status = Column(Boolean,nullable=False)
    doctor_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.now())
    patient = relationship("Patient")
    user = relationship("User")
