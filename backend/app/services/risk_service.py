import math
import json
import uuid
import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.db.models.medicine import Medicine
from backend.app.db.models.inventory import InventoryCurrent
from backend.app.db.models.supplier import Supplier
from backend.app.db.models.forecast import Forecast
from backend.app.db.models.risk import RiskResult
from backend.app.core.logging import logger


class RiskCalculator:
    """Computes deterministic stock-out risk, stock coverage, lead-time demand,
    and required stock conforming strictly to req.md Sections 14 and 15."""

    @staticmethod
    def calculate_medicine_risk(
        medicine: Medicine,
        inventory: InventoryCurrent,
        supplier: Optional[Supplier],
        forecast_points: List[Forecast],
    ) -> Dict[str, Any]:
        """Calculates risk parameters for a single medicine."""
        current_stock = int(inventory.closing_stock if inventory else 0)
        open_orders = int(inventory.on_order_units if inventory else 0)
        safety_stock = int(inventory.safety_stock if inventory and inventory.safety_stock > 0 else 50)
        reorder_point = int(inventory.reorder_point if inventory and inventory.reorder_point > 0 else 100)

        # Lead time days L
        lt_mean = float(supplier.lead_time_mean_days if supplier and supplier.lead_time_mean_days else 5.0)
        lead_time_days = float(max(1.0, lt_mean))
        L_int = max(1, int(math.ceil(lead_time_days)))

        # Forecast points ordered chronologically
        sorted_forecasts = sorted(forecast_points, key=lambda f: f.forecast_date)
        d_hat = [float(f.predicted_demand) for f in sorted_forecasts]

        # If no forecasts available, fallback to inventory expected_daily_demand or 10.0
        if not d_hat:
            fallback_demand = float(inventory.expected_daily_demand if inventory and inventory.expected_daily_demand > 0 else 10.0)
            d_hat = [fallback_demand] * 30

        # Lead-time window forecasts
        lead_window = d_hat[:L_int] if len(d_hat) >= L_int else d_hat
        lead_time_demand = float(sum(lead_window))
        expected_daily_demand = float(lead_time_demand / len(lead_window)) if lead_window else 0.0
        avg_next_7d = float(sum(d_hat[:7]) / min(7, len(d_hat))) if d_hat else expected_daily_demand

        # Stock coverage (days)
        if expected_daily_demand > 0:
            stock_coverage_days = float(current_stock / expected_daily_demand)
        else:
            stock_coverage_days = 999.0

        # Days until stockout
        days_until_stockout: Optional[float] = None
        if current_stock <= 0:
            days_until_stockout = 0.0
        else:
            cum_demand = 0.0
            for idx, dem in enumerate(d_hat):
                if cum_demand + dem >= current_stock:
                    rem = current_stock - cum_demand
                    fraction = rem / dem if dem > 0 else 0.0
                    days_until_stockout = float(idx + fraction)
                    break
                cum_demand += dem
            if days_until_stockout is None:
                days_until_stockout = min(999.0, float(stock_coverage_days))

        # Required stock = Lead-Time Demand + Safety Stock
        required_stock = int(round(lead_time_demand + safety_stock))
        inventory_position = current_stock + open_orders
        shortfall = max(0, required_stock - inventory_position)

        # Risk Classification (Section 15.1)
        if current_stock <= 0:
            risk_level = "CRITICAL"
            risk_score = 100
        elif stock_coverage_days <= 2.0 or current_stock < lead_time_demand:
            # Cannot cover demand during lead time
            if stock_coverage_days <= 1.5:
                risk_level = "CRITICAL"
            else:
                risk_level = "HIGH"
            # Score scaled 70 - 99
            risk_score = min(99, max(70, int(round(100.0 * (1.0 - current_stock / max(1.0, float(required_stock)))))))
        elif current_stock < required_stock:
            # Covers lead time but eats into safety stock
            risk_level = "MEDIUM"
            risk_score = min(69, max(30, int(round(100.0 * (1.0 - current_stock / max(1.0, float(required_stock)))))))
        else:
            # Above required stock
            risk_level = "LOW"
            risk_score = max(0, min(29, int(round(30.0 * max(0.0, 1.0 - current_stock / max(1.0, float(required_stock * 1.5)))))))

        # Stockout Probabilities (7d, 14d, 30d)
        def calc_prob(h_days: int) -> float:
            sub = d_hat[:h_days]
            tot_dem = sum(sub)
            if current_stock <= 0:
                return 1.0
            if tot_dem <= 0:
                return 0.0
            if current_stock < tot_dem:
                return round(min(0.99, max(0.50, 0.50 + 0.49 * (tot_dem - current_stock) / tot_dem)), 2)
            else:
                buffer = float(safety_stock)
                return round(max(0.02, min(0.49, 0.49 * (1.0 - (current_stock - tot_dem) / max(1.0, buffer * 2.0)))), 2)

        prob_7d = calc_prob(7)
        prob_14d = calc_prob(14)
        prob_30d = calc_prob(30)

        # Feature Contributions / Factors for Explainability
        cov_weight = min(0.45, max(0.10, (L_int - min(float(L_int), stock_coverage_days)) / float(L_int) * 0.45)) if L_int > 0 else 0.25
        ss_deficit = max(0, required_stock - current_stock)
        ss_weight = min(0.35, max(0.05, (ss_deficit / max(1.0, float(required_stock))) * 0.35))
        sup_rel = float(supplier.on_time_probability if supplier else 0.90)

        factors = [
            {
                "factor": "Stock Coverage vs Lead Time",
                "value": f"{stock_coverage_days:.1f}d / {lead_time_days:.1f}d",
                "contribution": round(cov_weight, 2),
                "explanation": f"On-hand stock provides {stock_coverage_days:.1f} days cover against supplier lead time of {lead_time_days:.1f} days.",
            },
            {
                "factor": "Safety Stock Buffer Deficit",
                "value": f"{current_stock} on hand vs {required_stock} req",
                "contribution": round(ss_weight, 2),
                "explanation": f"Current stock is {'below' if ss_deficit > 0 else 'above'} required threshold (Safety stock: {safety_stock} units).",
            },
            {
                "factor": "Supplier Reliability",
                "value": f"{int(sup_rel * 100)}% on-time",
                "contribution": 0.12,
                "explanation": f"Supplier delivery reliability is {int(sup_rel * 100)}% with lead time variance of ±{supplier.lead_time_sd_days if supplier else 1.0:.1f}d.",
            },
            {
                "factor": "Forecasted Demand Rate",
                "value": f"{expected_daily_demand:.1f} units/day",
                "contribution": 0.08,
                "explanation": f"Projected mean consumption over lead time is {expected_daily_demand:.1f} units per day (7-day avg: {avg_next_7d:.1f}/day).",
            },
        ]

        # Template Explanation (Section 15.3)
        explanation = (
            f"{risk_level} risk: {current_stock} units on hand, but expected demand over the "
            f"{lead_time_days:.0f}-day supplier lead time is {lead_time_demand:.1f} units "
            f"(≈{expected_daily_demand:.1f}/day). Stock would last about {stock_coverage_days:.1f} days. "
            f"Required stock (incl. safety stock of {safety_stock}) is {required_stock}. "
            f"Open orders: {open_orders}."
        )

        return {
            "medicine_id": medicine.medicine_id,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "expected_daily_demand": round(expected_daily_demand, 2),
            "avg_daily_demand": round(avg_next_7d, 2),
            "stock_coverage_days": round(stock_coverage_days, 1),
            "days_of_cover": round(stock_coverage_days, 1),
            "days_until_stockout": round(days_until_stockout, 1) if days_until_stockout is not None else None,
            "lead_time_days": round(lead_time_days, 1),
            "lead_time_demand": round(lead_time_demand, 1),
            "safety_stock": safety_stock,
            "required_stock": required_stock,
            "reorder_point": reorder_point,
            "shortfall": shortfall,
            "current_stock": current_stock,
            "open_order_qty": open_orders,
            "stockout_probability_7d": prob_7d,
            "stockout_probability_14d": prob_14d,
            "stockout_probability_30d": prob_30d,
            "explanation": explanation,
            "factors": factors,
        }


class RiskService:
    """Orchestrates risk runs and queries across the database."""

    @staticmethod
    def run_all(db: Session) -> Dict[str, Any]:
        """Calculates risk for all active medicines and stores in risk_results table."""
        medicines = db.query(Medicine).filter(Medicine.is_active == True).all()
        now = datetime.datetime.utcnow()
        run_id = f"RSK_{now.strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"

        counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}

        for med in medicines:
            inv = db.query(InventoryCurrent).filter(InventoryCurrent.medicine_id == med.medicine_id).first()
            sup = med.primary_supplier
            fcs = db.query(Forecast).filter(Forecast.medicine_id == med.medicine_id).order_by(Forecast.forecast_date.asc()).all()

            calc = RiskCalculator.calculate_medicine_risk(med, inv, sup, fcs)

            level = calc["risk_level"]
            counts[level] = counts.get(level, 0) + 1

            # Update or create RiskResult record
            risk_record = db.query(RiskResult).filter(RiskResult.medicine_id == med.medicine_id).first()
            factors_json = json.dumps({
                "lead_time_demand": calc["lead_time_demand"],
                "shortfall": calc["shortfall"],
                "days_until_stockout": calc["days_until_stockout"],
                "stockout_probability_7d": calc["stockout_probability_7d"],
                "stockout_probability_14d": calc["stockout_probability_14d"],
                "stockout_probability_30d": calc["stockout_probability_30d"],
                "factors": calc["factors"],
            })

            if not risk_record:
                risk_record = RiskResult(
                    risk_id=f"RISK_{med.medicine_id}",
                    medicine_id=med.medicine_id,
                    calculated_at=now,
                    risk_score=calc["risk_score"],
                    risk_level=calc["risk_level"],
                    expected_daily_demand=calc["expected_daily_demand"],
                    stock_coverage_days=calc["stock_coverage_days"],
                    lead_time_days=calc["lead_time_days"],
                    safety_stock=calc["safety_stock"],
                    required_stock=calc["required_stock"],
                    explanation=calc["explanation"],
                    factors_json=factors_json,
                )
                db.add(risk_record)
            else:
                risk_record.calculated_at = now
                risk_record.risk_score = calc["risk_score"]
                risk_record.risk_level = calc["risk_level"]
                risk_record.expected_daily_demand = calc["expected_daily_demand"]
                risk_record.stock_coverage_days = calc["stock_coverage_days"]
                risk_record.lead_time_days = calc["lead_time_days"]
                risk_record.safety_stock = calc["safety_stock"]
                risk_record.required_stock = calc["required_stock"]
                risk_record.explanation = calc["explanation"]
                risk_record.factors_json = factors_json

            # Update inventory_current fields
            if inv:
                inv.days_of_cover = calc["stock_coverage_days"]
                inv.expected_daily_demand = calc["expected_daily_demand"]
                if inv.closing_stock <= 0:
                    inv.stock_status = "OUT_OF_STOCK"
                elif inv.closing_stock <= inv.reorder_point:
                    inv.stock_status = "LOW_STOCK"
                elif inv.closing_stock > inv.order_up_to_level:
                    inv.stock_status = "OVERSTOCKED"
                else:
                    inv.stock_status = "IN_STOCK"
                inv.updated_at = now

        db.commit()
        logger.info("Risk run completed for %d medicines: %s", len(medicines), counts)

        return {
            "run_id": run_id,
            "status": "COMPLETED",
            "medicines_evaluated": len(medicines),
            "high_risk_count": counts.get("HIGH", 0) + counts.get("CRITICAL", 0),
            "medium_risk_count": counts.get("MEDIUM", 0),
            "low_risk_count": counts.get("LOW", 0),
            "computed_at": now,
        }

    @staticmethod
    def get_results(
        db: Session,
        search: Optional[str] = None,
        category_id: Optional[str] = None,
        risk_level: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "risk_score",
        sort_dir: str = "desc",
    ) -> Dict[str, Any]:
        """Fetch paginated risk results with rich details."""
        query = db.query(RiskResult).join(Medicine, RiskResult.medicine_id == Medicine.medicine_id)

        if search:
            q = f"%{search.strip().lower()}%"
            query = query.filter(
                (Medicine.display_name.ilike(q)) | (Medicine.generic_name.ilike(q)) | (Medicine.medicine_id.ilike(q))
            )
        if category_id:
            query = query.filter(Medicine.category_id == category_id)
        if risk_level:
            query = query.filter(RiskResult.risk_level == risk_level)

        total = query.count()

        # Sorting
        order_col = RiskResult.risk_score
        if sort_by == "stock_coverage_days":
            order_col = RiskResult.stock_coverage_days
        elif sort_by == "expected_daily_demand":
            order_col = RiskResult.expected_daily_demand

        if sort_dir.lower() == "asc":
            query = query.order_by(order_col.asc())
        else:
            query = query.order_by(order_col.desc())

        items = query.offset((page - 1) * page_size).limit(page_size).all()

        results = []
        for r in items:
            extra = {}
            if r.factors_json:
                try:
                    extra = json.loads(r.factors_json)
                except Exception:
                    pass

            results.append({
                "id": r.risk_id,
                "risk_id": r.risk_id,
                "medicine_id": r.medicine_id,
                "calculated_at": r.calculated_at,
                "computed_at": r.calculated_at,
                "risk_score": r.risk_score,
                "risk_level": r.risk_level,
                "expected_daily_demand": r.expected_daily_demand,
                "avg_daily_demand": r.expected_daily_demand,
                "stock_coverage_days": r.stock_coverage_days,
                "days_of_cover": r.stock_coverage_days,
                "days_until_stockout": extra.get("days_until_stockout"),
                "lead_time_days": r.lead_time_days,
                "lead_time_demand": extra.get("lead_time_demand", round(r.expected_daily_demand * r.lead_time_days, 1)),
                "safety_stock": r.safety_stock,
                "required_stock": r.required_stock,
                "reorder_point": r.medicine.inventory.reorder_point if r.medicine and r.medicine.inventory else 100,
                "shortfall": extra.get("shortfall", 0),
                "stockout_probability_7d": extra.get("stockout_probability_7d", 0.0),
                "stockout_probability_14d": extra.get("stockout_probability_14d", 0.0),
                "stockout_probability_30d": extra.get("stockout_probability_30d", 0.0),
                "explanation": r.explanation,
                "factors": extra.get("factors", []),
                "medicine": r.medicine,
            })

        return {
            "data": results,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": math.ceil(total / page_size) if page_size else 1,
        }

    @staticmethod
    def get_by_medicine(db: Session, medicine_id: str) -> Optional[Dict[str, Any]]:
        """Fetch single medicine risk record."""
        r = db.query(RiskResult).filter(RiskResult.medicine_id == medicine_id).first()
        if not r:
            return None
        extra = {}
        if r.factors_json:
            try:
                extra = json.loads(r.factors_json)
            except Exception:
                pass
        return {
            "id": r.risk_id,
            "risk_id": r.risk_id,
            "medicine_id": r.medicine_id,
            "calculated_at": r.calculated_at,
            "computed_at": r.calculated_at,
            "risk_score": r.risk_score,
            "risk_level": r.risk_level,
            "expected_daily_demand": r.expected_daily_demand,
            "avg_daily_demand": r.expected_daily_demand,
            "stock_coverage_days": r.stock_coverage_days,
            "days_of_cover": r.stock_coverage_days,
            "days_until_stockout": extra.get("days_until_stockout"),
            "lead_time_days": r.lead_time_days,
            "lead_time_demand": extra.get("lead_time_demand", round(r.expected_daily_demand * r.lead_time_days, 1)),
            "safety_stock": r.safety_stock,
            "required_stock": r.required_stock,
            "reorder_point": r.medicine.inventory.reorder_point if r.medicine and r.medicine.inventory else 100,
            "shortfall": extra.get("shortfall", 0),
            "stockout_probability_7d": extra.get("stockout_probability_7d", 0.0),
            "stockout_probability_14d": extra.get("stockout_probability_14d", 0.0),
            "stockout_probability_30d": extra.get("stockout_probability_30d", 0.0),
            "explanation": r.explanation,
            "factors": extra.get("factors", []),
            "medicine": r.medicine,
        }

    @staticmethod
    def get_calculation_chain(db: Session, medicine_id: str) -> Optional[Dict[str, Any]]:
        """Fetch calculation chain and explainability breakdown."""
        med = db.query(Medicine).filter(Medicine.medicine_id == medicine_id).first()
        if not med:
            return None
        inv = db.query(InventoryCurrent).filter(InventoryCurrent.medicine_id == medicine_id).first()
        sup = med.primary_supplier
        fcs = db.query(Forecast).filter(Forecast.medicine_id == medicine_id).order_by(Forecast.forecast_date.asc()).all()

        calc = RiskCalculator.calculate_medicine_risk(med, inv, sup, fcs)

        return {
            "medicine_id": medicine_id,
            "expected_daily_demand": calc["expected_daily_demand"],
            "closing_stock": calc["current_stock"],
            "coverage_days": calc["stock_coverage_days"],
            "lead_time_days": calc["lead_time_days"],
            "lead_time_demand": calc["lead_time_demand"],
            "safety_stock": calc["safety_stock"],
            "required_stock": calc["required_stock"],
            "reorder_point": calc["reorder_point"],
            "shortfall": calc["shortfall"],
            "risk_score": calc["risk_score"],
            "risk_level": calc["risk_level"],
            "explanation": calc["explanation"],
            "factors": calc["factors"],
        }

