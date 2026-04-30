from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import schemas, crud
from app.database import get_db
from app.models import User
from app.routers.auth import get_current_user
from app.utils import get_password_hash  # утиліта для хешування паролів

router = APIRouter(prefix="/users", tags=["users"])

# === Реєстрація користувача ===
@router.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # хешування пароля перед збереженням
    hashed_pw = get_password_hash(user.password)
    return crud.create_user(db=db, user=user, hashed_password=hashed_pw)

# === Отримати поточного користувача ===
@router.get("/me", response_model=schemas.User)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# === Перегляд покупок поточного користувача ===
@router.get("/me/purchases", response_model=List[schemas.PurchaseData])
def get_user_purchases(db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    return crud.get_purchases_by_user(db, user_id=current_user.id)
