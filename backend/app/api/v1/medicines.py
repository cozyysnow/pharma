import math
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.db.models.user import User
from backend.app.schemas.medicine import MedicineRead, MedicineCreate, MedicineUpdate
from backend.app.schemas.common import PaginatedResponse, StatusResponse
from backend.app.services.medicine_service import MedicineService
from backend.app.core.deps import require_manager_or_admin
from backend.app.core.errors import NotFoundException

router = APIRouter(prefix="/medicines", tags=["Medicines"])


@router.get("", response_model=PaginatedResponse[MedicineRead])
def list_medicines(
    search: Optional[str] = None,
    category_id: Optional[str] = None,
    supplier_id: Optional[str] = None,
    is_active: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    sort_by: str = "medicine_id",
    sort_dir: str = "asc",
    db: Session = Depends(get_db),
):
    """Retrieve medicines with search, category/supplier filters, sorting, and pagination."""
    items, total = MedicineService.list_medicines(
        db=db,
        search=search,
        category_id=category_id,
        supplier_id=supplier_id,
        is_active=is_active,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    return PaginatedResponse(
        data=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{medicine_id}", response_model=MedicineRead)
def get_medicine(
    medicine_id: str,
    db: Session = Depends(get_db),
):
    """Get single medicine by ID with category and primary supplier."""
    med = MedicineService.get_by_id(db, medicine_id)
    if not med:
        raise NotFoundException("Medicine", medicine_id)
    return med


@router.post("", response_model=MedicineRead, status_code=status.HTTP_201_CREATED)
def create_medicine(
    payload: MedicineCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_manager_or_admin),
):
    """Manager/Admin: Register a new medicine and initialize inventory tracking."""
    return MedicineService.create(db, payload)


@router.patch("/{medicine_id}", response_model=MedicineRead)
def update_medicine(
    medicine_id: str,
    payload: MedicineUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_manager_or_admin),
):
    """Manager/Admin: Update medicine master details."""
    return MedicineService.update(db, medicine_id, payload)


@router.post("/{medicine_id}/deactivate", response_model=StatusResponse)
def deactivate_medicine(
    medicine_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_manager_or_admin),
):
    """Manager/Admin: Soft-deactivate a medicine."""
    MedicineService.deactivate(db, medicine_id)
    return StatusResponse(status="success", message=f"Medicine {medicine_id} deactivated.")
