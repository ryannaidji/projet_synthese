from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal, Base, get_db
from pydantic import BaseModel
from datetime import date, datetime
from app.models import User
from typing import List
from typing import Annotated
from app.role_checker import RoleChecker
from app.auth import get_current_active_user, get_password_hash
from app.schemas import UserResponse, UserCreate

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.post('/register')
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password,email=user.email,role=user.role,disabled=False,fullname=user.fullname)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}

@router.get("/", response_model=List[UserResponse])
async def list_users(
        _: Annotated[bool, Depends(RoleChecker(allowed_roles=["admin"]))],
        db: Session = Depends(get_db)):
    return db.query(User).all()

@router.post("/")
async def create_user(
        _: Annotated[bool, Depends(RoleChecker(allowed_roles=["admin"]))],
        user: UserCreate, 
        db: Session = Depends(get_db)):
    return register(user,db)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
        _: Annotated[bool, Depends(RoleChecker(allowed_roles=["admin"]))],
        user_id: int, 
        db: SessionLocal = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
        _: Annotated[bool, Depends(RoleChecker(allowed_roles=["admin"]))],
        user_id: int, 
        user_new: UserCreate, 
        db: SessionLocal = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.username = user_new.username
    user.fullname = user_new.fullname
    user.email = user_new.email
    user.role = user_new.role
    user.disabled = user_new.disabled
    hashed_password = get_password_hash(user_new.password)
    user.hashed_password = hashed_password
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}")
async def delete_user(
        _: Annotated[bool, Depends(RoleChecker(allowed_roles=["admin"]))],
        user_id: int, 
        db: SessionLocal = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}

