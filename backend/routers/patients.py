from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, Base, get_db
from pydantic import BaseModel
from datetime import date, datetime
from models import Patient, PatientResponse, PatientCreate

router = APIRouter(prefix="/api/patients", tags=["Patients"])

@router.get("/", tags=["Patients"])
async def list_patients(db: Session = Depends(get_db)):
    return db.query(Patient).all()

@router.post("/", tags=["Patients"],response_model=PatientResponse)
async def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    patient_new = Patient(**patient.model_dump())
    db.add(patient_new)
    db.commit()
    db.refresh(patient_new)
    return patient_new

@router.get("/{patient_id}", tags=["Patients"], response_model=PatientResponse)
async def get_patient(patient_id: int, db: SessionLocal = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.put("/{patient_id}", tags=["Patients"],response_model=PatientResponse)
async def update_patient(patient_id: int, patient_new: PatientCreate, db: SessionLocal = Depends(get_db)):
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
async def delete_patient(patient_id: int, db: SessionLocal = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    db.delete(patient)
    db.commit()
    return {"message": "Patient deleted"}

