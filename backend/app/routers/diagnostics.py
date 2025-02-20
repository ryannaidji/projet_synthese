from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal, Base, get_db
from pydantic import BaseModel
from datetime import date, datetime
from app.models import Diagnostic
from app.schemas import DiagnosticResponse, DiagnosticCreate
from typing import List, Annotated
from app.role_checker import RoleChecker

router = APIRouter(prefix="/api/diagnostics", tags=["Diagnostics"])

@router.get("/")
async def list_diagnostics(
        _: Annotated[bool, Depends(RoleChecker(allowed_roles=["doctor", "nurse","admin"]))],
        db: Session = Depends(get_db)):
    return db.query(Diagnostic).all()

@router.post("/",response_model=DiagnosticResponse)
async def create_diagnostic(
        _: Annotated[bool, Depends(RoleChecker(allowed_roles=["doctor", "nurse","admin"]))],
        diagnostic: DiagnosticCreate, 
        db: Session = Depends(get_db)):
    diagnostic_new = Diagnostic(**diagnostic.model_dump())
    db.add(diagnostic_new)
    db.commit()
    db.refresh(diagnostic_new)
    return diagnostic_new

@router.get("/{diagnostic_id}", response_model=DiagnosticResponse)
async def get_diagnostic(
        _: Annotated[bool, Depends(RoleChecker(allowed_roles=["doctor", "nurse","admin"]))],
        diagnostic_id: int, 
        db: SessionLocal = Depends(get_db)):
    diagnostic = db.query(Diagnostic).filter(Diagnostic.id == diagnostic_id).first()
    if not diagnostic:
        raise HTTPException(status_code=404, detail="Diagnostic not found")
    return diagnostic

@router.put("/{diagnostic_id}")
async def update_diagnostic(
        _: Annotated[bool, Depends(RoleChecker(allowed_roles=["doctor", "nurse","admin"]))],
        diagnostic_id: int, 
        diagnostic_new: DiagnosticCreate, 
        db: SessionLocal = Depends(get_db)):
    diagnostic = db.query(Diagnostic).filter(Diagnostic.id == diagnostic_id).first()
    if not diagnostic:
        raise HTTPException(status_code=404, detail="Patient not found")
    diagnostic.patient_id = diagnostic_new.patient_id
    diagnostic.analysis_link = diagnostic_new.analysis_link
    diagnostic.reviewed_comment = diagnostic_new.reviewed_comment
    diagnostic.doctor_id = diagnostic_new.doctor_id
    diagnostic.prediction = diagnostic_new.prediction
    diagnostic.confidence = diagnostic_new.confidence
    diagnostic.review_status = diagnostic_new.review_status
    db.commit()
    db.refresh(diagnostic)
    return {"message": "Diagnostic updated"}

@router.delete("/{diagnostic_id}")
async def delete_diagnostic(
        _: Annotated[bool, Depends(RoleChecker(allowed_roles=["doctor", "nurse","admin"]))],
        diagnostic_id: int, 
        db: SessionLocal = Depends(get_db)):
    diagnostic = db.query(Diagnostic).filter(Diagnostic.id == diagnostic_id).first()
    if not diagnostic:
        raise HTTPException(status_code=404, detail="Diagnostic not found")
    db.delete(diagnostic)
    db.commit()
    return {"message": "Diagnostic deleted"}
