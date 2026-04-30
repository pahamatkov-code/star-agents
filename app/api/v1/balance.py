from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role
from app.schemas.balance import BalanceTopUpRequest
from app.services.balance_service import BalanceService

router = APIRouter(prefix="/balance", tags=["Balance"])


@router.post("/topup", dependencies=[Depends(require_role("admin"))])
def topup_balance(data: BalanceTopUpRequest, db: Session = Depends(get_db)):
    return BalanceService.topup(db, data.user_id, data.amount)


@router.get("/{user_id}")
def get_user_balance(user_id: int, db: Session = Depends(get_db)):
    return BalanceService.get_balance(db, user_id)
