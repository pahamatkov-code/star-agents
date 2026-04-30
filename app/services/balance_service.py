from sqlalchemy.orm import Session

from app.models.user import User
from app.models.balance_transaction import BalanceTransaction


class BalanceService:
    def __init__(self, db: Session):
        self.db = db

    # ---------------------------
    # GET USER BALANCE
    # ---------------------------
    def get_balance(self, user_id: int):
        user = self.db.query(User).filter(User.id == user_id).first()
        return user.balance if user else None

    # ---------------------------
    # ADD FUNDS
    # ---------------------------
    def add_funds(self, user_id: int, amount: float):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None, "User not found"

        user.balance += amount

        transaction = BalanceTransaction(
            user_id=user.id,
            amount=amount,
            type="deposit"
        )
        self.db.add(transaction)

        self.db.commit()
        self.db.refresh(user)

        return user, None

    # ---------------------------
    # GET TRANSACTION HISTORY
    # ---------------------------
    def get_transactions(self, user_id: int):
        return (
            self.db.query(BalanceTransaction)
            .filter(BalanceTransaction.user_id == user_id)
            .order_by(BalanceTransaction.created_at.desc())
            .all()
        )
