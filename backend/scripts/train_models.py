"""CLI script for reproducible model training and backtesting."""

import os
import sys

# Ensure backend is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.db.session import SessionLocal
from backend.app.ml.train import MLTrainer


def main():
    print("=" * 70)
    print(" PharmaStock IQ — Machine Learning Training Pipeline")
    print("=" * 70)

    db = SessionLocal()
    try:
        print("[1/5] Loading and verifying dataset...")
        print("[2/5] Engineering temporal features and chronological splitting...")
        print("[3/5] Evaluating baselines & candidate models on 2024 validation set...")
        print("[4/5] Running benchmark verification and selecting champion model...")
        print("[5/5] Refitting on Train+Val, testing on 2025, and saving artifact...")

        results = MLTrainer.train_pipeline(db=db)

        print("\n" + "=" * 70)
        print(" TRAINING COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print(f" Run ID:             {results['run_id']}")
        print(f" Selected Champion:  {results['selected_model']}")
        print(f" Selection Reason:   {results['selection_reason']}")
        print(f" Validation MAE:     {results['val_mae']:.3f}")
        print(f" Test MAE (2025):    {results['test_metrics']['mae']:.3f}")
        print(f" Test RMSE:          {results['test_metrics']['rmse']:.3f}")
        print(f" Test WAPE:          {results['test_metrics']['wape']:.4f}")
        print(f" Test MAPE:          {results['test_metrics']['mape']:.4f}")
        print(f" Pipeline Duration:  {results['pipeline_duration_seconds']}s")
        print("-" * 70)
        print(" Benchmark Check:")
        print(f"   {results['reproduction_check']['note']}")
        print("=" * 70)
    finally:
        db.close()


if __name__ == "__main__":
    main()
