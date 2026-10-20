"""Data preprocessing and integrity checks for ML training and backtesting."""

import os
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from backend.app.ml.config import MLConfig


class MLPreprocessor:
    @staticmethod
    def load_raw_dataset(csv_path: str) -> pd.DataFrame:
        """Load and type-coerce the daily dataset from CSV."""
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Dataset not found at {csv_path}")

        df = pd.read_csv(csv_path)
        return MLPreprocessor.preprocess(df)

    @staticmethod
    def preprocess(df: pd.DataFrame) -> pd.DataFrame:
        """Parse dates, sort chronologically, assert integrity, and prepare demand series."""
        df = df.copy()

        # 1. Parse date and sort
        df["date"] = pd.to_datetime(df["date"]).dt.date
        df = df.sort_values(by=["medicine_id", "date"]).reset_index(drop=True)

        # 2. Target column: demand
        # In stockout_prediction_dataset.csv, demand is recorded as 'units_demanded'
        if "units_demanded" in df.columns:
            df["demand"] = df["units_demanded"].astype(float)
        elif "demand" not in df.columns:
            raise KeyError("DataFrame must contain 'units_demanded' or 'demand'")

        # 3. Assertions & Integrity Checks
        # Non-negative demand
        assert (df["demand"] >= 0).all(), "Demand values must be non-negative"

        # Unique medicine-date pairs (no duplicates)
        dups = df.duplicated(subset=["medicine_id", "date"]).sum()
        assert dups == 0, f"Found {dups} duplicate (medicine_id, date) rows"

        # Ensure numeric columns are properly typed
        float_cols = [
            "sales_7d_avg", "sales_30d_avg", "days_of_cover",
            "stock_position_cover_days", "supplier_lead_time_mean_days",
            "supplier_full_fill_probability", "unit_price_inr"
        ]
        for col in float_cols:
            if col in df.columns:
                df[col] = df[col].astype(float)

        int_cols = [
            "closing_stock", "on_order_units", "reorder_point",
            "days_since_last_receipt", "stockout_days_last_30d"
        ]
        for col in int_cols:
            if col in df.columns:
                df[col] = df[col].astype(int)

        return df

    @staticmethod
    def verify_temporal_continuity(df: pd.DataFrame) -> Dict[str, Any]:
        """Verify that every medicine has contiguous daily records without date gaps."""
        report = {}
        medicines = df["medicine_id"].unique()
        all_continuous = True

        for med in medicines:
            med_df = df[df["medicine_id"] == med].sort_values("date")
            dates = pd.to_datetime(med_df["date"])
            diffs = dates.diff().dropna()
            is_contiguous = (diffs == pd.Timedelta(days=1)).all()
            if not is_contiguous:
                all_continuous = False
                report[med] = "Gaps detected"

        return {
            "all_continuous": all_continuous,
            "total_medicines": len(medicines),
            "exceptions": report,
        }
