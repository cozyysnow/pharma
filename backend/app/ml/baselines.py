"""Baseline forecasting models (naïve, seasonal naïve, rolling means, historical mean)."""

import numpy as np
import pandas as pd
from typing import Dict, Any, List


class BaselineForecaster:
    """Computes all 5 mandatory baseline predictions for a medicine demand series."""

    @staticmethod
    def naive_lag_1(series: pd.Series) -> pd.Series:
        """Naïve baseline: predict yesterday's demand."""
        return series.shift(1).bfill().fillna(0.0)

    @staticmethod
    def seasonal_naive_lag_7(series: pd.Series) -> pd.Series:
        """Seasonal naïve baseline: predict same day of previous week."""
        return series.shift(7).bfill().fillna(0.0)

    @staticmethod
    def rolling_mean_7(series: pd.Series) -> pd.Series:
        """7-day rolling mean baseline computed on shifted series."""
        return series.shift(1).rolling(window=7, min_periods=1).mean().fillna(0.0)

    @staticmethod
    def rolling_mean_28(series: pd.Series) -> pd.Series:
        """28-day rolling mean baseline computed on shifted series."""
        return series.shift(1).rolling(window=28, min_periods=1).mean().fillna(0.0)

    @staticmethod
    def historical_mean(train_series: pd.Series, target_length: int) -> pd.Series:
        """Historical mean demand from training period broadcast to target horizon."""
        mean_val = float(train_series.mean()) if not train_series.empty else 0.0
        return pd.Series([mean_val] * target_length)

    @staticmethod
    def generate_all_baselines(
        full_df: pd.DataFrame,
        eval_mask: pd.Series,
    ) -> Dict[str, np.ndarray]:
        """
        Compute baseline predictions for all 5 methods across evaluation rows.
        Returns dict mapping baseline name to prediction array.
        """
        predictions = {
            "Naive (Lag-1)": [],
            "Seasonal Naive (Lag-7)": [],
            "7-Day Rolling Mean": [],
            "28-Day Rolling Mean": [],
            "Historical Mean": [],
        }

        # Compute per medicine
        for med_id, group in full_df.groupby("medicine_id", sort=False):
            g = group.sort_values("date")
            sub_eval_mask = eval_mask.loc[g.index]

            l1 = BaselineForecaster.naive_lag_1(g["demand"]).loc[g.index[sub_eval_mask]]
            l7 = BaselineForecaster.seasonal_naive_lag_7(g["demand"]).loc[g.index[sub_eval_mask]]
            r7 = BaselineForecaster.rolling_mean_7(g["demand"]).loc[g.index[sub_eval_mask]]
            r28 = BaselineForecaster.rolling_mean_28(g["demand"]).loc[g.index[sub_eval_mask]]

            # Historical mean from training subset
            train_sub = g[g["date"] <= pd.to_datetime("2023-12-31").date()]
            hist_m = float(train_sub["demand"].mean()) if not train_sub.empty else float(g["demand"].mean())
            hm = pd.Series([hist_m] * sub_eval_mask.sum())

            predictions["Naive (Lag-1)"].extend(l1.values)
            predictions["Seasonal Naive (Lag-7)"].extend(l7.values)
            predictions["7-Day Rolling Mean"].extend(r7.values)
            predictions["28-Day Rolling Mean"].extend(r28.values)
            predictions["Historical Mean"].extend(hm.values)

        return {k: np.array(v) for k, v in predictions.items()}
