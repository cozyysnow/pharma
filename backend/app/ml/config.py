"""ML Configuration: horizons, chronological split dates, random seeds, and feature lists."""

import datetime
from typing import List, Dict, Any


class MLConfig:
    # Random seed for reproducible training
    RANDOM_SEED: int = 42

    # Forecast horizons (days)
    HORIZONS: List[int] = [1, 7, 14, 30]
    DEFAULT_HORIZON: int = 30

    # Chronological Split Dates (Section 12.5)
    TRAIN_START: datetime.date = datetime.date(2021, 1, 1)
    TRAIN_END: datetime.date = datetime.date(2023, 12, 31)

    VAL_START: datetime.date = datetime.date(2024, 1, 1)
    VAL_END: datetime.date = datetime.date(2024, 12, 31)

    TEST_START: datetime.date = datetime.date(2025, 1, 1)
    TEST_END: datetime.date = datetime.date(2025, 12, 31)

    # Lags to compute (days)
    LAGS: List[int] = [1, 2, 3, 7, 14, 21, 28]

    # Rolling window sizes (days) on shift(1)
    ROLLING_WINDOWS: List[int] = [3, 7, 14, 28]

    # Calendar features known in advance
    CALENDAR_FEATURES: List[str] = [
        "day_of_week",
        "day_of_month",
        "month",
        "quarter",
        "is_weekend",
        "day_of_year_sin",
        "day_of_year_cos",
    ]

    # Static medicine features (categorical or constant)
    STATIC_FEATURES: List[str] = [
        "category_id",
        "supplier_id",
        "supplier_lead_time_mean_days",
        "train_mean_demand",
    ]

    # Trend and Seasonal features
    TREND_SEASONAL_FEATURES: List[str] = [
        "rolling_ratio_7_28",
        "time_index",
        "same_weekday_lag_7",
        "same_weekday_lag_14",
    ]

    # Target variable for demand regression
    TARGET_COLUMN: str = "demand"

    # Columns strictly forbidden as model inputs for day >= t (Data leakage prevention, Sec 12.4)
    FORBIDDEN_FEATURES: List[str] = [
        "demand",
        "units_demanded",
        "quantity_sold",
        "units_sold",
        "unmet_demand",
        "lost_sales_units",
        "stockout_today",
        "stockout_next_7d",
        "stockout_flag",
        "closing_stock",
        "days_of_cover",
        "stock_position_cover_days",
        "required_stock",
        "lead_time_demand",
        "safety_stock",
        "shortfall",
        "risk_score",
        "risk_level",
        "risk_label",
    ]
