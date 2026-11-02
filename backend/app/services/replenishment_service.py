import math
import uuid
import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.db.models.replenishment import ReplenishmentRecommendation
from backend.app.db.models.medicine import Medicine
from backend.app.db.models.inventory import InventoryCurrent
from backend.app.db.models.supplier import Supplier
from backend.app.db.models.risk import RiskResult
from backend.app.core.logging import logger
from backend.app.core.errors import AppException


class ReplenishmentService:
    """Computes replenishment recommendations strictly conforming to Section 16,
    enforcing human-in-the-loop workflow transitions without autonomous ordering."""

    @staticmethod
    def generate_recommendations(db: Session) -> Dict[str, int]:
        """Evaluates inventory positions and generates/refreshes pending recommendations."""
        now = datetime.datetime.utcnow()
        medicines = db.query(Medicine).filter(Medicine.is_active == True).all()

        created = 0
        updated = 0
        auto_cleared = 0

        for med in medicines:
            med_id = med.medicine_id
            inv = db.query(InventoryCurrent).filter(InventoryCurrent.medicine_id == med_id).first()
            if not inv:
                continue

            sup = med.primary_supplier
            risk = db.query(RiskResult).filter(RiskResult.medicine_id == med_id).first()

            current_stock = inv.closing_stock
            open_orders = inv.on_order_units
            inventory_position = current_stock + open_orders

            # Required stock from risk calculation or fallback
            required_stock = risk.required_stock if risk else int(inv.reorder_point + inv.safety_stock)
            lead_time_days = float(sup.lead_time_mean_days if sup else 5.0)
            days_of_cover = float(inv.days_of_cover if inv.days_of_cover is not None else 0.0)

            raw_need = required_stock - inventory_position

            existing_pending = (
                db.query(ReplenishmentRecommendation)
                .filter(
                    ReplenishmentRecommendation.medicine_id == med_id,
                    ReplenishmentRecommendation.status == "PENDING",
                )
                .first()
            )

            if raw_need <= 0:
                # Stock position is sufficient — clear any lingering pending recommendation
                if existing_pending:
                    existing_pending.status = "DISMISSED"
                    existing_pending.dismissed_at = now
                    existing_pending.dismissed_by = "System Auto-Resolution"
                    existing_pending.dismiss_reason = "Inventory position regained sufficiency."
                    auto_cleared += 1
                continue

            # Need exists: apply MOQ
            moq = int(inv.moq if inv.moq and inv.moq > 0 else 1)
            order_qty = max(raw_need, moq)
            order_qty = int(math.ceil(order_qty))

            # Urgency check (days of cover < lead time or stockout)
            is_urgent = (current_stock <= 0) or (days_of_cover < lead_time_days)

            if existing_pending:
                existing_pending.current_stock = current_stock
                existing_pending.open_order_qty = open_orders
                existing_pending.required_stock = required_stock
                existing_pending.lead_time_days = lead_time_days
                existing_pending.moq_applied = moq
                existing_pending.recommended_order_quantity = order_qty
                existing_pending.is_urgent = is_urgent
                updated += 1
            else:
                rec = ReplenishmentRecommendation(
                    recommendation_id=f"REC_{med_id}_{uuid.uuid4().hex[:6]}",
                    medicine_id=med_id,
                    supplier_id=med.primary_supplier_id,
                    current_stock=current_stock,
                    open_order_qty=open_orders,
                    required_stock=required_stock,
                    lead_time_days=lead_time_days,
                    moq_applied=moq,
                    recommended_order_quantity=order_qty,
                    is_urgent=is_urgent,
                    status="PENDING",
                    created_at=now,
                )
                db.add(rec)
                created += 1

        db.commit()
        logger.info(
            "Replenishment generation completed: created=%d, updated=%d, cleared=%d",
            created,
            updated,
            auto_cleared,
        )
        return {"created": created, "updated": updated, "cleared": auto_cleared}

    @staticmethod
    def list_recommendations(
        db: Session,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        query = db.query(ReplenishmentRecommendation).join(
            Medicine, ReplenishmentRecommendation.medicine_id == Medicine.medicine_id
        )
        if status:
            query = query.filter(ReplenishmentRecommendation.status == status)

        # Order by urgent first, then creation date desc
        recs = query.order_by(
            ReplenishmentRecommendation.is_urgent.desc(),
            desc(ReplenishmentRecommendation.created_at),
        ).all()

        results = []
        for r in recs:
            med = r.medicine
            sup = r.supplier or (med.primary_supplier if med else None)
            unit_cost = float(med.unit_cost_inr if med else 0.0)
            est_cost = round(r.recommended_order_quantity * unit_cost, 2)
            urgency_level = "CRITICAL" if r.is_urgent else "MEDIUM"
            rationale = (
                f"Deficit of {max(0, r.required_stock - (r.current_stock + r.open_order_qty))} units "
                f"below required buffer. MOQ {r.moq_applied} applied."
            )

            results.append({
                "id": r.recommendation_id,
                "recommendation_id": r.recommendation_id,
                "medicine_id": r.medicine_id,
                "supplier_id": r.supplier_id,
                "current_stock": r.current_stock,
                "open_order_qty": r.open_order_qty,
                "required_stock": r.required_stock,
                "lead_time_days": r.lead_time_days,
                "moq_applied": r.moq_applied,
                "recommended_order_quantity": r.recommended_order_quantity,
                "recommended_quantity": r.recommended_order_quantity,
                "estimated_cost_inr": est_cost,
                "urgency_level": urgency_level,
                "is_urgent": r.is_urgent,
                "reorder_point": med.inventory.reorder_point if med and med.inventory else 100,
                "days_of_cover": med.inventory.days_of_cover if med and med.inventory else 0.0,
                "rationale": rationale,
                "status": r.status,
                "created_at": r.created_at,
                "generated_at": r.created_at,
                "accepted_at": r.accepted_at,
                "ordered_at": r.ordered_at,
                "dismissed_at": r.dismissed_at,
                "accepted_by": r.accepted_by,
                "dismissed_by": r.dismissed_by,
                "dismiss_reason": r.dismiss_reason,
                "po_reference": r.po_reference,
                "medicine": med,
                "supplier": sup,
            })

        return results

    @staticmethod
    def accept(db: Session, recommendation_id: str, by: Optional[str] = None) -> Dict[str, Any]:
        """Transitions PENDING -> ACCEPTED."""
        rec = (
            db.query(ReplenishmentRecommendation)
            .filter(ReplenishmentRecommendation.recommendation_id == recommendation_id)
            .first()
        )
        if not rec:
            raise AppException(f"Recommendation {recommendation_id} not found", "NOT_FOUND", 404)
        if rec.status != "PENDING":
            raise AppException(
                f"Cannot accept recommendation with status '{rec.status}' (must be PENDING)",
                "INVALID_STATE",
                400,
            )

        now = datetime.datetime.utcnow()
        rec.status = "ACCEPTED"
        rec.accepted_at = now
        rec.accepted_by = by or "Authorized Manager"
        db.commit()
        db.refresh(rec)
        return ReplenishmentService._serialize(rec)

    @staticmethod
    def order_placed(db: Session, recommendation_id: str, po_ref: Optional[str] = None) -> Dict[str, Any]:
        """Transitions ACCEPTED -> ORDERED.
        Crucial: Updates open_order_qty (on_order_units) on inventory_current."""
        rec = (
            db.query(ReplenishmentRecommendation)
            .filter(ReplenishmentRecommendation.recommendation_id == recommendation_id)
            .first()
        )
        if not rec:
            raise AppException(f"Recommendation {recommendation_id} not found", "NOT_FOUND", 404)
        if rec.status not in ("PENDING", "ACCEPTED"):
            raise AppException(
                f"Cannot mark order placed on recommendation with status '{rec.status}'",
                "INVALID_STATE",
                400,
            )

        now = datetime.datetime.utcnow()
        rec.status = "ORDERED"
        rec.ordered_at = now
        rec.po_reference = po_ref

        # Update physical on_order_units on inventory position
        inv = db.query(InventoryCurrent).filter(InventoryCurrent.medicine_id == rec.medicine_id).first()
        if inv:
            inv.on_order_units += rec.recommended_order_quantity
            inv.updated_at = now

        db.commit()
        db.refresh(rec)
        logger.info(
            "Marked recommendation %s as ORDERED. Incremented on_order_units by %d for %s.",
            rec.recommendation_id,
            rec.recommended_order_quantity,
            rec.medicine_id,
        )
        return ReplenishmentService._serialize(rec)

    @staticmethod
    def dismiss(
        db: Session,
        recommendation_id: str,
        reason: str,
        by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Transitions PENDING -> DISMISSED with human rationale."""
        rec = (
            db.query(ReplenishmentRecommendation)
            .filter(ReplenishmentRecommendation.recommendation_id == recommendation_id)
            .first()
        )
        if not rec:
            raise AppException(f"Recommendation {recommendation_id} not found", "NOT_FOUND", 404)
        if rec.status != "PENDING":
            raise AppException(
                f"Cannot dismiss recommendation with status '{rec.status}' (must be PENDING)",
                "INVALID_STATE",
                400,
            )

        now = datetime.datetime.utcnow()
        rec.status = "DISMISSED"
        rec.dismissed_at = now
        rec.dismissed_by = by or "Authorized Manager"
        rec.dismiss_reason = reason
        db.commit()
        db.refresh(rec)
        return ReplenishmentService._serialize(rec)

    @staticmethod
    def _serialize(r: ReplenishmentRecommendation) -> Dict[str, Any]:
        med = r.medicine
        sup = r.supplier or (med.primary_supplier if med else None)
        unit_cost = float(med.unit_cost_inr if med else 0.0)
        return {
            "id": r.recommendation_id,
            "recommendation_id": r.recommendation_id,
            "medicine_id": r.medicine_id,
            "supplier_id": r.supplier_id,
            "current_stock": r.current_stock,
            "open_order_qty": r.open_order_qty,
            "required_stock": r.required_stock,
            "lead_time_days": r.lead_time_days,
            "moq_applied": r.moq_applied,
            "recommended_order_quantity": r.recommended_order_quantity,
            "recommended_quantity": r.recommended_order_quantity,
            "estimated_cost_inr": round(r.recommended_order_quantity * unit_cost, 2),
            "urgency_level": "CRITICAL" if r.is_urgent else "MEDIUM",
            "is_urgent": r.is_urgent,
            "reorder_point": med.inventory.reorder_point if med and med.inventory else 100,
            "days_of_cover": med.inventory.days_of_cover if med and med.inventory else 0.0,
            "rationale": f"Procurement required. Shortfall: {max(0, r.required_stock - (r.current_stock + r.open_order_qty))} units.",
            "status": r.status,
            "created_at": r.created_at,
            "generated_at": r.created_at,
            "accepted_at": r.accepted_at,
            "ordered_at": r.ordered_at,
            "dismissed_at": r.dismissed_at,
            "accepted_by": r.accepted_by,
            "dismissed_by": r.dismissed_by,
            "dismiss_reason": r.dismiss_reason,
            "po_reference": r.po_reference,
            "medicine": med,
            "supplier": sup,
        }
