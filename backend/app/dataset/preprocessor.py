"""Dataset preprocessor for type coercion, date parsing, ordering, and audit logging."""

import datetime
from typing import Dict, List, Any, Optional, Tuple
from pydantic import BaseModel


class PreprocessingAuditEntry(BaseModel):
    table_name: str
    column_name: str
    action: str
    records_affected: int
    sample_before: Optional[str] = None
    sample_after: Optional[str] = None


class PreprocessingReport(BaseModel):
    is_clean: bool
    total_records_processed: int
    audit_entries: List[PreprocessingAuditEntry] = []
    summary: str = ""


class DatasetPreprocessor:
    @staticmethod
    def parse_date(date_str: str) -> datetime.date:
        return datetime.date.fromisoformat(date_str.strip())

    @staticmethod
    def coerce_daily_record(row: Dict[str, str]) -> Dict[str, Any]:
        """Coerce raw CSV row from stockout_prediction_dataset to typed record dict."""
        return {
            "record_id": row["record_id"].strip(),
            "date": DatasetPreprocessor.parse_date(row["date"]),
            "medicine_id": row["medicine_id"].strip(),
            "category_id": row["category_id"].strip(),
            "supplier_id": row["supplier_id"].strip(),
            "closing_stock": int(row.get("closing_stock", 0)),
            "on_order_units": int(row.get("on_order_units", 0)),
            "reorder_point": int(row.get("reorder_point", 100)),
            "units_demanded": int(row.get("units_demanded", 0)),
            "units_sold": int(row.get("units_sold", 0)),
            "sales_7d_avg": float(row.get("sales_7d_avg", 0.0)),
            "sales_30d_avg": float(row.get("sales_30d_avg", 0.0)),
            "days_of_cover": float(row.get("days_of_cover", 0.0)),
            "stock_position_cover_days": float(row.get("stock_position_cover_days", 0.0)),
            "days_since_last_receipt": int(row.get("days_since_last_receipt", 0)),
            "stockout_days_last_30d": int(row.get("stockout_days_last_30d", 0)),
            "supplier_lead_time_mean_days": float(row.get("supplier_lead_time_mean_days", 5.0)),
            "supplier_full_fill_probability": float(row.get("supplier_full_fill_probability", 0.95)),
            "supplier_disruption_active": bool(int(row.get("supplier_disruption_active", 0))),
            "unit_price_inr": float(row.get("unit_price_inr", 0.0)),
            "stockout_today": bool(int(row.get("stockout_today", 0))),
            "stockout_next_7d": bool(int(row.get("stockout_next_7d", 0))),
        }

    @staticmethod
    def coerce_category(row: Dict[str, str]) -> Dict[str, Any]:
        return {
            "category_id": row["category_id"].strip(),
            "category_name": row["category_name"].strip(),
            "description": row["description"].strip() if row.get("description") else "",
        }

    @staticmethod
    def coerce_supplier(row: Dict[str, str]) -> Dict[str, Any]:
        return {
            "supplier_id": row["supplier_id"].strip(),
            "supplier_name": row["supplier_name"].strip(),
            "supplier_type": row["supplier_type"].strip(),
            "city": row["city"].strip(),
            "state": row["state"].strip(),
            "lead_time_mean_days": float(row.get("lead_time_mean_days", 5.0)),
            "lead_time_sd_days": float(row.get("lead_time_sd_days", 1.0)),
            "on_time_probability": float(row.get("on_time_probability", 0.9)),
            "full_fill_probability": float(row.get("full_fill_probability", 0.9)),
            "payment_terms_days": int(row.get("payment_terms_days", 30)),
            "is_active": True,
        }

    @staticmethod
    def coerce_medicine(row: Dict[str, str]) -> Dict[str, Any]:
        cost = float(row.get("unit_cost_inr_2021", row.get("unit_cost_inr", 0.0)))
        price = float(row.get("unit_price_inr_2021", row.get("unit_price_inr", 0.0)))
        return {
            "medicine_id": row["medicine_id"].strip(),
            "generic_name": row["generic_name"].strip(),
            "display_name": row["display_name"].strip(),
            "active_ingredients": row.get("active_ingredients", "").strip() or None,
            "strength": row.get("strength", "").strip(),
            "dosage_form": row.get("dosage_form", "").strip(),
            "route": row.get("route", "Oral").strip(),
            "category_id": row["category_id"].strip(),
            "primary_supplier_id": row["primary_supplier_id"].strip(),
            "unit_of_measure": row.get("unit_of_measure", "tablet").strip(),
            "pack_size": int(row.get("pack_size", 10)),
            "storage_condition": row.get("storage_condition", "Room temperature").strip(),
            "unit_cost_inr": cost,
            "unit_price_inr": price,
            "composition_status": row.get("composition_status", "VERIFIED_STANDARD_REFERENCE").strip(),
            "composition_note": row.get("composition_note", "").strip() or None,
            "is_active": True,
        }
