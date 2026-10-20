"""Chronological data splitting and rolling-origin backtest folds."""

import datetime
import pandas as pd
from typing import Tuple, List, Dict, Any
from backend.app.ml.config import MLConfig


class ChronologicalSplitter:
    @staticmethod
    def split_train_val_test(
        df: pd.DataFrame,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Partition dataset into strictly chronological Train, Validation, and Test subsets.
        Train: 2021-01-01 -> 2023-12-31
        Validation: 2024-01-01 -> 2024-12-31
        Test: 2025-01-01 -> 2025-12-31
        """
        df = df.copy()
        if not pd.api.types.is_datetime64_any_dtype(df["date"]):
            df["date"] = pd.to_datetime(df["date"]).dt.date

        train_mask = (df["date"] >= MLConfig.TRAIN_START) & (df["date"] <= MLConfig.TRAIN_END)
        val_mask = (df["date"] >= MLConfig.VAL_START) & (df["date"] <= MLConfig.VAL_END)
        test_mask = (df["date"] >= MLConfig.TEST_START) & (df["date"] <= MLConfig.TEST_END)

        train_df = df[train_mask].copy().reset_index(drop=True)
        val_df = df[val_mask].copy().reset_index(drop=True)
        test_df = df[test_mask].copy().reset_index(drop=True)

        # Assert no temporal overlap
        if not train_df.empty and not val_df.empty:
            assert train_df["date"].max() < val_df["date"].min(), "Train overlaps Validation"
        if not val_df.empty and not test_df.empty:
            assert val_df["date"].max() < test_df["date"].min(), "Validation overlaps Test"

        return train_df, val_df, test_df

    @staticmethod
    def get_rolling_origin_cutoffs(
        start_date: datetime.date = MLConfig.TEST_START,
        end_date: datetime.date = MLConfig.TEST_END,
        step_days: int = 30,
        horizon_days: int = 30,
    ) -> List[datetime.date]:
        """
        Generate origin cutoff dates across evaluation period for rolling-origin backtesting.
        Ensures origin + horizon_days does not exceed the test period end.
        """
        cutoffs = []
        curr = start_date
        max_origin = end_date - datetime.timedelta(days=horizon_days)

        while curr <= max_origin:
            cutoffs.append(curr)
            curr += datetime.timedelta(days=step_days)

        return cutoffs
