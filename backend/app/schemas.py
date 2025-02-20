from datetime import date, datetime
from pydantic import BaseModel

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

class UserResponse(BaseModel):
    id: int
    username: str
    fullname: str
    email: str
    role: str
    created_at: datetime
    hashed_password: str
    disabled: bool

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    username: str
    fullname: str
    email: str
    password: str
    role: str
    #created_at: datetime
    disabled: bool = False

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class DiagnosticResponse(BaseModel):
    id: int
    patient_id: int
    analysis_link: str
    prediction: str
    confidence: float
    reviewed_comment: str
    review_status: bool
    doctor_id: int
    created_at: datetime

class DiagnosticCreate(BaseModel):
    patient_id: int
    analysis_link: str
    prediction: str
    confidence: float
    reviewed_comment: str
    review_status: bool
    doctor_id: int
    #created_at: date

