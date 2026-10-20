import math
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.db.models.user import User
from backend.app.schemas.inventory import (
    InventoryItemRead,
    InventoryParamsUpdate,
    InventorySummary,
)
from backend.app.schemas.common import PaginatedResponse
from backend.app.services.inventory_service import InventoryService
from backend.app.core.deps import require_manager_or_admin
from backend.app.core.errors import NotFoundException

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("/summary", response_model=InventorySummary)
def get_inventory_summary(
    db: Session = Depends(get_db),
):
    """Retrieve aggregate inventory KPIs, stockout counts, and valuation."""
    return InventoryService.get_summary(db)


@router.get("", response_model=PaginatedResponse[InventoryItemRead])
def list_inventory(
    search: Optional[str] = None,
    category_id: Optional[str] = None,
    stock_status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """List current inventory items with status, stock levels, and days of cover."""
    items, total = InventoryService.list_inventory(
        db=db,
        search=search,
        category_id=category_id,
        stock_status=stock_status,
        page=page,
        page_size=page_size,
    )
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    return PaginatedResponse(
        data=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{medicine_id}", response_model=InventoryItemRead)
def get_inventory_item(
    medicine_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve detailed inventory tracking for a single medicine."""
    item = InventoryService.get_by_medicine_id(db, medicine_id)
    if not item:
        raise NotFoundException("Inventory record for medicine", medicine_id)
    return item


@router.patch("/{medicine_id}/parameters", response_model=InventoryItemRead)
def update_inventory_parameters(
    medicine_id: str,
    payload: InventoryParamsUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_manager_or_admin),
):
    """Manager/Admin: Update replenishment thresholds (reorder point, safety stock, MOQ, order-up-to level)."""
    return InventoryService.update_parameters(
        db=db,
        medicine_id=medicine_id,
        params=payload,
        user_name=user.name or user.email,
    )
