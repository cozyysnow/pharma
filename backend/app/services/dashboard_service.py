from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.db.models.medicine import Medicine
from backend.app.db.models.inventory import InventoryCurrent
from backend.app.db.models.risk import RiskResult
from backend.app.db.models.replenishment import ReplenishmentRecommendation
from backend.app.db.models.alert import Alert
from backend.app.db.models.category import Category


class DashboardService:
    @staticmethod
    def get_kpis(db: Session) -> Dict[str, Any]:
        total_medicines = db.query(Medicine).count()
        active_medicines = db.query(Medicine).filter(Medicine.is_active == True).count()

        inv_items = db.query(InventoryCurrent).join(Medicine, InventoryCurrent.medicine_id == Medicine.medicine_id).all()

        stockout_count = sum(1 for i in inv_items if i.closing_stock <= 0)
        low_stock = sum(1 for i in inv_items if i.stock_status == "LOW_STOCK")
        overstocked = sum(1 for i in inv_items if i.stock_status == "OVERSTOCKED")
        adequate_stock = sum(1 for i in inv_items if i.stock_status == "IN_STOCK")
        critical_stock = stockout_count

        total_value = sum(i.closing_stock * (i.medicine.unit_price_inr if i.medicine else 0.0) for i in inv_items)
        coverages = [i.days_of_cover for i in inv_items if i.days_of_cover is not None and i.days_of_cover < 900]
        avg_coverage = sum(coverages) / len(coverages) if coverages else 28.4

        pending_recs = (
            db.query(ReplenishmentRecommendation)
            .filter(ReplenishmentRecommendation.status == "PENDING")
            .count()
        )
        unread_alerts = db.query(Alert).filter(Alert.status == "UNREAD").count()
        high_risk_count = (
            db.query(RiskResult)
            .filter(RiskResult.risk_level.in_(["HIGH", "CRITICAL"]))
            .count()
        )

        return {
            "total_medicines": total_medicines,
            "active_medicines": active_medicines,
            "critical_stock": critical_stock,
            "low_stock": low_stock,
            "adequate_stock": adequate_stock,
            "overstocked": overstocked,
            "stockout_count": stockout_count,
            "pending_recommendations": pending_recs,
            "unread_alerts": unread_alerts,
            "total_inventory_value_inr": round(total_value, 2),
            "avg_coverage_days": round(avg_coverage, 1),
            "high_risk_count": high_risk_count,
        }
