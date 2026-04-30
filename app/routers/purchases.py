from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.purchase import PurchaseCreate, PurchaseRead, PurchaseData
from app.services.purchase_service import PurchaseService
from app.core.deps import get_current_user, require_role
from app.models import User

router = APIRouter(
    prefix="/purchases",
    tags=["Purchases"],
)


# === Створення покупки (USER) ===
@router.post("/", response_model=PurchaseRead, status_code=status.HTTP_201_CREATED)
def create_purchase(
    data: PurchaseCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Створює покупку від імені поточного користувача.
    user_id береться з JWT.
    """
    service = PurchaseService(db)
    data.user_id = user.id
    return service.create_purchase(data)


# === Перегляд покупок поточного користувача (USER) ===
@router.get("/me", response_model=List[PurchaseData])
def get_my_purchases(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Повертає покупки поточного користувача.
    """
    service = PurchaseService(db)
    return service.get_purchases_by_user(user.id)


# === Перегляд усіх покупок (ADMIN) ===
@router.get("/", response_model=List[PurchaseRead], dependencies=[Depends(require_role("admin"))])
def get_all_purchases(
    db: Session = Depends(get_db),
):
    """
    Повертає всі покупки.
    Доступно тільки для admin.
    """
    service = PurchaseService(db)
    return service.get_all_purchases()


# === Видалення покупки (ADMIN) ===
@router.delete("/{purchase_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_role("admin"))])
def delete_purchase(
    purchase_id: int,
    db: Session = Depends(get_db),
):
    """
    Видаляє покупку.
    Доступно тільки для admin.
    """
    service = PurchaseService(db)
    deleted = service.delete_purchase(purchase_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Purchase not found")

    return None
