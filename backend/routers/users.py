from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, Base
from pydantic import BaseModel
from datetime import date, datetime
from models import User, UserResponse, UserCreate

router = APIRouter(prefix="/api/users", tags=["Users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
async def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.post("/",response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    user_new = User(**user.model_dump())
    db.add(user_new)
    db.commit()
    db.refresh(user_new)
    return user_new

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: SessionLocal = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_new: UserCreate, db: SessionLocal = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Patient not found")
    #patient.name = patient_new.name
    #patient.dob = patient_new.dob
    #patient.gender = patient_new.gender
    #patient.address = patient_new.address
    #patient.phone = patient_new.phone
    db.commit()
    db.refresh(patient)
    return patient

@router.delete("/{user_id}")
async def delete_user(user_id: int, db: SessionLocal = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}

