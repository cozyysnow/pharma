"""Candidate ML models for demand forecasting: Linear Regression, Random Forest, Gradient Boosting."""

import time
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from backend.app.ml.config import MLConfig


class CandidateModels:
    @staticmethod
    def get_model_instances() -> Dict[str, Any]:
        """Returns dict of model candidate instances configured with reproducible random seeds."""
        return {
            "Linear Regression": Ridge(alpha=1.0, random_state=MLConfig.RANDOM_SEED),
            "Random Forest": RandomForestRegressor(
                n_estimators=100,
                max_depth=12,
                min_samples_split=10,
                random_state=MLConfig.RANDOM_SEED,
                n_jobs=-1,
            ),
            "Gradient Boosting": HistGradientBoostingRegressor(
                max_iter=150,
                max_depth=8,
                learning_rate=0.08,
                min_samples_leaf=20,
                random_state=MLConfig.RANDOM_SEED,
            ),
        }

    @staticmethod
    def train_model(
        model_name: str,
        model: Any,
        X_train: pd.DataFrame,
        y_train: pd.Series,
    ) -> Dict[str, Any]:
        """Fit model and record training duration and parameters."""
        start_time = time.time()
        model.fit(X_train, y_train)
        duration = round(time.time() - start_time, 2)

        return {
            "model_name": model_name,
            "fitted_model": model,
            "training_time_seconds": duration,
            "feature_names": list(X_train.columns),
            "train_samples": len(X_train),
        }
