"""Feature engineering pipeline for demand forecasting with strict temporal leakage prevention."""

import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Any, Optional
from backend.app.ml.config import MLConfig


class FeatureEngineer:
    def __init__(self, train_mean_demand_map: Optional[Dict[str, float]] = None):
        """
        train_mean_demand_map: precomputed historical mean demand per medicine
        computed strictly on training period data.
        """
        self.train_mean_demand_map = train_mean_demand_map or {}
        self.feature_names: List[str] = []

    def fit_static_statistics(self, df: pd.DataFrame, train_end_date=MLConfig.TRAIN_END):
        """Fit static medicine-level aggregations ONLY on the training period."""
        train_df = df[df["date"] <= train_end_date]
        self.train_mean_demand_map = (
            train_df.groupby("medicine_id")["demand"].mean().to_dict()
        )

    def generate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute all lag, rolling, calendar, and seasonal features grouped per medicine.
        Uses shift(1) for rolling stats to prevent temporal target leakage.
        """
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])
        min_date = df["date"].min()

        # Sort chronologically by entity and date
        df = df.sort_values(by=["medicine_id", "date"]).reset_index(drop=True)

        features_df_list = []
        feature_cols_set = set()

        # Group by medicine to calculate lags and rolling features per series
        for med_id, group in df.groupby("medicine_id", sort=False):
            g = group.copy().sort_values("date")
            demand_series = g["demand"]

            # 1. Lags
            for lag in MLConfig.LAGS:
                col = f"lag_{lag}"
                g[col] = demand_series.shift(lag)
                feature_cols_set.add(col)

            # 2. Rolling stats on shifted series (shift(1) ensures no contemporaneous leakage)
            shifted = demand_series.shift(1)
            for window in MLConfig.ROLLING_WINDOWS:
                mean_col = f"rolling_mean_{window}"
                std_col = f"rolling_std_{window}"
                min_col = f"rolling_min_{window}"
                max_col = f"rolling_max_{window}"

                roll = shifted.rolling(window=window, min_periods=1)
                g[mean_col] = roll.mean()
                g[std_col] = roll.std().fillna(0.0)
                g[min_col] = roll.min()
                g[max_col] = roll.max()

                feature_cols_set.update([mean_col, std_col, min_col, max_col])

            # Exponential weighted moving average (7-day span)
            g["ewm_mean_7"] = shifted.ewm(span=7, min_periods=1).mean()
            feature_cols_set.add("ewm_mean_7")

            # 3. Calendar features (known in advance)
            dt = g["date"].dt
            g["day_of_week"] = dt.dayofweek
            g["day_of_month"] = dt.day
            g["month"] = dt.month
            g["quarter"] = dt.quarter
            g["is_weekend"] = (dt.dayofweek >= 5).astype(int)

            day_of_year = dt.dayofyear
            g["day_of_year_sin"] = np.sin(2 * np.pi * day_of_year / 365.25)
            g["day_of_year_cos"] = np.cos(2 * np.pi * day_of_year / 365.25)

            feature_cols_set.update(MLConfig.CALENDAR_FEATURES)

            # 4. Trend and Seasonal features
            r7 = g["rolling_mean_7"] + 1e-4
            r28 = g["rolling_mean_28"] + 1e-4
            g["rolling_ratio_7_28"] = r7 / r28
            g["time_index"] = (g["date"] - min_date).dt.days
            g["same_weekday_lag_7"] = g["lag_7"]
            g["same_weekday_lag_14"] = g["lag_14"]

            feature_cols_set.update([
                "rolling_ratio_7_28",
                "time_index",
                "same_weekday_lag_7",
                "same_weekday_lag_14",
            ])

            # 5. Static medicine feature: train_mean_demand
            fallback_mean = float(demand_series.mean())
            med_mean = self.train_mean_demand_map.get(med_id, fallback_mean)
            g["train_mean_demand"] = med_mean
            feature_cols_set.add("train_mean_demand")

            # Static supplier lead time if present
            if "supplier_lead_time_mean_days" in g.columns:
                feature_cols_set.add("supplier_lead_time_mean_days")

            features_df_list.append(g)

        result_df = pd.concat(features_df_list, axis=0).reset_index(drop=True)
        result_df["date"] = result_df["date"].dt.date
        self.feature_names = sorted(list(feature_cols_set))

        return result_df

    def get_feature_matrix(
        self, df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.Series, List[str]]:
        """Extract feature matrix X, target y, and validated feature list without NaNs or forbidden columns."""
        # Clean any forbidden columns from feature list
        valid_features = [
            f for f in self.feature_names if f not in MLConfig.FORBIDDEN_FEATURES
        ]

        # Fill leading edge NaNs from earliest lags with 0.0 or train_mean_demand
        X = df[valid_features].copy().fillna(0.0)
        y = df[MLConfig.TARGET_COLUMN].copy()

        return X, y, valid_features
