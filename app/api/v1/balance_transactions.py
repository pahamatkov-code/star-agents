from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, require_role
from app.schemas.balance_transaction import (
    BalanceTransactionCreate,
    BalanceTransactionRead,
    BalanceTransactionUpdate,
)
from app.services.balance_transaction_service import BalanceTransactionService
from app.models.user import User

router = APIRouter(
    prefix="/balance-transactions",
    tags=["Balance Transactions"],
)


# ---------------------------------------------------
# USER: Get own transactions
# ---------------------------------------------------
@router.get("/me", response_model=List[BalanceTransactionRead])
def get_my_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = BalanceTransactionService(db)
    return service.get_user_transactions(current_user.id)


# ---------------------------------------------------
# ADMIN: Get all transactions
# ---------------------------------------------------
@router.get(
    "/", 
    response_model=List[BalanceTransactionRead],
    dependencies=[Depends(require_role("admin"))]
)
def get_all_transactions(
    db: Session = Depends(get_db),
):
    service = BalanceTransactionService(db)
    return service.get_all_transactions()


# ---------------------------------------------------
# ADMIN: Create transaction manually
# ---------------------------------------------------
@router.post(
    "/", 
    response_model=BalanceTransactionRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin"))]
)
def create_transaction(
    data: BalanceTransactionCreate,
    db: Session = Depends(get_db),
):
    service = BalanceTransactionService(db)
    transaction, error = service.create_transaction(data)

    if error:
        raise HTTPException(status_code=400, detail=error)

    return transaction


# ---------------------------------------------------
# ADMIN: Update transaction
# ---------------------------------------------------
@router.put(
    "/{transaction_id}",
    response_model=BalanceTransactionRead,
    dependencies=[Depends(require_role("admin"))]
)
def update_transaction(
    transaction_id: int,
    data: BalanceTransactionUpdate,
    db: Session = Depends(get_db),
):
    service = BalanceTransactionService(db)
    transaction, error = service.update_transaction(transaction_id, data)

    if error:
        raise HTTPException(status_code=404, detail=error)

    return transaction


# ---------------------------------------------------
# ADMIN: Delete transaction
# ---------------------------------------------------
@router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("admin"))]
)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
):
    service = BalanceTransactionService(db)
    deleted, error = service.delete_transaction(transaction_id)

    if error:
        raise HTTPException(status_code=404, detail=error)

    return None
