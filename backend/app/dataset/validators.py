"""Dataset schema verification and runtime data quality validation rules."""

import os
import csv
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from backend.app.dataset.column_map import FILE_SCHEMAS


class ValidationCheckResult(BaseModel):
    category: str
    check_name: str
    passed: bool
    details: str
    error_count: int = 0


class FileSchemaResult(BaseModel):
    filename: str
    passed: bool
    total_columns_found: int
    expected_columns_count: int
    missing_columns: List[str] = []
    extra_columns: List[str] = []
    column_checks: List[Dict[str, Any]] = []


class DatasetValidationReport(BaseModel):
    overall_passed: bool
    files_checked: int
    total_checks: int
    passed_checks: int
    failed_checks: int
    schema_results: Dict[str, FileSchemaResult]
    quality_checks: List[ValidationCheckResult]


class DatasetValidator:
    def __init__(self, raw_data_dir: str):
        self.raw_data_dir = raw_data_dir

    def get_file_path(self, filename: str) -> Optional[str]:
        p = os.path.join(self.raw_data_dir, filename)
        return p if os.path.exists(p) else None

    def verify_schema(self, filename: str) -> FileSchemaResult:
        file_path = self.get_file_path(filename)
        expected_cols = FILE_SCHEMAS.get(filename, [])
        expected_names = [col.name for col in expected_cols]

        if not file_path:
            return FileSchemaResult(
                filename=filename,
                passed=False,
                total_columns_found=0,
                expected_columns_count=len(expected_cols),
                missing_columns=expected_names,
                extra_columns=[],
                column_checks=[{"column": name, "status": "FILE_NOT_FOUND"} for name in expected_names],
            )

        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, [])

        header_set = set(header)
        expected_set = set(expected_names)

        missing = [c for c in expected_names if c not in header_set]
        extra = [c for c in header if c not in expected_set]

        column_checks = []
        for col_def in expected_cols:
            present = col_def.name in header_set
            column_checks.append({
                "column": col_def.name,
                "expected_dtype": col_def.dtype,
                "required": col_def.required,
                "present": present,
                "status": "PASS" if present else ("FAIL" if col_def.required else "OPTIONAL_MISSING"),
            })

        passed = len(missing) == 0
        return FileSchemaResult(
            filename=filename,
            passed=passed,
            total_columns_found=len(header),
            expected_columns_count=len(expected_names),
            missing_columns=missing,
            extra_columns=extra,
            column_checks=column_checks,
        )

    def run_all_validations(self) -> DatasetValidationReport:
        schema_results: Dict[str, FileSchemaResult] = {}
        for filename in FILE_SCHEMAS.keys():
            schema_results[filename] = self.verify_schema(filename)

        quality_checks: List[ValidationCheckResult] = []

        # 1. Structure: Total daily records == 155,210
        pred_file = self.get_file_path("stockout_prediction_dataset.csv")
        row_count = 0
        unique_record_ids = set()
        unique_meds = set()
        unique_dates = set()
        negative_closing = 0
        negative_demand = 0
        stockout_7d_count = 0

        if pred_file:
            with open(pred_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row_count += 1
                    rec_id = row.get("record_id")
                    if rec_id:
                        unique_record_ids.add(rec_id)
                    med_id = row.get("medicine_id")
                    if med_id:
                        unique_meds.add(med_id)
                    d = row.get("date")
                    if d:
                        unique_dates.add(d)
                    
                    try:
                        cs = int(row.get("closing_stock", 0))
                        if cs < 0:
                            negative_closing += 1
                    except ValueError:
                        pass

                    try:
                        dem = int(row.get("units_demanded", 0))
                        if dem < 0:
                            negative_demand += 1
                    except ValueError:
                        pass

                    if row.get("stockout_next_7d") == "1":
                        stockout_7d_count += 1

        quality_checks.append(ValidationCheckResult(
            category="Structure",
            check_name="Total daily records count (155,210)",
            passed=(row_count == 155210),
            details=f"Found {row_count:,} records (expected 155,210)",
            error_count=abs(row_count - 155210),
        ))

        quality_checks.append(ValidationCheckResult(
            category="Structure",
            check_name="Record ID uniqueness",
            passed=(len(unique_record_ids) == row_count and row_count > 0),
            details=f"{len(unique_record_ids):,} unique IDs for {row_count:,} rows",
            error_count=row_count - len(unique_record_ids),
        ))

        quality_checks.append(ValidationCheckResult(
            category="Structure",
            check_name="Distinct medicines count (85)",
            passed=(len(unique_meds) == 85),
            details=f"Found {len(unique_meds)} distinct medicines (expected 85)",
            error_count=abs(len(unique_meds) - 85),
        ))

        quality_checks.append(ValidationCheckResult(
            category="Structure",
            check_name="Date span (1,826 days from 2021-01-01 to 2025-12-31)",
            passed=(len(unique_dates) == 1826 and "2021-01-01" in unique_dates and "2025-12-31" in unique_dates),
            details=f"Found {len(unique_dates):,} continuous calendar dates",
            error_count=abs(len(unique_dates) - 1826),
        ))

        quality_checks.append(ValidationCheckResult(
            category="Data Quality",
            check_name="No negative closing stock",
            passed=(negative_closing == 0),
            details=f"Found {negative_closing} negative inventory rows",
            error_count=negative_closing,
        ))

        quality_checks.append(ValidationCheckResult(
            category="Data Quality",
            check_name="No negative customer demand",
            passed=(negative_demand == 0),
            details=f"Found {negative_demand} negative demand rows",
            error_count=negative_demand,
        ))

        # Check categories count
        cat_file = self.get_file_path("categories.csv")
        cat_count = 0
        if cat_file:
            with open(cat_file, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)
                cat_count = sum(1 for row in reader if row)

        quality_checks.append(ValidationCheckResult(
            category="Master Data",
            check_name="Distinct categories count (11)",
            passed=(cat_count == 11),
            details=f"Found {cat_count} therapeutic categories (expected 11)",
            error_count=abs(cat_count - 11),
        ))

        # Check suppliers count
        sup_file = self.get_file_path("suppliers.csv")
        sup_count = 0
        if sup_file:
            with open(sup_file, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)
                sup_count = sum(1 for row in reader if row)

        quality_checks.append(ValidationCheckResult(
            category="Master Data",
            check_name="Distinct suppliers count (15)",
            passed=(sup_count == 15),
            details=f"Found {sup_count} commercial suppliers (expected 15)",
            error_count=abs(sup_count - 15),
        ))

        # Target stockout_next_7d prevalence
        prevalence = round((stockout_7d_count / max(1, row_count)) * 100, 2)
        quality_checks.append(ValidationCheckResult(
            category="Target Verification",
            check_name="Stockout target prevalence (expected ~18.8%)",
            passed=(18.0 <= prevalence <= 19.5),
            details=f"Target stockout_next_7d prevalence: {prevalence}% ({stockout_7d_count:,} positive cases)",
            error_count=0,
        ))

        total_q = len(quality_checks)
        passed_q = sum(1 for q in quality_checks if q.passed)
        failed_q = total_q - passed_q
        all_schemas_passed = all(s.passed for s in schema_results.values())
        overall_passed = all_schemas_passed and (failed_q == 0)

        return DatasetValidationReport(
            overall_passed=overall_passed,
            files_checked=len(schema_results),
            total_checks=total_q,
            passed_checks=passed_q,
            failed_checks=failed_q,
            schema_results=schema_results,
            quality_checks=quality_checks,
        )
