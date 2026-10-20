from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.db.models.user import User
from backend.app.schemas.supplier import SupplierRead, SupplierCreate, SupplierUpdate
from backend.app.schemas.medicine import MedicineRead
from backend.app.services.supplier_service import SupplierService
from backend.app.core.deps import require_manager_or_admin, require_admin
from backend.app.core.errors import NotFoundException

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@router.get("", response_model=List[SupplierRead])
def get_suppliers(
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
):
    """List all authorized distributors and wholesalers."""
    return SupplierService.list_all(db, is_active=is_active)


@router.get("/{supplier_id}", response_model=SupplierRead)
def get_supplier(supplier_id: str, db: Session = Depends(get_db)):
    """Retrieve detailed logistics profile of a supplier."""
    sup = SupplierService.get_by_id(db, supplier_id)
    if not sup:
        raise NotFoundException("Supplier", supplier_id)
    return sup


@router.get("/{supplier_id}/medicines", response_model=List[MedicineRead])
def get_supplier_medicines(supplier_id: str, db: Session = Depends(get_db)):
    """List all medicines primarily supplied by this vendor."""
    return SupplierService.get_medicines_by_supplier(db, supplier_id)


@router.post("", response_model=SupplierRead, status_code=status.HTTP_201_CREATED)
def create_supplier(
    payload: SupplierCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_manager_or_admin),
):
    """Manager/Admin: Register a new supplier."""
    return SupplierService.create(db, payload)


@router.patch("/{supplier_id}", response_model=SupplierRead)
def update_supplier(
    supplier_id: str,
    payload: SupplierUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_manager_or_admin),
):
    """Manager/Admin: Update supplier logistics parameters."""
    return SupplierService.update(db, supplier_id, payload)


@router.post("/{supplier_id}/deactivate", response_model=SupplierRead)
def deactivate_supplier(
    supplier_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    """Admin-only: Deactivate a supplier."""
    return SupplierService.deactivate(db, supplier_id)
