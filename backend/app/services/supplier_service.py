from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.db.models.supplier import Supplier
from backend.app.db.models.medicine import Medicine
from backend.app.schemas.supplier import SupplierCreate, SupplierUpdate
from backend.app.core.errors import ConflictException, NotFoundException


class SupplierService:
    @staticmethod
    def list_all(db: Session, is_active: Optional[bool] = None) -> List[Supplier]:
        q = db.query(Supplier)
        if is_active is not None:
            q = q.filter(Supplier.is_active == is_active)
        return q.order_by(Supplier.supplier_id).all()

    @staticmethod
    def get_by_id(db: Session, supplier_id: str) -> Optional[Supplier]:
        return db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()

    @staticmethod
    def create(db: Session, sup_in: SupplierCreate) -> Supplier:
        existing = SupplierService.get_by_id(db, sup_in.supplier_id)
        if existing:
            raise ConflictException(f"Supplier with ID '{sup_in.supplier_id}' already exists.")
        sup = Supplier(**sup_in.model_dump())
        db.add(sup)
        db.commit()
        db.refresh(sup)
        return sup

    @staticmethod
    def update(db: Session, supplier_id: str, sup_in: SupplierUpdate) -> Supplier:
        sup = SupplierService.get_by_id(db, supplier_id)
        if not sup:
            raise NotFoundException("Supplier", supplier_id)
        for field, value in sup_in.model_dump(exclude_unset=True).items():
            setattr(sup, field, value)
        db.commit()
        db.refresh(sup)
        return sup

    @staticmethod
    def deactivate(db: Session, supplier_id: str) -> Supplier:
        sup = SupplierService.get_by_id(db, supplier_id)
        if not sup:
            raise NotFoundException("Supplier", supplier_id)
        sup.is_active = False
        db.commit()
        db.refresh(sup)
        return sup

    @staticmethod
    def get_medicines_by_supplier(db: Session, supplier_id: str) -> List[Medicine]:
        return db.query(Medicine).filter(Medicine.primary_supplier_id == supplier_id).all()
