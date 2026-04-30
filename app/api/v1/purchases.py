from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, require_role
from app.models.user import User
from app.schemas.purchase import PurchaseCreate, PurchaseRead, PurchaseUpdate, PurchaseData
from app.services.purchase_service import PurchaseService

router = APIRouter(prefix="/purchases", tags=["Purchases"])


# ---------------------------------------------------
# CREATE PURCHASE (USER or ADMIN)
# ---------------------------------------------------
@router.post("/", response_model=PurchaseRead, status_code=status.HTTP_201_CREATED)
def create_purchase(
    data: PurchaseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = PurchaseService(db)
    purchase, error = service.create_purchase(data, current_user)

    if error:
        raise HTTPException(status_code=400, detail=error)

    return purchase


# ---------------------------------------------------
# GET PURCHASES OF CURRENT USER
# ---------------------------------------------------
@router.get("/me", response_model=List[PurchaseData])
def get_my_purchases(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = PurchaseService(db)
    return service.get_user_purchases(current_user.id)


# ---------------------------------------------------
# GET ALL PURCHASES (ADMIN)
# ---------------------------------------------------
@router.get("/", response_model=List[PurchaseRead], dependencies=[Depends(require_role("admin"))])
def get_all_purchases(
    db: Session = Depends(get_db)
):
    service = PurchaseService(db)
    return service.get_all()


# ---------------------------------------------------
# UPDATE PURCHASE (ADMIN)
# ---------------------------------------------------
@router.put("/{purchase_id}", response_model=PurchaseRead, dependencies=[Depends(require_role("admin"))])
def update_purchase(
    purchase_id: int,
    data: PurchaseUpdate,
    db: Session = Depends(get_db)
):
    service = PurchaseService(db)
    purchase, error = service.update_purchase(purchase_id, data)

    if error:
        raise HTTPException(status_code=404, detail=error)

    return purchase


# ---------------------------------------------------
# DELETE PURCHASE (ADMIN)
# ---------------------------------------------------
@router.delete("/{purchase_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_role("admin"))])
def delete_purchase(
    purchase_id: int,
    db: Session = Depends(get_db)
):
    service = PurchaseService(db)
    deleted, error = service.delete_purchase(purchase_id)

    if error:
        raise HTTPException(status_code=404, detail=error)

    return None
