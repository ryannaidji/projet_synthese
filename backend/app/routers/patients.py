from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal, Base, get_db
from pydantic import BaseModel
from datetime import date, datetime
from app.models import Patient
from typing import List, Annotated
from app.role_checker import RoleChecker
from app.schemas import PatientResponse, PatientCreate
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/api/patients", tags=["Patients"])

@router.get("/", response_model=List[PatientResponse] )
async def list_patients(
        _: Annotated[bool, Depends(RoleChecker(allowed_roles=["doctor", "nurse","admin"]))], 
        db: Session = Depends(get_db)):
    return db.query(Patient).all()

@router.post("/", tags=["Patients"],response_model=PatientResponse)
async def create_patient(
        _: Annotated[bool, Depends(RoleChecker(allowed_roles=["doctor", "nurse","admin"]))],
        patient: PatientCreate, 
        db: Session = Depends(get_db)):
    patient_new = Patient(**patient.model_dump())
    db.add(patient_new)
    db.commit()
    db.refresh(patient_new)
    return patient_new

@router.get("/{patient_id}", tags=["Patients"], response_model=PatientResponse)
async def get_patient(
        _: Annotated[bool, Depends(RoleChecker(allowed_roles=["doctor", "nurse","admin"]))],
        patient_id: int, 
        db: SessionLocal = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.put("/{patient_id}", tags=["Patients"],response_model=PatientResponse)
async def update_patient(
        _: Annotated[bool, Depends(RoleChecker(allowed_roles=["doctor", "nurse","admin"]))],
        patient_id: int, 
        patient_new: PatientCreate, 
        db: SessionLocal = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient.name = patient_new.name
    patient.dob = patient_new.dob
    patient.gender = patient_new.gender
    patient.address = patient_new.address
    patient.phone = patient_new.phone
    db.commit()
    db.refresh(patient)
    return patient

@router.delete("/{patient_id}",tags=["Patients"])
async def delete_patient(
        _: Annotated[bool, Depends(RoleChecker(allowed_roles=["doctor", "nurse","admin"]))],
        patient_id: int, 
        db: SessionLocal = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    try:
        db.delete(patient)
        db.commit()
        return {"message": "Patient deleted successfully"}
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete patient because there are associated diagnostics."
        )

