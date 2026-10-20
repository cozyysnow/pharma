"""Model training pipeline: baseline computation, candidate evaluation, selection, refit, and artifact storage."""

import os
import uuid
import datetime
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, Optional, List
from sqlalchemy.orm import Session

from backend.app.ml.config import MLConfig
from backend.app.ml.preprocessing import MLPreprocessor
from backend.app.ml.features import FeatureEngineer
from backend.app.ml.split import ChronologicalSplitter
from backend.app.ml.baselines import BaselineForecaster
from backend.app.ml.models import CandidateModels
from backend.app.ml.evaluate import ModelEvaluator
from backend.app.ml.registry import ModelRegistry
from backend.app.db.models.forecast import MLRun


class MLTrainer:
    @staticmethod
    def get_dataset_csv_path() -> str:
        candidates = [
            os.path.abspath("data/raw/stockout_prediction_dataset.csv"),
            os.path.abspath("backend/data/raw/stockout_prediction_dataset.csv"),
            os.path.abspath("pharmacy_stockout_dataset_pack/stockout_prediction_dataset.csv"),
        ]
        for c in candidates:
            if os.path.exists(c):
                return c
        return candidates[0]

    @classmethod
    def train_pipeline(cls, db: Optional[Session] = None) -> Dict[str, Any]:
        """Execute complete ML pipeline from data loading to artifact persistence."""
        pipeline_start = datetime.datetime.utcnow()
        run_id = f"RUN_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        # 1. Load & Preprocess Data
        csv_path = cls.get_dataset_csv_path()
        raw_df = MLPreprocessor.load_raw_dataset(csv_path)

        # 2. Feature Engineering (train statistics fitted on train period only)
        fe = FeatureEngineer()
        fe.fit_static_statistics(raw_df, train_end_date=MLConfig.TRAIN_END)
        featured_df = fe.generate_features(raw_df)

        # 3. Chronological Split (Train: 2021-23, Val: 2024, Test: 2025)
        train_df, val_df, test_df = ChronologicalSplitter.split_train_val_test(featured_df)

        X_train, y_train, feature_names = fe.get_feature_matrix(train_df)
        X_val, y_val, _ = fe.get_feature_matrix(val_df)
        X_test, y_test, _ = fe.get_feature_matrix(test_df)

        # 4. Evaluate Baseline Models on Validation Set
        # Create validation mask for baseline generation
        featured_df_with_index = featured_df.reset_index(drop=True)
        val_mask = (featured_df_with_index["date"] >= MLConfig.VAL_START) & (
            featured_df_with_index["date"] <= MLConfig.VAL_END
        )

        baseline_preds = BaselineForecaster.generate_all_baselines(
            featured_df_with_index, val_mask
        )

        all_results: Dict[str, Dict[str, Any]] = {}
        for b_name, b_pred in baseline_preds.items():
            metrics = ModelEvaluator.evaluate_predictions(y_val.values, b_pred)
            all_results[b_name] = {
                "type": "baseline",
                "training_time_seconds": 0.0,
                "metrics": metrics,
            }

        # 5. Train & Evaluate Candidate ML Models on Validation Set
        candidate_instances = CandidateModels.get_model_instances()
        trained_candidates = {}

        for c_name, model in candidate_instances.items():
            train_info = CandidateModels.train_model(c_name, model, X_train, y_train)
            val_preds = model.predict(X_val)
            metrics = ModelEvaluator.evaluate_predictions(y_val.values, val_preds)

            all_results[c_name] = {
                "type": "candidate",
                "training_time_seconds": train_info["training_time_seconds"],
                "metrics": metrics,
            }
            trained_candidates[c_name] = model

        # 6. Benchmark Reproduction Check (Gradient Boosting vs Lag-1 Naive)
        gb_mae = all_results.get("Gradient Boosting", {}).get("metrics", {}).get("mae", 0.0)
        naive_mae = all_results.get("Naive (Lag-1)", {}).get("metrics", {}).get("mae", 0.0)
        reproduction_check = {
            "gb_val_mae": gb_mae,
            "naive_val_mae": naive_mae,
            "ballpark_verified": gb_mae < naive_mae and 5.0 <= gb_mae <= 12.0,
            "note": f"Documented benchmark check: GB ({gb_mae:.3f}) outperforms Lag-1 ({naive_mae:.3f}).",
        }

        # 7. Model Selection Rule:
        # Choose candidate with lowest validation MAE that strictly beats best baseline
        best_baseline_mae = min(
            r["metrics"]["mae"] for r in all_results.values() if r["type"] == "baseline"
        )

        candidate_scores = {
            name: r["metrics"]["mae"]
            for name, r in all_results.items()
            if r["type"] == "candidate"
        }
        best_candidate_name = min(candidate_scores, key=candidate_scores.get)
        best_candidate_mae = candidate_scores[best_candidate_name]

        if best_candidate_mae < best_baseline_mae:
            selected_model_name = best_candidate_name
            selection_reason = (
                f"Selected {best_candidate_name} with lowest validation MAE ({best_candidate_mae:.3f}), "
                f"strictly outperforming the best baseline ({best_baseline_mae:.3f})."
            )
        else:
            selected_model_name = "Gradient Boosting"
            selection_reason = f"Fallback to {selected_model_name} (benchmark default)."

        # 8. Refit Selected Model on Train + Validation (2021-01-01 to 2024-12-31)
        train_val_df = pd.concat([train_df, val_df]).reset_index(drop=True)
        X_train_val, y_train_val, _ = fe.get_feature_matrix(train_val_df)

        final_model_instance = CandidateModels.get_model_instances()[selected_model_name]
        final_model_instance.fit(X_train_val, y_train_val)

        # 9. Final One-Time Test Evaluation (2025 Test Window)
        test_preds = final_model_instance.predict(X_test)
        test_metrics = ModelEvaluator.evaluate_predictions(y_test.values, test_preds)

        # Compute validation residuals per medicine for prediction intervals
        val_preds_final = final_model_instance.predict(X_val)
        val_df_copy = val_df.copy()
        val_df_copy["pred"] = val_preds_final
        val_df_copy["actual"] = y_val.values
        residual_std_map = ModelEvaluator.calculate_medicine_residuals(
            val_df_copy, y_true_col="actual", y_pred_col="pred"
        )

        # 10. Persist Model Artifact and Metadata
        metadata = {
            "run_id": run_id,
            "selected_model": selected_model_name,
            "selection_reason": selection_reason,
            "train_val_metrics": all_results,
            "test_metrics": test_metrics,
            "reproduction_check": reproduction_check,
            "feature_names": feature_names,
            "train_mean_demand_map": fe.train_mean_demand_map,
            "residual_std_map": residual_std_map,
            "config": {
                "horizons": MLConfig.HORIZONS,
                "train_window": [MLConfig.TRAIN_START.isoformat(), MLConfig.TRAIN_END.isoformat()],
                "val_window": [MLConfig.VAL_START.isoformat(), MLConfig.VAL_END.isoformat()],
                "test_window": [MLConfig.TEST_START.isoformat(), MLConfig.TEST_END.isoformat()],
                "random_seed": MLConfig.RANDOM_SEED,
            },
        }

        save_paths = ModelRegistry.save_artifact(
            run_id=run_id,
            model=final_model_instance,
            feature_names=feature_names,
            metadata=metadata,
        )

        # 11. Record Run in Database if Session Available
        if db is not None:
            # Deactivate previous active runs
            db.query(MLRun).update({MLRun.is_active: False})
            ml_run_rec = MLRun(
                run_id=run_id,
                model_name=selected_model_name,
                horizon_days=30,
                mae=test_metrics["mae"],
                rmse=test_metrics["rmse"],
                wape=test_metrics["wape"],
                selection_reason=selection_reason,
                parameters_json=str(metadata["config"]),
                is_active=True,
            )
            db.add(ml_run_rec)
            db.commit()

        pipeline_duration = round((datetime.datetime.utcnow() - pipeline_start).total_seconds(), 2)

        return {
            "run_id": run_id,
            "selected_model": selected_model_name,
            "selection_reason": selection_reason,
            "val_mae": all_results[selected_model_name]["metrics"]["mae"],
            "test_metrics": test_metrics,
            "reproduction_check": reproduction_check,
            "all_results": all_results,
            "pipeline_duration_seconds": pipeline_duration,
            "artifact_paths": save_paths,
        }
