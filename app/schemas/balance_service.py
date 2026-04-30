from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models import User


class BalanceService:
    def __init__(self, db: Session):
        self.db = db

    # -----------------------------
    # ADMIN: поповнення будь-якому користувачу
    # -----------------------------
    def admin_top_up(self, user_id: int, amount: int):
        user = self.db.query(User).get(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        user.balance += amount
        self.db.commit()
        self.db.refresh(user)

        return user

    # -----------------------------
    # USER: поповнення собі
    # -----------------------------
    def user_top_up(self, user: User, amount: int):
        user.balance += amount
        self.db.commit()
        self.db.refresh(user)
        return user
