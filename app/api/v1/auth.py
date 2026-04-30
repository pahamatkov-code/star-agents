from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import LoginRequest, TokenPair, RefreshRequest
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Auth"])


# ---------------------------
# REGISTER
# ---------------------------
@router.post("/register", response_model=dict)
def register_user(data: LoginRequest, db: Session = Depends(get_db)):
    user_service = UserService(db)

    existing = user_service.get_by_email(data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    hashed_password = get_password_hash(data.password)
    user = user_service.create_user(
        email=data.email,
        hashed_password=hashed_password,
        role="user",
    )

    return {"message": "User registered successfully", "user_id": user.id}


# ---------------------------
# LOGIN
# ---------------------------
@router.post("/login", response_model=TokenPair)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user_service = UserService(db)

    user = user_service.get_by_email(form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    access_token = create_access_token(user_id=user.id, role=user.role)
    refresh_token = create_refresh_token(user_id=user.id, role=user.role)

    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


# ---------------------------
# REFRESH TOKEN
# ---------------------------
@router.post("/refresh", response_model=TokenPair)
def refresh_token(data: RefreshRequest, db: Session = Depends(get_db)):
    payload = decode_token(data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = int(payload.get("sub"))
    role = payload.get("role")

    user_service = UserService(db)
    user = user_service.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_access = create_access_token(user_id=user.id, role=user.role)
    new_refresh = create_refresh_token(user_id=user.id, role=user.role)

    return TokenPair(
        access_token=new_access,
        refresh_token=new_refresh,
        token_type="bearer",
    )
