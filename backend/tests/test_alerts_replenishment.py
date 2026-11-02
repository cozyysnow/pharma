"""Tests for Alerts Engine, Replenishment calculations, and human workflow transitions."""

import pytest
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.db.base import Base
from backend.app.db.models.medicine import Medicine
from backend.app.db.models.category import Category
from backend.app.db.models.supplier import Supplier
from backend.app.db.models.inventory import InventoryCurrent
from backend.app.db.models.risk import RiskResult
from backend.app.db.models.replenishment import ReplenishmentRecommendation
from backend.app.db.models.alert import Alert
from backend.app.services.replenishment_service import ReplenishmentService
from backend.app.services.alert_service import AlertEngine, AlertService
from backend.app.core.errors import AppException


@pytest.fixture
def isolated_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Seed minimal entities
    cat = Category(category_id="CAT01", category_name="Cardiology", description="Heart meds")
    sup = Supplier(
        supplier_id="SUP01",
        supplier_name="Apex Pharma Distributors",
        supplier_type="Wholesaler",
        city="Mumbai",
        state="Maharashtra",
        lead_time_mean_days=5.0,
        lead_time_sd_days=1.0,
        on_time_probability=0.95,
        full_fill_probability=0.98,
        payment_terms_days=30,
        is_active=True,
    )
    med = Medicine(
        medicine_id="MED999",
        generic_name="Atorvastatin",
        display_name="Atorvastatin 20mg",
        strength="20mg",
        dosage_form="Tablet",
        route="Oral",
        category_id="CAT01",
        primary_supplier_id="SUP01",
        unit_of_measure="strip",
        pack_size=10,
        storage_condition="Room Temperature",
        unit_cost_inr=30.0,
        unit_price_inr=50.0,
        is_active=True,
    )
    inv = InventoryCurrent(
        medicine_id="MED999",
        closing_stock=20,
        on_order_units=0,
        safety_stock=50,
        reorder_point=100,
        order_up_to_level=400,
        days_of_cover=2.0,
        stock_status="LOW_STOCK",
        moq=50,
        expected_daily_demand=10.0,
    )
    risk = RiskResult(
        risk_id="RISK_MED999",
        medicine_id="MED999",
        calculated_at=datetime.datetime.utcnow(),
        risk_score=85,
        risk_level="HIGH",
        expected_daily_demand=10.0,
        stock_coverage_days=2.0,
        lead_time_days=5.0,
        safety_stock=50,
        required_stock=100,
        explanation="High risk of stockout.",
    )

    session.add_all([cat, sup, med, inv, risk])
    session.commit()

    yield session
    session.close()


def test_replenishment_math_and_moq_rounding(isolated_db):
    """Raw need = required (100) - stock (20) - open (0) = 80.
    Since 80 >= MOQ (50), recommended qty is 80."""
    result = ReplenishmentService.generate_recommendations(isolated_db)
    assert result["created"] == 1

    recs = ReplenishmentService.list_recommendations(isolated_db)
    assert len(recs) == 1
    rec = recs[0]
    assert rec["medicine_id"] == "MED999"
    assert rec["recommended_order_quantity"] == 80
    assert rec["status"] == "PENDING"
    assert rec["is_urgent"] == True  # days_of_cover (2.0) < lead_time (5.0)


def test_moq_enforcement_when_need_is_smaller_than_moq(isolated_db):
    """If required = 100, stock = 80, raw need = 20. But MOQ = 50 -> must order 50."""
    inv = isolated_db.query(InventoryCurrent).filter(InventoryCurrent.medicine_id == "MED999").first()
    inv.closing_stock = 80
    isolated_db.commit()

    ReplenishmentService.generate_recommendations(isolated_db)
    recs = ReplenishmentService.list_recommendations(isolated_db)
    rec = recs[0]
    assert rec["recommended_order_quantity"] == 50  # MOQ applied


def test_replenishment_workflow_transitions(isolated_db):
    """Verify strictly enforced human-in-the-loop workflow:
    PENDING -> ACCEPTED -> ORDERED, updating on_order_units in inventory."""
    ReplenishmentService.generate_recommendations(isolated_db)
    rec = ReplenishmentService.list_recommendations(isolated_db)[0]
    rec_id = rec["id"]

    # 1. Accept
    accepted = ReplenishmentService.accept(isolated_db, rec_id, by="Pharmacy Manager")
    assert accepted["status"] == "ACCEPTED"
    assert accepted["accepted_by"] == "Pharmacy Manager"

    # Cannot re-accept or dismiss once accepted
    with pytest.raises(AppException):
        ReplenishmentService.accept(isolated_db, rec_id)

    # 2. Mark Order Placed
    inv_before = isolated_db.query(InventoryCurrent).filter(InventoryCurrent.medicine_id == "MED999").first()
    initial_on_order = inv_before.on_order_units

    ordered = ReplenishmentService.order_placed(isolated_db, rec_id, po_ref="PO-2026-001")
    assert ordered["status"] == "ORDERED"
    assert ordered["po_reference"] == "PO-2026-001"

    # Check inventory on_order_units increased atomically
    inv_after = isolated_db.query(InventoryCurrent).filter(InventoryCurrent.medicine_id == "MED999").first()
    assert inv_after.on_order_units == initial_on_order + ordered["recommended_order_quantity"]


def test_replenishment_dismiss_workflow(isolated_db):
    """Verify dismissal with required reason."""
    ReplenishmentService.generate_recommendations(isolated_db)
    rec = ReplenishmentService.list_recommendations(isolated_db)[0]
    rec_id = rec["id"]

    dismissed = ReplenishmentService.dismiss(isolated_db, rec_id, reason="Alternative therapeutic equivalent in stock")
    assert dismissed["status"] == "DISMISSED"
    assert dismissed["dismiss_reason"] == "Alternative therapeutic equivalent in stock"


def test_alert_engine_triggers_and_deduplication(isolated_db):
    """Alert engine must create HIGH_RISK and LOW_STOCK alerts, and deduplicate on rerun."""
    res1 = AlertEngine.evaluate_system_alerts(isolated_db)
    assert res1["created"] >= 2  # HIGH_RISK + LOW_STOCK

    alerts = AlertService.list_alerts(isolated_db)
    types = [a["alert_type"] for a in alerts]
    assert "HIGH_RISK" in types
    assert "LOW_STOCK" in types

    # Rerunning engine must NOT duplicate alerts, but update them
    res2 = AlertEngine.evaluate_system_alerts(isolated_db)
    assert res2["created"] == 0
    assert res2["updated"] >= 2


def test_alert_auto_resolve_when_condition_clears(isolated_db):
    """When risk drops to LOW and stock is healthy, active alerts must auto-resolve."""
    AlertEngine.evaluate_system_alerts(isolated_db)
    assert AlertService.get_unread_count(isolated_db) >= 2

    # Restock inventory and reduce risk
    inv = isolated_db.query(InventoryCurrent).filter(InventoryCurrent.medicine_id == "MED999").first()
    inv.closing_stock = 500
    inv.stock_status = "IN_STOCK"
    risk = isolated_db.query(RiskResult).filter(RiskResult.medicine_id == "MED999").first()
    risk.risk_level = "LOW"
    risk.risk_score = 10
    isolated_db.commit()

    # Rerun engine
    res = AlertEngine.evaluate_system_alerts(isolated_db)
    assert res["resolved"] >= 2

    # Verify alerts transitioned to RESOLVED
    alerts = AlertService.list_alerts(isolated_db, status="RESOLVED")
    assert len(alerts) >= 2
    for a in alerts:
        assert a["resolved_by"] == "System Auto-Resolve"
