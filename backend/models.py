from database import Base
from sqlalchemy import Column, Integer, String, Date, create_engine, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import date, datetime
from pydantic import BaseModel

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    dob = Column(Date, nullable=False)  # Date of Birth
    gender = Column(String(10), nullable=False)
    phone = Column(String(20), nullable=True)
    address = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.now())

class PatientResponse(BaseModel):
    id: int
    name: str
    dob: date
    gender: str
    phone: str
    address: str

class PatientCreate(BaseModel):
    name: str
    dob: date
    gender: str
    phone: str
    address: str

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False, unique=True)
    fullname = Column(String(100), nullable=True, unique=True)
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(200), nullable=False)
    role = Column(String(50), nullable=False)  # e.g., 'admin', 'doctor', 'nurse'
    created_at = Column(DateTime, default=datetime.now())

class UserResponse(BaseModel):
    id: int
    username: str
    fullname: str
    email: str
    role: str
    created_at: date

class UserCreate(BaseModel):
    username: str
    fullname: str
    email: str
    password: str
    role: str
    created_at: date

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

class DiagnosticResponse(BaseModel):
    id: int
    patient_id: int
    analysis_link: str
    prediction: str
    reviewed_comment: str
    review_status: bool
    doctor_id: int
    created_at: date

class DiagnosticCreate(BaseModel):
    patient_id: int
    analysis_link: str
    prediction: str
    reviewed_comment: str
    review_status: bool
    doctor_id: int
    created_at: date


