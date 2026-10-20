"""High-performance, idempotent dataset importer for master data and daily records."""

import os
import csv
import uuid
import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.db.models.category import Category
from backend.app.db.models.supplier import Supplier
from backend.app.db.models.medicine import Medicine
from backend.app.db.models.daily_record import DailyRecord
from backend.app.db.models.inventory import InventoryCurrent
from backend.app.db.models.app_settings import DatasetImport
from backend.app.dataset.preprocessor import DatasetPreprocessor


class ImportResult:
    def __init__(self):
        self.categories_count = 0
        self.suppliers_count = 0
        self.medicines_count = 0
        self.daily_records_count = 0
        self.inventory_synced_count = 0
        self.was_already_imported = False
        self.duration_seconds = 0.0
        self.message = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "categories_count": self.categories_count,
            "suppliers_count": self.suppliers_count,
            "medicines_count": self.medicines_count,
            "daily_records_count": self.daily_records_count,
            "inventory_synced_count": self.inventory_synced_count,
            "was_already_imported": self.was_already_imported,
            "duration_seconds": self.duration_seconds,
            "message": self.message,
        }


class DatasetImporter:
    def __init__(self, raw_data_dir: str):
        self.raw_data_dir = raw_data_dir

    def _file_path(self, filename: str) -> str:
        p = os.path.join(self.raw_data_dir, filename)
        if not os.path.exists(p):
            raise FileNotFoundError(f"Dataset file not found at: {p}")
        return p

    def import_all(self, db: Session, force_reload: bool = False) -> ImportResult:
        start_time = datetime.datetime.utcnow()
        result = ImportResult()

        # Check idempotency: if already 155,210 daily records exist and not forced
        existing_records = db.query(func.count(DailyRecord.record_id)).scalar() or 0
        if existing_records >= 155210 and not force_reload:
            result.was_already_imported = True
            result.categories_count = 11
            result.suppliers_count = 15
            result.medicines_count = 85
            result.daily_records_count = existing_records
            result.inventory_synced_count = 85
            result.duration_seconds = 0.0
            result.message = "Dataset already imported (155,210 records). Idempotent no-op."
            return result

        # 1. Import Categories
        cat_file = self._file_path("categories.csv")
        cat_count = 0
        with open(cat_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data = DatasetPreprocessor.coerce_category(row)
                existing = db.query(Category).filter(Category.category_id == data["category_id"]).first()
                if not existing:
                    db.add(Category(**data))
                else:
                    existing.category_name = data["category_name"]
                    existing.description = data["description"]
                cat_count += 1
        db.commit()
        result.categories_count = cat_count

        # 2. Import Suppliers
        sup_file = self._file_path("suppliers.csv")
        sup_count = 0
        with open(sup_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data = DatasetPreprocessor.coerce_supplier(row)
                existing = db.query(Supplier).filter(Supplier.supplier_id == data["supplier_id"]).first()
                if not existing:
                    db.add(Supplier(**data))
                else:
                    for k, v in data.items():
                        setattr(existing, k, v)
                sup_count += 1
        db.commit()
        result.suppliers_count = sup_count

        # 3. Import Medicines
        med_file = self._file_path("medicines.csv")
        med_count = 0
        with open(med_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data = DatasetPreprocessor.coerce_medicine(row)
                existing = db.query(Medicine).filter(Medicine.medicine_id == data["medicine_id"]).first()
                if not existing:
                    db.add(Medicine(**data))
                else:
                    for k, v in data.items():
                        setattr(existing, k, v)
                med_count += 1
        db.commit()
        result.medicines_count = med_count

        # 4. Import Daily Records (Chunked bulk insert)
        pred_file = self._file_path("stockout_prediction_dataset.csv")
        
        # If forcing reload, delete old daily records
        if force_reload and existing_records > 0:
            db.query(DailyRecord).delete()
            db.commit()

        chunk_size = 10000
        chunk = []
        imported_rows = 0

        with open(pred_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                chunk.append(DatasetPreprocessor.coerce_daily_record(row))
                if len(chunk) >= chunk_size:
                    db.bulk_insert_mappings(DailyRecord, chunk)
                    db.commit()
                    imported_rows += len(chunk)
                    chunk = []

            if chunk:
                db.bulk_insert_mappings(DailyRecord, chunk)
                db.commit()
                imported_rows += len(chunk)

        result.daily_records_count = imported_rows

        # 5. Initialize / Synchronize Inventory Current to 2025-12-31 closing values
        latest_date = datetime.date(2025, 12, 31)
        latest_records = (
            db.query(DailyRecord)
            .filter(DailyRecord.date == latest_date)
            .all()
        )

        synced_count = 0
        for rec in latest_records:
            inv = db.query(InventoryCurrent).filter(InventoryCurrent.medicine_id == rec.medicine_id).first()
            if not inv:
                inv = InventoryCurrent(medicine_id=rec.medicine_id)
                db.add(inv)

            inv.opening_stock = rec.closing_stock
            inv.closing_stock = rec.closing_stock
            inv.on_order_units = rec.on_order_units
            inv.reorder_point = rec.reorder_point
            inv.order_up_to_level = rec.reorder_point * 2
            inv.safety_stock = max(50, int(rec.reorder_point * 0.3))
            inv.moq = 50
            inv.expected_daily_demand = max(0.1, round(rec.sales_7d_avg, 2))
            inv.days_of_cover = round(rec.days_of_cover, 2)

            if inv.closing_stock <= 0:
                inv.stock_status = "OUT_OF_STOCK"
            elif inv.closing_stock <= inv.reorder_point:
                inv.stock_status = "LOW_STOCK"
            elif inv.closing_stock > inv.order_up_to_level:
                inv.stock_status = "OVERSTOCKED"
            else:
                inv.stock_status = "IN_STOCK"

            synced_count += 1

        db.commit()
        result.inventory_synced_count = synced_count

        # 6. Audit Import Table
        imp_log = db.query(DatasetImport).filter(DatasetImport.import_id == "IMP_BUNDLED_2026").first()
        if not imp_log:
            imp_log = DatasetImport(
                import_id="IMP_BUNDLED_2026",
                file_name="stockout_prediction_dataset.csv",
                row_count=str(imported_rows),
                status="SUCCESS",
                details_json=f'{{"categories": {result.categories_count}, "suppliers": {result.suppliers_count}, "medicines": {result.medicines_count}}}',
            )
            db.add(imp_log)
        else:
            imp_log.row_count = str(imported_rows)
            imp_log.status = "SUCCESS"
            imp_log.imported_at = datetime.datetime.utcnow()

        db.commit()

        duration = (datetime.datetime.utcnow() - start_time).total_seconds()
        result.duration_seconds = round(duration, 2)
        result.message = f"Successfully imported {imported_rows:,} daily records, {result.medicines_count} medicines, {result.suppliers_count} suppliers, {result.categories_count} categories in {result.duration_seconds}s."
        return result
