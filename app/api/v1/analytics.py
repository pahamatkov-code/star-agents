from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import AnalyticsResponse


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get(
    "/dashboard",
    response_model=AnalyticsResponse,
    dependencies=[Depends(require_role("admin"))]
)
def get_dashboard(db: Session = Depends(get_db)):
    """
    Повертає повну аналітику:
    - покупки (KPI + графіки + топи)
    - баланс (KPI + графіки)
    """
    service = AnalyticsService(db)
    data = service.get_dashboard()
    return AnalyticsResponse(**data)
