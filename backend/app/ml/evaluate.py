"""Model evaluation metrics: MAE, RMSE, MAPE (non-zero actuals), and WAPE."""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional


class ModelEvaluator:
    @staticmethod
    def calculate_mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        return float(np.mean(np.abs(y_true - y_pred)))

    @staticmethod
    def calculate_rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))

    @staticmethod
    def calculate_wape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        sum_actual = np.sum(y_true)
        if sum_actual == 0:
            return 0.0
        return float(np.sum(np.abs(y_true - y_pred)) / sum_actual)

    @staticmethod
    def calculate_mape_nonzero(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
        """MAPE computed strictly where y_true > 0, tracking number of zero actuals excluded."""
        mask = y_true > 0
        excluded = int(np.sum(~mask))
        if not np.any(mask):
            return {"mape": 0.0, "excluded_zeros_count": excluded}

        mape_val = float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])))
        return {
            "mape": round(mape_val, 4),
            "excluded_zeros_count": excluded,
        }

    @staticmethod
    def evaluate_predictions(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
        """Calculate complete suite of evaluation metrics."""
        y_true = np.array(y_true, dtype=float)
        y_pred = np.clip(np.array(y_pred, dtype=float), a_min=0, a_max=None)

        mae = ModelEvaluator.calculate_mae(y_true, y_pred)
        rmse = ModelEvaluator.calculate_rmse(y_true, y_pred)
        wape = ModelEvaluator.calculate_wape(y_true, y_pred)
        mape_dict = ModelEvaluator.calculate_mape_nonzero(y_true, y_pred)

        return {
            "mae": round(mae, 3),
            "rmse": round(rmse, 3),
            "wape": round(wape, 4),
            "mape": mape_dict["mape"],
            "mape_excluded_zeros": mape_dict["excluded_zeros_count"],
            "samples_count": len(y_true),
        }

    @staticmethod
    def calculate_medicine_residuals(
        df_eval: pd.DataFrame, y_true_col: str, y_pred_col: str
    ) -> Dict[str, float]:
        """
        Compute standard deviation of residuals per medicine on validation set.
        Used for prediction interval bounds and safety stock fallbacks.
        """
        std_map = {}
        for med_id, grp in df_eval.groupby("medicine_id"):
            residuals = grp[y_true_col] - grp[y_pred_col]
            std = float(residuals.std())
            std_map[med_id] = round(std if not np.isnan(std) else 1.0, 2)
        return std_map
