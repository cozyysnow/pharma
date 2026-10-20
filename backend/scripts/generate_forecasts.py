"""CLI script to generate 30-day operational demand forecasts for all medicines using the active model."""

import os
import sys
import uuid
import datetime
import pandas as pd

# Ensure backend is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.db.session import SessionLocal
from backend.app.db.models.medicine import Medicine
from backend.app.db.models.daily_record import DailyRecord
from backend.app.db.models.forecast import Forecast, MLRun
from backend.app.ml.registry import ModelRegistry
from backend.app.ml.forecast import ForecastGenerator
from backend.app.ml.preprocessing import MLPreprocessor
from backend.app.ml.train import MLTrainer


def main():
    print("=" * 70)
    print(" PharmaStock IQ — Operational Forecast Generation Pipeline")
    print("=" * 70)

    db = SessionLocal()
    try:
        # 1. Retrieve Active Model Run
        active_run = db.query(MLRun).filter(MLRun.is_active == True).first()
        if not active_run:
            # Check registry for any saved artifact
            artifacts = ModelRegistry.list_artifacts()
            if not artifacts:
                print("No active model found. Training initial models first...")
                MLTrainer.train_pipeline(db=db)
                active_run = db.query(MLRun).filter(MLRun.is_active == True).first()
            else:
                active_run_id = artifacts[0]["run_id"]
                model_name = artifacts[0]["selected_model"]
        else:
            active_run_id = active_run.run_id
            model_name = active_run.model_name

        print(f"Using Active Model: {model_name} (Run ID: {active_run_id})")

        # 2. Load Model Artifact & Metadata
        fitted_model, metadata = ModelRegistry.load_artifact(active_run_id)
        feature_names = metadata["feature_names"]
        train_mean_map = metadata.get("train_mean_demand_map", {})
        residual_std_map = metadata.get("residual_std_map", {})

        generator = ForecastGenerator(
            fitted_model=fitted_model,
            feature_names=feature_names,
            train_mean_demand_map=train_mean_map,
            residual_std_map=residual_std_map,
        )

        # 3. Load Recent History for all medicines
        csv_path = MLTrainer.get_dataset_csv_path()
        df = MLPreprocessor.load_raw_dataset(csv_path)

        medicines = db.query(Medicine.medicine_id).all()
        med_ids = [m[0] for m in medicines]
        if not med_ids:
            med_ids = list(df["medicine_id"].unique())

        print(f"Generating 30-day recursive forecasts for {len(med_ids)} medicines...")

        # 4. Generate forecasts for all medicines
        total_points = 0
        forecast_objects = []
        as_of_date = datetime.date(2025, 12, 31)

        # Clear existing forecasts for this run_id
        db.query(Forecast).filter(Forecast.run_id == active_run_id).delete()
        db.commit()

        for med_id in med_ids:
            try:
                points = generator.generate_recursive_forecast(
                    historical_df=df,
                    medicine_id=med_id,
                    horizon_days=30,
                    as_of_date=as_of_date,
                )
                for pt in points:
                    f_id = f"FC_{med_id}_{pt['date'].replace('-', '')}"
                    forecast_objects.append(
                        Forecast(
                            forecast_id=f_id,
                            run_id=active_run_id,
                            medicine_id=med_id,
                            model_name=model_name,
                            forecast_date=datetime.date.fromisoformat(pt["date"]),
                            horizon_days=30,
                            predicted_demand=pt["predicted_demand"],
                            lower_bound=pt["lower_bound"],
                            upper_bound=pt["upper_bound"],
                            is_forecast=True,
                        )
                    )
                    total_points += 1
            except Exception as e:
                print(f"Warning: could not forecast for {med_id}: {e}")

        # Bulk insert forecast records
        db.bulk_save_objects(forecast_objects)
        db.commit()

        print("=" * 70)
        print(f" FORECAST GENERATION COMPLETE: {total_points:,} points persisted across {len(med_ids)} medicines.")
        print(f" Forecast period: 2026-01-01 to 2026-01-30")
        print("=" * 70)
    finally:
        db.close()


if __name__ == "__main__":
    main()
