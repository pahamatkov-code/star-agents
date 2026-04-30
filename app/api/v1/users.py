from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, require_role
from app.models.user import User
from app.schemas.user import UserRead
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserRead)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user


@router.get("/{user_id}", response_model=UserRead, dependencies=[Depends(require_role("admin"))])
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    user = user_service.get(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
