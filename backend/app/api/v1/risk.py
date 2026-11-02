from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.db.models.user import User
from backend.app.schemas.risk import RiskResultRead, RiskRunResponse
from backend.app.schemas.common import PaginatedResponse
from backend.app.services.risk_service import RiskService
from backend.app.core.deps import get_current_user
from backend.app.core.errors import NotFoundException

router = APIRouter(prefix="/risk", tags=["Stock-Out Risk"])


@router.get("", response_model=PaginatedResponse[RiskResultRead])
def get_risk_results(
    search: Optional[str] = None,
    category_id: Optional[str] = None,
    risk_level: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    sort_by: str = "risk_score",
    sort_dir: str = "desc",
    db: Session = Depends(get_db),
):
    """Retrieve paginated stock-out risk assessment results with explainability factors."""
    res = RiskService.get_results(
        db=db,
        search=search,
        category_id=category_id,
        risk_level=risk_level,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    return PaginatedResponse(
        data=res["data"],
        total=res["total"],
        page=res["page"],
        page_size=res["page_size"],
        total_pages=res["total_pages"],
    )


@router.get("/{medicine_id}", response_model=RiskResultRead)
def get_medicine_risk(
    medicine_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve risk details for a single medicine."""
    result = RiskService.get_by_medicine(db, medicine_id)
    if not result:
        raise NotFoundException("RiskResult", medicine_id)
    return result


@router.post("/run", response_model=RiskRunResponse, status_code=status.HTTP_200_OK)
def run_risk_analysis(
    db: Session = Depends(get_db),
):
    """Recomputes stock-out risk, coverage, and required stock across all medicines."""
    return RiskService.run_all(db)

