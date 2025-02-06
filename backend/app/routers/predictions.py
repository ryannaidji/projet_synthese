from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal, Base
from pydantic import BaseModel
from datetime import date, datetime
import json

router = APIRouter(prefix="/api/predict", tags=["Predictions"])

@router.get("/")
async def predict_bain_cancer():
    data = {}
    data['prediction'] = '60'
    json_data = json.dumps(data)
    return json_data
