from fastapi import FastAPI, Depends, HTTPException
from app.routers import patients, users, diagnostics, predictions
from app.database import engine, get_db
from prometheus_fastapi_instrumentator import Instrumentator, metrics
from passlib.context import CryptContext
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt
from fastapi import Depends, FastAPI, HTTPException, status
import app.models as models
from app.schemas import Token, UserResponse
from app.auth import SECRET_KEY,ACCESS_TOKEN_EXPIRE_MINUTES,ALGORITHM, get_user, authenticate_user, create_access_token
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/token", response_model=Token)
async def login_for_access_token( 
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
            data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

app.include_router(patients.router)
app.include_router(users.router)
app.include_router(diagnostics.router)
app.include_router(predictions.router)

@app.get("/api/health")
def root():
    return {"message": "The API is LIVE!!"}
