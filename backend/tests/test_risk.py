"""Unit tests for stock-out risk calculations, edge cases, and deterministic formulas."""

import pytest
import datetime
from unittest.mock import MagicMock

from backend.app.services.risk_service import RiskCalculator
from backend.app.db.models.medicine import Medicine
from backend.app.db.models.inventory import InventoryCurrent
from backend.app.db.models.supplier import Supplier
from backend.app.db.models.forecast import Forecast


def create_mock_medicine(med_id="MED001", name="Paracetamol 500mg"):
    med = MagicMock(spec=Medicine)
    med.medicine_id = med_id
    med.display_name = name
    med.generic_name = name
    return med


def create_mock_inventory(closing_stock=100, safety_stock=50, reorder_point=150, on_order=0):
    inv = MagicMock(spec=InventoryCurrent)
    inv.closing_stock = closing_stock
    inv.safety_stock = safety_stock
    inv.reorder_point = reorder_point
    inv.on_order_units = on_order
    inv.expected_daily_demand = 10.0
    return inv


def create_mock_supplier(lead_time_days=5.0, on_time_prob=0.95):
    sup = MagicMock(spec=Supplier)
    sup.lead_time_mean_days = lead_time_days
    sup.lead_time_sd_days = 1.0
    sup.on_time_probability = on_time_prob
    return sup


def create_mock_forecasts(daily_demand=20.0, days=30):
    base_date = datetime.date(2026, 1, 1)
    fcs = []
    for d in range(days):
        fc = MagicMock(spec=Forecast)
        fc.forecast_date = base_date + datetime.timedelta(days=d)
        fc.predicted_demand = daily_demand
        fcs.append(fc)
    return fcs


def test_hand_computed_risk_case():
    """Verify Section 14 & 15 exact math on hand-computed scenario:
    S = 120, L = 7 days, daily forecast = 20.0, safety stock = 50.
    LTD = 140, Required = 190. Since 120 < 140, Risk must be HIGH."""
    med = create_mock_medicine()
    inv = create_mock_inventory(closing_stock=120, safety_stock=50)
    sup = create_mock_supplier(lead_time_days=7.0)
    fcs = create_mock_forecasts(daily_demand=20.0, days=30)

    result = RiskCalculator.calculate_medicine_risk(med, inv, sup, fcs)

    assert result["expected_daily_demand"] == 20.0
    assert result["lead_time_demand"] == 140.0
    assert result["stock_coverage_days"] == 6.0  # 120 / 20 = 6.0 days
    assert result["required_stock"] == 190       # 140 + 50
    assert result["risk_level"] in ("HIGH", "CRITICAL")
    assert result["risk_score"] >= 70
    assert result["shortfall"] == 70             # 190 - 120
    assert "120 units on hand" in result["explanation"]
    assert "140.0 units" in result["explanation"]


def test_zero_stock_edge_case():
    """Stock = 0 must result in CRITICAL risk, score = 100, and 100% stockout probability."""
    med = create_mock_medicine()
    inv = create_mock_inventory(closing_stock=0)
    sup = create_mock_supplier()
    fcs = create_mock_forecasts(daily_demand=15.0)

    result = RiskCalculator.calculate_medicine_risk(med, inv, sup, fcs)

    assert result["risk_level"] == "CRITICAL"
    assert result["risk_score"] == 100
    assert result["stock_coverage_days"] == 0.0
    assert result["days_until_stockout"] == 0.0
    assert result["stockout_probability_7d"] == 1.0


def test_negative_stock_edge_case():
    """Negative stock (data anomaly) must be flagged as CRITICAL risk score 100."""
    med = create_mock_medicine()
    inv = create_mock_inventory(closing_stock=-5)
    sup = create_mock_supplier()
    fcs = create_mock_forecasts(daily_demand=10.0)

    result = RiskCalculator.calculate_medicine_risk(med, inv, sup, fcs)

    assert result["risk_level"] == "CRITICAL"
    assert result["risk_score"] == 100
    assert result["stockout_probability_7d"] == 1.0


def test_zero_demand_edge_case():
    """When demand is zero, coverage must be capped at 999.0 and risk must be LOW."""
    med = create_mock_medicine()
    inv = create_mock_inventory(closing_stock=50, safety_stock=20)
    sup = create_mock_supplier()
    fcs = create_mock_forecasts(daily_demand=0.0)

    result = RiskCalculator.calculate_medicine_risk(med, inv, sup, fcs)

    assert result["expected_daily_demand"] == 0.0
    assert result["stock_coverage_days"] == 999.0
    assert result["risk_level"] == "LOW"
    assert result["risk_score"] == 0


def test_lead_time_exceeds_horizon_edge_case():
    """When L > available forecast horizon (e.g. L=15, horizon=7), calculator uses available horizon."""
    med = create_mock_medicine()
    inv = create_mock_inventory(closing_stock=100)
    sup = create_mock_supplier(lead_time_days=15.0)
    fcs = create_mock_forecasts(daily_demand=10.0, days=7)  # only 7 days

    result = RiskCalculator.calculate_medicine_risk(med, inv, sup, fcs)

    assert result["lead_time_demand"] == 70.0  # 7 * 10
    assert result["expected_daily_demand"] == 10.0
    assert result["stock_coverage_days"] == 10.0


def test_medium_risk_covers_lead_time_but_eats_safety_stock():
    """S >= LTD but S < required_stock must be classified as MEDIUM."""
    med = create_mock_medicine()
    # LTD = 5 * 20 = 100. Safety stock = 50 -> Required = 150.
    # Current stock = 120 (covers 100, but less than 150)
    inv = create_mock_inventory(closing_stock=120, safety_stock=50)
    sup = create_mock_supplier(lead_time_days=5.0)
    fcs = create_mock_forecasts(daily_demand=20.0, days=30)

    result = RiskCalculator.calculate_medicine_risk(med, inv, sup, fcs)

    assert result["risk_level"] == "MEDIUM"
    assert 30 <= result["risk_score"] <= 69


def test_low_risk_healthy_stock():
    """S >= required_stock must be classified as LOW risk."""
    med = create_mock_medicine()
    # LTD = 100, Required = 150, Current = 300
    inv = create_mock_inventory(closing_stock=300, safety_stock=50)
    sup = create_mock_supplier(lead_time_days=5.0)
    fcs = create_mock_forecasts(daily_demand=20.0, days=30)

    result = RiskCalculator.calculate_medicine_risk(med, inv, sup, fcs)

    assert result["risk_level"] == "LOW"
    assert result["risk_score"] < 30

