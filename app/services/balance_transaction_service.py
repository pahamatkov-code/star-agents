from sqlalchemy.orm import Session

from app.repositories.balance_transaction_repository import BalanceTransactionRepository
from app.schemas.balance_transaction import (
    BalanceTransactionCreate,
    BalanceTransactionUpdate,
)


class BalanceTransactionService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = BalanceTransactionRepository(db)

    # ---------------------------------------------------
    # CREATE (ADMIN)
    # ---------------------------------------------------
    def create_transaction(self, data: BalanceTransactionCreate):
        """
        Admin може створювати транзакції вручну:
        - adjustment
        - manual topup
        - manual refund
        """
        transaction = self.repo.create(data.dict())
        return transaction, None

    # ---------------------------------------------------
    # GET BY ID
    # ---------------------------------------------------
    def get_transaction(self, transaction_id: int):
        return self.repo.get(transaction_id)

    # ---------------------------------------------------
    # GET ALL (ADMIN)
    # ---------------------------------------------------
    def get_all_transactions(self):
        return self.repo.get_all()

    # ---------------------------------------------------
    # GET USER TRANSACTIONS (USER)
    # ---------------------------------------------------
    def get_user_transactions(self, user_id: int):
        return self.repo.get_by_user(user_id)

    # ---------------------------------------------------
    # UPDATE (ADMIN)
    # ---------------------------------------------------
    def update_transaction(self, transaction_id: int, data: BalanceTransactionUpdate):
        transaction = self.repo.get(transaction_id)
        if not transaction:
            return None, "Transaction not found"

        updated = self.repo.update(transaction, data.dict(exclude_unset=True))
        return updated, None

    # ---------------------------------------------------
    # DELETE (ADMIN)
    # ---------------------------------------------------
    def delete_transaction(self, transaction_id: int):
        transaction = self.repo.get(transaction_id)
        if not transaction:
            return None, "Transaction not found"

        self.repo.delete(transaction)
        return True, None
