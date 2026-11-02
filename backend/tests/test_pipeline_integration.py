"""End-to-End Pipeline Integration Test:
Tests the complete lifecycle: Transaction -> Stock Update -> Risk Re-evaluation -> Replenishment -> Alerting."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.db.base import Base
from backend.app.db.models.medicine import Medicine
from backend.app.db.models.category import Category
from backend.app.db.models.supplier import Supplier
from backend.app.db.models.inventory import InventoryCurrent
from backend.app.db.models.forecast import Forecast
from backend.app.services.transaction_service import TransactionService
from backend.app.services.risk_service import RiskService
from backend.app.services.replenishment_service import ReplenishmentService
from backend.app.services.alert_service import AlertEngine, AlertService
from backend.app.schemas.transaction import TransactionCreate
from backend.app.core.errors import AppException


@pytest.fixture
def pipeline_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    # Seed catalog
    cat = Category(category_id="CAT01", category_name="Cardiology", description="Cardio drugs")
    sup = Supplier(
        supplier_id="SUP01",
        supplier_name="Apex Pharma Distributors",
        supplier_type="Wholesaler",
        city="Mumbai",
        state="Maharashtra",
        lead_time_mean_days=4.0,
        lead_time_sd_days=1.0,
        on_time_probability=0.96,
        full_fill_probability=0.98,
        payment_terms_days=30,
        is_active=True,
    )
    med = Medicine(
        medicine_id="MED001",
        generic_name="Atorvastatin",
        display_name="Atorvastatin 20mg",
        strength="20mg",
        dosage_form="Tablet",
        category_id="CAT01",
        primary_supplier_id="SUP01",
        unit_cost_inr=20.0,
        unit_price_inr=35.0,
        is_active=True,
    )
    inv = InventoryCurrent(
        medicine_id="MED001",
        closing_stock=50,
        on_order_units=0,
        safety_stock=30,
        reorder_point=80,
        moq=40,
        expected_daily_demand=10.0,
        days_of_cover=5.0,
        stock_status="LOW_STOCK",
    )

    db.add_all([cat, sup, med, inv])
    db.commit()

    yield db
    db.close()


def test_full_operational_lifecycle(pipeline_db):
    """Executes the full chain from prescription dispensing transaction through replenishment order placement."""
    db = pipeline_db

    # 1. Negative stock rejection check
    tx_excess = TransactionCreate(
        medicine_id="MED001",
        transaction_type="SALE",
        quantity=999,
        reference_number="INV-FAIL-01",
    )
    with pytest.raises(AppException):
        TransactionService.create_transaction(db, tx_excess, user_name="Staff Tester")

    # 2. Valid Sale transaction: 50 -> 30 units
    tx_valid = TransactionCreate(
        medicine_id="MED001",
        transaction_type="SALE",
        quantity=20,
        reference_number="INV-2026-001",
        notes="Dispensed prescription",
    )
    tx_record = TransactionService.create_transaction(db, tx_valid, user_name="Staff Tester")
    assert tx_record.stock_after == 30

    inv = db.query(InventoryCurrent).filter(InventoryCurrent.medicine_id == "MED001").first()
    assert inv.closing_stock == 30

    # 3. Risk Run
    risk_summary = RiskService.run_all(db)
    assert risk_summary["status"] == "COMPLETED"

    risk_res = RiskService.get_by_medicine(db, "MED001")
    assert risk_res is not None
    assert risk_res["risk_level"] in ("HIGH", "CRITICAL", "MEDIUM")

    # 4. Replenishment generation
    repl_summary = ReplenishmentService.generate_recommendations(db)
    assert repl_summary["created"] >= 1

    recs = ReplenishmentService.list_recommendations(db, status="PENDING")
    assert len(recs) == 1
    rec = recs[0]
    assert rec["medicine_id"] == "MED001"
    assert rec["recommended_order_quantity"] >= rec["moq_applied"]

    # 5. Alert Engine run
    alert_summary = AlertEngine.evaluate_system_alerts(db)
    assert alert_summary["created"] >= 1

    alerts = AlertService.list_alerts(db)
    assert len(alerts) >= 1

    # 6. Accept recommendation and mark order placed
    accepted = ReplenishmentService.accept(db, rec["id"], by="Clinical Pharmacist")
    assert accepted["status"] == "ACCEPTED"

    ordered = ReplenishmentService.order_placed(db, rec["id"], po_ref="PO-2026-99")
    assert ordered["status"] == "ORDERED"

    # 7. Verify inventory position updated with open order
    db.refresh(inv)
    assert inv.on_order_units == rec["recommended_order_quantity"]
