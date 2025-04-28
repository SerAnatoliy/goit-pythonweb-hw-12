from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import shutil
import os

from app.config import SessionLocal
import app.database.schemas as schemas
import app.database.crud as crud
from app.services.auth import (
    authenticate_user,
    create_access_token,
    create_reset_token,
    verify_reset_token,
    get_current_admin_user
)
from loguru import logger

router = APIRouter(prefix="/users", tags=["Users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/signup", response_model=schemas.UserResponse, status_code=201)
def signup(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    new_user = crud.create_user(db, user_data)
    return new_user

@router.post("/login")
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(hours=1)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/test")
def test_route():
    return {"message": "Users API is working!"}

@router.post("/reset_password_request/")
def request_password_reset(email: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reset_token = create_reset_token(email)
    reset_link = f"http://localhost:8000/users/reset_password/?token={reset_token}"
    logger.info(f"Password reset forÑ {email}: {reset_link}")

    return {"message": "Password reset link has been sent (check logs)."}

@router.post("/reset_password/")
def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    email = verify_reset_token(token)
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    user = crud.update_user_password(db, email, new_password)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {"message": "Password was resetted"}

@router.post("/avatar", response_model=schemas.UserResponse)
def update_user_avatar(
    file: UploadFile = File(...),
    current_user: schemas.UserResponse = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    avatar_dir = "static/avatars"
    os.makedirs(avatar_dir, exist_ok=True)

    avatar_path = os.path.join(avatar_dir, file.filename)
    with open(avatar_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    user = crud.get_user_by_email(db, current_user.email)
    updated_user = crud.update_avatar(db, user, avatar_path)
    return updated_user
