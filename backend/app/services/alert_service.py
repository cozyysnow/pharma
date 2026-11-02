import datetime
import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.db.models.alert import Alert
from backend.app.db.models.medicine import Medicine
from backend.app.db.models.inventory import InventoryCurrent
from backend.app.db.models.risk import RiskResult
from backend.app.db.models.replenishment import ReplenishmentRecommendation
from backend.app.core.logging import logger


class AlertEngine:
    """Evaluates rules across inventory, risk, and replenishment, handling deduplication and auto-resolution."""

    @staticmethod
    def evaluate_system_alerts(db: Session) -> Dict[str, int]:
        """Runs the rule engine against all active medicines."""
        now = datetime.datetime.utcnow()
        medicines = db.query(Medicine).filter(Medicine.is_active == True).all()

        created_count = 0
        updated_count = 0
        resolved_count = 0

        for med in medicines:
            med_id = med.medicine_id
            inv = db.query(InventoryCurrent).filter(InventoryCurrent.medicine_id == med_id).first()
            risk = db.query(RiskResult).filter(RiskResult.medicine_id == med_id).first()
            rec = (
                db.query(ReplenishmentRecommendation)
                .filter(ReplenishmentRecommendation.medicine_id == med_id, ReplenishmentRecommendation.status == "PENDING")
                .first()
            )

            # Conditions map: alert_type -> (condition_active: bool, severity: str, title: str, message: str)
            active_rules: Dict[str, tuple[bool, str, str, str]] = {}

            # 1. HIGH_RISK
            if risk and risk.risk_level in ("HIGH", "CRITICAL"):
                sev = "CRITICAL"
                title = f"High Stock-Out Vulnerability: {med.display_name}"
                msg = (
                    f"{risk.risk_level} risk score of {risk.risk_score}/100. "
                    f"Current stock of {inv.closing_stock if inv else 0} covers only {risk.stock_coverage_days:.1f} days "
                    f"against supplier lead time of {risk.lead_time_days:.1f} days."
                )
                active_rules["HIGH_RISK"] = (True, sev, title, msg)
            else:
                active_rules["HIGH_RISK"] = (False, "", "", "")

            # 2. LOW_STOCK
            if inv and (inv.closing_stock <= 0 or inv.closing_stock <= inv.reorder_point):
                sev = "CRITICAL" if inv.closing_stock <= 0 else "WARNING"
                title = f"Stock Depletion: {med.display_name}"
                if inv.closing_stock <= 0:
                    msg = f"Zero units on hand (Out of Stock). Immediate emergency restocking required."
                else:
                    msg = f"Closing stock of {inv.closing_stock} units is below reorder point of {inv.reorder_point}."
                active_rules["LOW_STOCK"] = (True, sev, title, msg)
            else:
                active_rules["LOW_STOCK"] = (False, "", "", "")

            # 3. REPLENISHMENT_REQUIRED
            if rec:
                sev = "CRITICAL" if rec.is_urgent else "WARNING"
                title = f"Replenishment Action Required: {med.display_name}"
                msg = (
                    f"Pending procurement order of {rec.recommended_order_quantity} units required. "
                    f"Current position: {rec.current_stock} on hand, {rec.open_order_qty} on order."
                )
                active_rules["REPLENISHMENT_REQUIRED"] = (True, sev, title, msg)
            else:
                active_rules["REPLENISHMENT_REQUIRED"] = (False, "", "", "")

            # 4. DEMAND_SPIKE
            if inv and inv.expected_daily_demand > 25.0 and risk and risk.expected_daily_demand > 25.0:
                # Flag if projected rate is elevated
                active_rules["DEMAND_SPIKE"] = (
                    True,
                    "WARNING",
                    f"Elevated Demand Pace: {med.display_name}",
                    f"Projected daily consumption is {risk.expected_daily_demand:.1f} units/day.",
                )
            else:
                active_rules["DEMAND_SPIKE"] = (False, "", "", "")

            # Process each alert type with dedup & auto-resolve
            for alert_type, (is_active, severity, title, message) in active_rules.items():
                open_alert = (
                    db.query(Alert)
                    .filter(
                        Alert.medicine_id == med_id,
                        Alert.alert_type == alert_type,
                        Alert.status.in_(["UNREAD", "ACKNOWLEDGED"]),
                    )
                    .first()
                )

                if is_active:
                    if open_alert:
                        # Deduplicate by updating existing open alert
                        open_alert.title = title
                        open_alert.message = message
                        open_alert.severity = severity
                        updated_count += 1
                    else:
                        new_alert = Alert(
                            alert_id=f"ALT_{med_id}_{alert_type}_{uuid.uuid4().hex[:4]}",
                            medicine_id=med_id,
                            alert_type=alert_type,
                            severity=severity,
                            title=title,
                            message=message,
                            status="UNREAD",
                            created_at=now,
                        )
                        db.add(new_alert)
                        created_count += 1
                else:
                    # Auto-resolve condition if it cleared
                    if open_alert:
                        open_alert.status = "RESOLVED"
                        open_alert.resolved_at = now
                        open_alert.resolved_by = "System Auto-Resolve"
                        resolved_count += 1

        db.commit()
        logger.info(
            "Alert evaluation finished: created=%d, updated=%d, auto-resolved=%d",
            created_count,
            updated_count,
            resolved_count,
        )
        return {"created": created_count, "updated": updated_count, "resolved": resolved_count}


class AlertService:
    """Provides querying and state transitions for user notifications."""

    @staticmethod
    def list_alerts(
        db: Session,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        alert_type: Optional[str] = None,
        medicine_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        query = db.query(Alert).join(Medicine, Alert.medicine_id == Medicine.medicine_id)

        if status:
            query = query.filter(Alert.status == status)
        if severity:
            query = query.filter(Alert.severity == severity)
        if alert_type:
            query = query.filter(Alert.alert_type == alert_type)
        if medicine_id:
            query = query.filter(Alert.medicine_id == medicine_id)

        alerts = query.order_by(desc(Alert.created_at)).all()

        return [
            {
                "id": a.alert_id,
                "alert_id": a.alert_id,
                "medicine_id": a.medicine_id,
                "alert_type": a.alert_type,
                "severity": a.severity,
                "title": a.title,
                "message": a.message,
                "status": a.status,
                "created_at": a.created_at,
                "acknowledged_at": a.acknowledged_at,
                "resolved_at": a.resolved_at,
                "acknowledged_by": a.acknowledged_by,
                "resolved_by": a.resolved_by,
                "medicine": a.medicine,
            }
            for a in alerts
        ]

    @staticmethod
    def get_unread_count(db: Session) -> int:
        return db.query(Alert).filter(Alert.status == "UNREAD").count()

    @staticmethod
    def acknowledge(db: Session, alert_id: str, by: Optional[str] = None) -> Optional[Dict[str, Any]]:
        alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
        if not alert:
            return None
        alert.status = "ACKNOWLEDGED"
        alert.acknowledged_at = datetime.datetime.utcnow()
        alert.acknowledged_by = by or "Authorized Staff"
        db.commit()
        db.refresh(alert)
        return {
            "id": alert.alert_id,
            "alert_id": alert.alert_id,
            "medicine_id": alert.medicine_id,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "title": alert.title,
            "message": alert.message,
            "status": alert.status,
            "created_at": alert.created_at,
            "acknowledged_at": alert.acknowledged_at,
            "acknowledged_by": alert.acknowledged_by,
            "medicine": alert.medicine,
        }

    @staticmethod
    def resolve(db: Session, alert_id: str, by: Optional[str] = None) -> Optional[Dict[str, Any]]:
        alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
        if not alert:
            return None
        alert.status = "RESOLVED"
        alert.resolved_at = datetime.datetime.utcnow()
        alert.resolved_by = by or "Authorized Staff"
        db.commit()
        db.refresh(alert)
        return {
            "id": alert.alert_id,
            "alert_id": alert.alert_id,
            "medicine_id": alert.medicine_id,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "title": alert.title,
            "message": alert.message,
            "status": alert.status,
            "created_at": alert.created_at,
            "resolved_at": alert.resolved_at,
            "resolved_by": alert.resolved_by,
            "medicine": alert.medicine,
        }

    @staticmethod
    def dismiss(db: Session, alert_id: str) -> Optional[Dict[str, Any]]:
        alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
        if not alert:
            return None
        alert.status = "DISMISSED"
        db.commit()
        db.refresh(alert)
        return {
            "id": alert.alert_id,
            "alert_id": alert.alert_id,
            "medicine_id": alert.medicine_id,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "title": alert.title,
            "message": alert.message,
            "status": alert.status,
            "created_at": alert.created_at,
            "medicine": alert.medicine,
        }

    @staticmethod
    def bulk_acknowledge(db: Session, ids: List[str], by: Optional[str] = None) -> int:
        now = datetime.datetime.utcnow()
        user_name = by or "Authorized Staff"
        count = (
            db.query(Alert)
            .filter(Alert.alert_id.in_(ids), Alert.status == "UNREAD")
            .update(
                {"status": "ACKNOWLEDGED", "acknowledged_at": now, "acknowledged_by": user_name},
                synchronize_session=False,
            )
        )
        db.commit()
        return count

