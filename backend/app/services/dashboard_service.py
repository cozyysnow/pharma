import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from backend.app.db.models.medicine import Medicine
from backend.app.db.models.inventory import InventoryCurrent
from backend.app.db.models.risk import RiskResult
from backend.app.db.models.replenishment import ReplenishmentRecommendation
from backend.app.db.models.alert import Alert
from backend.app.db.models.category import Category
from backend.app.db.models.daily_record import DailyRecord


class DashboardService:
    @staticmethod
    def get_summary(db: Session) -> Dict[str, Any]:
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

        # Risk distribution
        risk_results = db.query(RiskResult).all()
        risk_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for r in risk_results:
            lvl = r.risk_level
            risk_counts[lvl] = risk_counts.get(lvl, 0) + 1

        # Category distribution
        categories = db.query(Category).all()
        category_dist = []
        for cat in categories:
            med_ids = [m.medicine_id for m in cat.medicines]
            cat_inv = [i for i in inv_items if i.medicine_id in med_ids]
            val = sum(i.closing_stock * (i.medicine.unit_price_inr if i.medicine else 0.0) for i in cat_inv)
            category_dist.append({
                "category_id": cat.category_id,
                "category_name": cat.category_name,
                "short_name": cat.category_name.split()[0],
                "medicine_count": len(med_ids),
                "total_stock_value": round(val, 2),
            })

        # 14-day demand trend from daily_records
        trend_rows = (
            db.query(DailyRecord.date, func.sum(DailyRecord.units_demanded))
            .filter(DailyRecord.date >= "2025-12-18")
            .group_by(DailyRecord.date)
            .order_by(DailyRecord.date.asc())
            .all()
        )
        demand_trend = [
            {"date": r[0].isoformat()[5:] if hasattr(r[0], 'isoformat') else str(r[0])[5:], "actualDemand": int(r[1])}
            for r in trend_rows
        ]

        kpis = {
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
            "high_risk_count": risk_counts.get("HIGH", 0) + risk_counts.get("CRITICAL", 0),
        }

        return {
            **kpis,
            "kpis": kpis,
            "risk_distribution": risk_counts,
            "category_distribution": category_dist,
            "demand_trend": demand_trend,
        }
