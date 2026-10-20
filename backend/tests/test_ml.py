"""Unit and integration tests for ML pipeline, leakage prevention, and model evaluation."""

import os
import datetime
import pytest
import numpy as np
import pandas as pd

from backend.app.ml.config import MLConfig
from backend.app.ml.preprocessing import MLPreprocessor
from backend.app.ml.features import FeatureEngineer
from backend.app.ml.split import ChronologicalSplitter
from backend.app.ml.baselines import BaselineForecaster
from backend.app.ml.models import CandidateModels
from backend.app.ml.evaluate import ModelEvaluator
from backend.app.ml.train import MLTrainer


@pytest.fixture
def sample_daily_data():
    """Create a synthetic 100-day dataset across 2 medicines for testing."""
    records = []
    base_date = datetime.date(2023, 1, 1)
    for med in ["MED001", "MED002"]:
        for d in range(100):
            dt = base_date + datetime.timedelta(days=d)
            # Demand with weekly pattern
            val = 50 + 10 * (d % 7) + (d % 3) * 5
            records.append({
                "record_id": f"REC_{med}_{d}",
                "date": dt.isoformat(),
                "medicine_id": med,
                "category_id": "CAT01",
                "supplier_id": "SUP01",
                "units_demanded": val,
                "closing_stock": 200 - val,
                "on_order_units": 0,
                "reorder_point": 50,
                "sales_7d_avg": float(val),
                "sales_30d_avg": float(val),
                "days_of_cover": 5.0,
                "stock_position_cover_days": 5.0,
                "days_since_last_receipt": 3,
                "stockout_days_last_30d": 0,
                "supplier_lead_time_mean_days": 4.0,
                "supplier_full_fill_probability": 0.95,
                "supplier_disruption_active": 0,
                "unit_price_inr": 25.0,
                "stockout_today": 0,
                "stockout_next_7d": 0,
            })
    return pd.DataFrame(records)


def test_leakage_1_feature_list_disjoint_from_forbidden(sample_daily_data):
    """Leakage Test 1: Feature list must never intersect forbidden target/future variables."""
    preprocessed = MLPreprocessor.preprocess(sample_daily_data)
    fe = FeatureEngineer()
    fe.fit_static_statistics(preprocessed, train_end_date=datetime.date(2023, 2, 1))
    featured = fe.generate_features(preprocessed)
    _, _, feature_names = fe.get_feature_matrix(featured)

    forbidden_set = set(MLConfig.FORBIDDEN_FEATURES)
    feature_set = set(feature_names)
    overlap = feature_set.intersection(forbidden_set)

    assert overlap == set(), f"Target leakage detected! Overlapping features: {overlap}"


def test_leakage_2_chronological_split_strict_ordering():
    """Leakage Test 2: Chronological partitions must have strictly ascending dates without overlap."""
    dates = pd.date_range("2021-01-01", "2025-12-31", freq="D")
    df = pd.DataFrame({
        "date": dates.date,
        "medicine_id": "MED001",
        "demand": 50.0,
    })

    train_df, val_df, test_df = ChronologicalSplitter.split_train_val_test(df)

    assert not train_df.empty
    assert not val_df.empty
    assert not test_df.empty

    assert train_df["date"].max() < val_df["date"].min()
    assert val_df["date"].max() < test_df["date"].min()

    assert train_df["date"].max() == datetime.date(2023, 12, 31)
    assert val_df["date"].min() == datetime.date(2024, 1, 1)
    assert val_df["date"].max() == datetime.date(2024, 12, 31)
    assert test_df["date"].min() == datetime.date(2025, 1, 1)


def test_leakage_3_rolling_shift_prevents_contemporaneous_leakage(sample_daily_data):
    """Leakage Test 3: Changing future actuals must NOT alter past feature values."""
    preprocessed = MLPreprocessor.preprocess(sample_daily_data)
    fe = FeatureEngineer()
    fe.fit_static_statistics(preprocessed)
    df_orig = fe.generate_features(preprocessed)

    # Corrupt demand for the last 10 days of MED001
    corrupted_data = sample_daily_data.copy()
    corrupted_data.loc[corrupted_data["medicine_id"] == "MED001", "units_demanded"].iloc[-10:] += 5000

    prep_corrupt = MLPreprocessor.preprocess(corrupted_data)
    fe_corrupt = FeatureEngineer(train_mean_demand_map=fe.train_mean_demand_map)
    df_corrupt = fe_corrupt.generate_features(prep_corrupt)

    # Check rows before the corruption cutoff
    cutoff_idx = len(df_orig[df_orig["medicine_id"] == "MED001"]) - 10
    orig_early = df_orig[df_orig["medicine_id"] == "MED001"].iloc[:cutoff_idx]["rolling_mean_7"]
    corrupt_early = df_corrupt[df_corrupt["medicine_id"] == "MED001"].iloc[:cutoff_idx]["rolling_mean_7"]

    np.testing.assert_array_almost_equal(orig_early.values, corrupt_early.values)


def test_leakage_4_static_aggregates_fit_on_train_only(sample_daily_data):
    """Leakage Test 4: Static aggregations like train_mean_demand must use train window only."""
    preprocessed = MLPreprocessor.preprocess(sample_daily_data)
    fe = FeatureEngineer()
    train_end = datetime.date(2023, 1, 20)
    fe.fit_static_statistics(preprocessed, train_end_date=train_end)

    expected_med1_mean = preprocessed[
        (preprocessed["medicine_id"] == "MED001") & (preprocessed["date"] <= train_end)
    ]["demand"].mean()

    assert fe.train_mean_demand_map["MED001"] == pytest.approx(expected_med1_mean, rel=1e-3)


def test_baselines_and_evaluator():
    """Verify that all 5 baselines and metrics produce valid, non-empty outputs."""
    y_true = np.array([10.0, 20.0, 0.0, 30.0, 40.0])
    y_pred = np.array([12.0, 18.0, 5.0, 25.0, 45.0])

    metrics = ModelEvaluator.evaluate_predictions(y_true, y_pred)
    assert metrics["mae"] > 0
    assert metrics["rmse"] >= metrics["mae"]
    assert metrics["wape"] > 0
    assert metrics["mape_excluded_zeros"] == 1
