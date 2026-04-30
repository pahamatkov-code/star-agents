from sqlalchemy.orm import Session
from app.models.balance_transaction import BalanceTransaction


class BalanceTransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    # -----------------------------
    # CREATE
    # -----------------------------
    def create(self, data: dict) -> BalanceTransaction:
        transaction = BalanceTransaction(**data)
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    # -----------------------------
    # GET BY ID
    # -----------------------------
    def get(self, transaction_id: int) -> BalanceTransaction | None:
        return (
            self.db.query(BalanceTransaction)
            .filter(BalanceTransaction.id == transaction_id)
            .first()
        )

    # -----------------------------
    # GET ALL (ADMIN)
    # -----------------------------
    def get_all(self):
        return self.db.query(BalanceTransaction).all()

    # -----------------------------
    # GET BY USER
    # -----------------------------
    def get_by_user(self, user_id: int):
        return (
            self.db.query(BalanceTransaction)
            .filter(BalanceTransaction.user_id == user_id)
            .order_by(BalanceTransaction.created_at.desc())
            .all()
        )

    # -----------------------------
    # UPDATE (ADMIN)
    # -----------------------------
    def update(self, transaction: BalanceTransaction, data: dict):
        for key, value in data.items():
            setattr(transaction, key, value)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    # -----------------------------
    # DELETE (ADMIN)
    # -----------------------------
    def delete(self, transaction: BalanceTransaction):
        self.db.delete(transaction)
        self.db.commit()
        return True
