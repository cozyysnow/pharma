from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from backend.app.db.models.inventory import InventoryCurrent
from backend.app.db.models.medicine import Medicine
from backend.app.db.models.audit_log import AuditLog
from backend.app.schemas.inventory import InventoryParamsUpdate, InventorySummary
from backend.app.core.errors import NotFoundException
import json


class InventoryService:
    @staticmethod
    def list_inventory(
        db: Session,
        search: Optional[str] = None,
        category_id: Optional[str] = None,
        stock_status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[InventoryCurrent], int]:
        q = db.query(InventoryCurrent).join(Medicine).options(
            joinedload(InventoryCurrent.medicine).joinedload(Medicine.category),
            joinedload(InventoryCurrent.medicine).joinedload(Medicine.primary_supplier),
        )

        if search:
            search_fmt = f"%{search.lower()}%"
            q = q.filter(
                (Medicine.medicine_id.ilike(search_fmt))
                | (Medicine.display_name.ilike(search_fmt))
                | (Medicine.generic_name.ilike(search_fmt))
            )

        if category_id:
            q = q.filter(Medicine.category_id == category_id)

        if stock_status:
            q = q.filter(InventoryCurrent.stock_status == stock_status)

        total = q.count()
        skip = (page - 1) * page_size
        items = q.offset(skip).limit(page_size).all()
        return items, total

    @staticmethod
    def get_by_medicine_id(db: Session, medicine_id: str) -> Optional[InventoryCurrent]:
        return (
            db.query(InventoryCurrent)
            .options(
                joinedload(InventoryCurrent.medicine).joinedload(Medicine.category),
                joinedload(InventoryCurrent.medicine).joinedload(Medicine.primary_supplier),
            )
            .filter(InventoryCurrent.medicine_id == medicine_id)
            .first()
        )

    @staticmethod
    def update_parameters(
        db: Session,
        medicine_id: str,
        params: InventoryParamsUpdate,
        user_name: str = "Admin",
    ) -> InventoryCurrent:
        inv = db.query(InventoryCurrent).filter(InventoryCurrent.medicine_id == medicine_id).first()
        if not inv:
            raise NotFoundException("Inventory record for medicine", medicine_id)

        update_data = params.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(inv, field, value)

        # Audit log parameter update
        audit = AuditLog(
            user_id=user_name,
            action="UPDATE_INVENTORY_PARAMETERS",
            entity_type="INVENTORY",
            entity_id=medicine_id,
            details_json=json.dumps(update_data),
        )
        db.add(audit)

        db.commit()
        db.refresh(inv)
        return inv

    @staticmethod
    def get_summary(db: Session) -> InventorySummary:
        items = (
            db.query(InventoryCurrent)
            .options(joinedload(InventoryCurrent.medicine))
            .all()
        )
        total_skus = len(items)
        total_units = sum(i.closing_stock for i in items)
        stockout_count = sum(1 for i in items if i.closing_stock <= 0)
        low_stock_count = sum(1 for i in items if 0 < i.closing_stock <= i.reorder_point)
        adequate_count = sum(1 for i in items if i.reorder_point < i.closing_stock <= i.order_up_to_level)
        overstocked_count = sum(1 for i in items if i.closing_stock > i.order_up_to_level)

        total_cost = sum(i.closing_stock * (i.medicine.unit_cost_inr if i.medicine else 0.0) for i in items)
        total_retail = sum(i.closing_stock * (i.medicine.unit_price_inr if i.medicine else 0.0) for i in items)

        return InventorySummary(
            total_skus=total_skus,
            total_units_in_stock=total_units,
            stockout_count=stockout_count,
            low_stock_count=low_stock_count,
            adequate_stock_count=adequate_count,
            overstocked_count=overstocked_count,
            total_stock_value_cost_inr=round(total_cost, 2),
            total_stock_value_retail_inr=round(total_retail, 2),
        )
