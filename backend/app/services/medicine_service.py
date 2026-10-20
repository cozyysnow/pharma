from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from backend.app.db.models.medicine import Medicine
from backend.app.db.models.inventory import InventoryCurrent
from backend.app.schemas.medicine import MedicineCreate, MedicineUpdate
from backend.app.core.errors import ConflictException, NotFoundException


class MedicineService:
    @staticmethod
    def list_medicines(
        db: Session,
        search: Optional[str] = None,
        category_id: Optional[str] = None,
        supplier_id: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "medicine_id",
        sort_dir: str = "asc",
    ) -> Tuple[List[Medicine], int]:
        q = db.query(Medicine).options(
            joinedload(Medicine.category),
            joinedload(Medicine.primary_supplier),
        )

        if search:
            search_fmt = f"%{search.lower()}%"
            q = q.filter(
                or_(
                    Medicine.medicine_id.ilike(search_fmt),
                    Medicine.display_name.ilike(search_fmt),
                    Medicine.generic_name.ilike(search_fmt),
                )
            )

        if category_id:
            q = q.filter(Medicine.category_id == category_id)

        if supplier_id:
            q = q.filter(Medicine.primary_supplier_id == supplier_id)

        if is_active is not None:
            q = q.filter(Medicine.is_active == is_active)

        total = q.count()

        # Sorting
        sort_col = getattr(Medicine, sort_by, Medicine.medicine_id)
        if sort_dir.lower() == "desc":
            q = q.order_by(sort_col.desc())
        else:
            q = q.order_by(sort_col.asc())

        skip = (page - 1) * page_size
        items = q.offset(skip).limit(page_size).all()
        return items, total

    @staticmethod
    def get_by_id(db: Session, medicine_id: str) -> Optional[Medicine]:
        return (
            db.query(Medicine)
            .options(
                joinedload(Medicine.category),
                joinedload(Medicine.primary_supplier),
            )
            .filter(Medicine.medicine_id == medicine_id)
            .first()
        )

    @staticmethod
    def create(db: Session, med_in: MedicineCreate) -> Medicine:
        existing = MedicineService.get_by_id(db, med_in.medicine_id)
        if existing:
            raise ConflictException(f"Medicine with ID '{med_in.medicine_id}' already exists.")

        med = Medicine(**med_in.model_dump())
        db.add(med)

        # Automatically initialize current inventory record
        inv = InventoryCurrent(
            medicine_id=med.medicine_id,
            opening_stock=0,
            closing_stock=0,
            reorder_point=100,
            safety_stock=50,
            moq=50,
            days_of_cover=0.0,
            stock_status="OUT_OF_STOCK",
        )
        db.add(inv)

        db.commit()
        db.refresh(med)
        return med

    @staticmethod
    def update(db: Session, medicine_id: str, med_in: MedicineUpdate) -> Medicine:
        med = MedicineService.get_by_id(db, medicine_id)
        if not med:
            raise NotFoundException("Medicine", medicine_id)

        for field, value in med_in.model_dump(exclude_unset=True).items():
            setattr(med, field, value)

        db.commit()
        db.refresh(med)
        return med

    @staticmethod
    def deactivate(db: Session, medicine_id: str) -> Medicine:
        med = MedicineService.get_by_id(db, medicine_id)
        if not med:
            raise NotFoundException("Medicine", medicine_id)
        med.is_active = False
        db.commit()
        db.refresh(med)
        return med
