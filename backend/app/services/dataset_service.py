"""Dataset service orchestrating detection, preview, validation, import, and statistics."""

import os
import csv
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.db.models.category import Category
from backend.app.db.models.supplier import Supplier
from backend.app.db.models.medicine import Medicine
from backend.app.db.models.daily_record import DailyRecord
from backend.app.db.models.inventory import InventoryCurrent
from backend.app.db.models.app_settings import DatasetImport
from backend.app.dataset.column_map import FILE_SCHEMAS
from backend.app.dataset.validators import DatasetValidator, DatasetValidationReport
from backend.app.dataset.importer import DatasetImporter, ImportResult
from backend.app.core.errors import NotFoundException


class DatasetService:
    @staticmethod
    def get_raw_data_dir() -> str:
        candidates = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "raw")),
            os.path.abspath("data/raw"),
            os.path.abspath("backend/data/raw"),
            os.path.abspath("pharmacy_stockout_dataset_pack"),
        ]
        for c in candidates:
            if os.path.exists(c) and os.path.exists(os.path.join(c, "stockout_prediction_dataset.csv")):
                return c
        return candidates[0]

    @staticmethod
    def get_dataset_status(db: Session) -> Dict[str, Any]:
        raw_dir = DatasetService.get_raw_data_dir()
        raw_files = []
        if os.path.exists(raw_dir):
            for f in os.listdir(raw_dir):
                if f.endswith(".csv"):
                    p = os.path.join(raw_dir, f)
                    raw_files.append({
                        "filename": f,
                        "size_bytes": os.path.getsize(p),
                        "is_expected": f in FILE_SCHEMAS,
                    })

        total_daily_records = db.query(func.count(DailyRecord.record_id)).scalar() or 0
        total_medicines = db.query(func.count(Medicine.medicine_id)).scalar() or 0
        total_suppliers = db.query(func.count(Supplier.supplier_id)).scalar() or 0
        total_categories = db.query(func.count(Category.category_id)).scalar() or 0
        last_import = db.query(DatasetImport).order_by(DatasetImport.imported_at.desc()).first()

        is_imported = total_daily_records >= 155210

        return {
            "raw_data_dir": raw_dir,
            "raw_files_count": len(raw_files),
            "raw_files": raw_files,
            "is_imported": is_imported,
            "total_daily_records": total_daily_records,
            "total_medicines": total_medicines,
            "total_suppliers": total_suppliers,
            "total_categories": total_categories,
            "last_import": {
                "import_id": last_import.import_id,
                "file_name": last_import.file_name,
                "row_count": last_import.row_count,
                "status": last_import.status,
                "imported_at": last_import.imported_at.isoformat() if last_import.imported_at else None,
            } if last_import else None,
        }

    @staticmethod
    def preview_file(filename: str, limit: int = 10) -> Dict[str, Any]:
        raw_dir = DatasetService.get_raw_data_dir()
        file_path = os.path.join(raw_dir, filename)
        if not os.path.exists(file_path):
            raise NotFoundException("Dataset file", filename)

        rows = []
        headers = []
        total_rows_est = 0

        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader, [])
            for i, r in enumerate(reader):
                if i < limit:
                    rows.append(r)
                total_rows_est += 1

        # Dtypes from schema definition if available
        col_defs = {c.name: c.dtype for c in FILE_SCHEMAS.get(filename, [])}
        columns_meta = [
            {"name": h, "dtype": col_defs.get(h, "string")} for h in headers
        ]

        return {
            "filename": filename,
            "columns": columns_meta,
            "rows": rows,
            "sample_count": len(rows),
            "total_rows_estimate": total_rows_est,
        }

    @staticmethod
    def validate_dataset() -> DatasetValidationReport:
        raw_dir = DatasetService.get_raw_data_dir()
        validator = DatasetValidator(raw_dir)
        return validator.run_all_validations()

    @staticmethod
    def run_import(db: Session, force_reload: bool = False) -> ImportResult:
        raw_dir = DatasetService.get_raw_data_dir()
        importer = DatasetImporter(raw_dir)
        return importer.import_all(db, force_reload=force_reload)

    @staticmethod
    def get_statistics(db: Session) -> Dict[str, Any]:
        total_records = db.query(func.count(DailyRecord.record_id)).scalar() or 0
        total_meds = db.query(func.count(Medicine.medicine_id)).scalar() or 0
        total_sups = db.query(func.count(Supplier.supplier_id)).scalar() or 0
        total_cats = db.query(func.count(Category.category_id)).scalar() or 0

        min_date = db.query(func.min(DailyRecord.date)).scalar()
        max_date = db.query(func.max(DailyRecord.date)).scalar()

        stockout_7d_count = (
            db.query(func.count(DailyRecord.record_id))
            .filter(DailyRecord.stockout_next_7d == True)
            .scalar()
            or 0
        )

        stockout_prevalence = round((stockout_7d_count / max(1, total_records)) * 100, 2)

        return {
            "total_daily_records": total_records,
            "expected_daily_records": 155210,
            "total_medicines": total_meds,
            "expected_medicines": 85,
            "total_suppliers": total_sups,
            "expected_suppliers": 15,
            "total_categories": total_cats,
            "expected_categories": 11,
            "date_range": {
                "start_date": min_date.isoformat() if min_date else None,
                "end_date": max_date.isoformat() if max_date else None,
            },
            "stockout_next_7d_count": stockout_7d_count,
            "stockout_prevalence_pct": stockout_prevalence,
            "is_complete": (total_records == 155210 and total_meds == 85),
        }
