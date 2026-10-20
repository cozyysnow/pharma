"""Multi-step recursive forecast generator for operational demand projections."""

import datetime
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from backend.app.ml.config import MLConfig


class ForecastGenerator:
    def __init__(
        self,
        fitted_model: Any,
        feature_names: List[str],
        train_mean_demand_map: Dict[str, float],
        residual_std_map: Optional[Dict[str, float]] = None,
    ):
        self.model = fitted_model
        self.feature_names = feature_names
        self.train_mean_demand_map = train_mean_demand_map
        self.residual_std_map = residual_std_map or {}

    def generate_recursive_forecast(
        self,
        historical_df: pd.DataFrame,
        medicine_id: str,
        horizon_days: int = MLConfig.DEFAULT_HORIZON,
        as_of_date: Optional[datetime.date] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate recursive multi-step demand predictions for a single medicine.
        Past predictions are recursively fed into lag and rolling features.
        """
        med_history = (
            historical_df[historical_df["medicine_id"] == medicine_id]
            .sort_values("date")
            .copy()
        )
        if med_history.empty:
            raise ValueError(f"No history found for medicine {medicine_id}")

        if as_of_date is None:
            as_of_date = med_history["date"].max()
        else:
            med_history = med_history[med_history["date"] <= as_of_date]

        # Use recent demand values buffer (up to 60 days) to populate lags
        history_dates = list(pd.to_datetime(med_history["date"]).dt.date)
        history_demands = list(med_history["demand"].astype(float))

        # Base series mapping: date -> demand
        demand_series_map = dict(zip(history_dates, history_demands))

        category_id = med_history["category_id"].iloc[-1] if "category_id" in med_history.columns else "CAT01"
        supplier_id = med_history["supplier_id"].iloc[-1] if "supplier_id" in med_history.columns else "SUP01"
        lead_time = float(med_history["supplier_lead_time_mean_days"].iloc[-1]) if "supplier_lead_time_mean_days" in med_history.columns else 5.0
        train_mean = self.train_mean_demand_map.get(medicine_id, float(np.mean(history_demands)))
        res_std = self.residual_std_map.get(medicine_id, 3.0)

        min_date = med_history["date"].min()
        predictions = []

        curr_date = as_of_date + datetime.timedelta(days=1)
        simulated_demands = list(history_demands)

        for step in range(horizon_days):
            target_date = curr_date + datetime.timedelta(days=step)

            # Build feature row for target_date
            row_features = {}

            # 1. Lags from simulated demands
            for lag in MLConfig.LAGS:
                if len(simulated_demands) >= lag:
                    row_features[f"lag_{lag}"] = simulated_demands[-lag]
                else:
                    row_features[f"lag_{lag}"] = train_mean

            # 2. Rolling stats on simulated demands (last N entries)
            for window in MLConfig.ROLLING_WINDOWS:
                recent = simulated_demands[-window:] if len(simulated_demands) >= window else simulated_demands
                row_features[f"rolling_mean_{window}"] = float(np.mean(recent)) if recent else train_mean
                row_features[f"rolling_std_{window}"] = float(np.std(recent)) if len(recent) > 1 else 0.0
                row_features[f"rolling_min_{window}"] = float(np.min(recent)) if recent else train_mean
                row_features[f"rolling_max_{window}"] = float(np.max(recent)) if recent else train_mean

            # EWM mean
            row_features["ewm_mean_7"] = float(pd.Series(simulated_demands[-14:]).ewm(span=7).mean().iloc[-1])

            # 3. Calendar features
            dt = pd.to_datetime(target_date)
            row_features["day_of_week"] = dt.dayofweek
            row_features["day_of_month"] = dt.day
            row_features["month"] = dt.month
            row_features["quarter"] = dt.quarter
            row_features["is_weekend"] = int(dt.dayofweek >= 5)

            doy = dt.dayofyear
            row_features["day_of_year_sin"] = np.sin(2 * np.pi * doy / 365.25)
            row_features["day_of_year_cos"] = np.cos(2 * np.pi * doy / 365.25)

            # 4. Trend and Seasonal features
            r7 = row_features["rolling_mean_7"] + 1e-4
            r28 = row_features["rolling_mean_28"] + 1e-4
            row_features["rolling_ratio_7_28"] = r7 / r28
            row_features["time_index"] = (target_date - min_date).days
            row_features["same_weekday_lag_7"] = row_features.get("lag_7", train_mean)
            row_features["same_weekday_lag_14"] = row_features.get("lag_14", train_mean)

            # 5. Static features
            row_features["train_mean_demand"] = train_mean
            row_features["supplier_lead_time_mean_days"] = lead_time

            # Format X row matching training columns
            X_step = pd.DataFrame([{f: row_features.get(f, 0.0) for f in self.feature_names}])

            # Predict demand
            pred_demand = float(self.model.predict(X_step)[0])
            pred_demand = max(0.0, round(pred_demand, 2))

            # Recursive feedback: append predicted value to simulated demand series
            simulated_demands.append(pred_demand)

            # Prediction intervals (95% z ~ 1.65)
            margin = round(1.65 * res_std, 2)
            lower = max(0.0, round(pred_demand - margin, 2))
            upper = round(pred_demand + margin, 2)

            predictions.append({
                "date": target_date.isoformat(),
                "predicted_demand": pred_demand,
                "lower_bound": lower,
                "upper_bound": upper,
                "is_forecast": True,
            })

        return predictions
