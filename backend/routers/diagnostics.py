from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, Base
from pydantic import BaseModel
from datetime import date, datetime
from models import Diagnostic, DiagnosticResponse, DiagnosticCreate

router = APIRouter(prefix="/api/diagnostics", tags=["Diagnostics"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
async def list_diagnostics(db: Session = Depends(get_db)):
    return db.query(Diagnostic).all()

@router.post("/",response_model=DiagnosticResponse)
async def create_diagnostic(diagnostic: DiagnosticCreate, db: Session = Depends(get_db)):
    diagnostic_new = Diagnostic(**diagnostic.model_dump())
    db.add(diagnostic_new)
    db.commit()
    db.refresh(diagnostic_new)
    return diagnostic_new

@router.get("/{diagnostic_id}", response_model=DiagnosticResponse)
async def get_diagnostic(diagnostic_id: int, db: SessionLocal = Depends(get_db)):
    diagnostic = db.query(Diagnostic).filter(Diagnostic.id == diagnostic_id).first()
    if not diagnostic:
        raise HTTPException(status_code=404, detail="Diagnostic not found")
    return diagnostic

@router.put("/{diagnostic_id}", response_model=DiagnosticResponse)
async def update_diagnostic(diagnostic_id: int, diagnostic_new: DiagnosticCreate, db: SessionLocal = Depends(get_db)):
    diagnostic = db.query(Diagnostic).filter(Diagnostic.id == diagnostic_id).first()
    if not diagnostic:
        raise HTTPException(status_code=404, detail="Patient not found")
    #patient.name = patient_new.name
    #patient.dob = patient_new.dob
    #patient.gender = patient_new.gender
    #patient.address = patient_new.address
    #patient.phone = patient_new.phone
    db.commit()
    db.refresh(patient)
    return patient

@router.delete("/{diagnostic_id}")
async def delete_diagnostic(diagnostic_id: int, db: SessionLocal = Depends(get_db)):
    diagnostic = db.query(Diagnostic).filter(Diagnostic.id == diagnostic_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Diagnostic not found")
    db.delete(diagnostic)
    db.commit()
    return {"message": "Diagnostic deleted"}

