from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard Intelligence"])


@router.get("/kpis", response_model=Dict[str, Any])
@router.get("/summary", response_model=Dict[str, Any])
def get_dashboard_summary(
    db: Session = Depends(get_db),
):
    """Retrieve operational dashboard KPIs and risk aggregates."""
    return DashboardService.get_summary(db)
