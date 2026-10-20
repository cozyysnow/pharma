import pytest
from backend.app.core.security import create_access_token
from backend.app.db.models.inventory import InventoryCurrent


@pytest.fixture
def admin_headers(admin_user):
    token = create_access_token(subject=admin_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def staff_headers(staff_user):
    token = create_access_token(subject=staff_user.id)
    return {"Authorization": f"Bearer {token}"}


def test_category_and_supplier_crud(client, admin_headers, staff_headers):
    # Staff cannot create category
    res = client.post(
        "/api/v1/categories",
        json={"category_id": "TEST_CAT", "category_name": "Test Antibiotics", "description": "Testing category"},
        headers=staff_headers,
    )
    assert res.status_code == 403

    # Admin can create category
    res = client.post(
        "/api/v1/categories",
        json={"category_id": "TEST_CAT", "category_name": "Test Antibiotics", "description": "Testing category"},
        headers=admin_headers,
    )
    assert res.status_code == 201
    assert res.json()["category_id"] == "TEST_CAT"

    # Anyone can list categories
    res = client.get("/api/v1/categories")
    assert res.status_code == 200
    cats = res.json()
    assert any(c["category_id"] == "TEST_CAT" for c in cats)

    # Admin creates supplier
    res = client.post(
        "/api/v1/suppliers",
        json={
            "supplier_id": "SUP_TEST",
            "supplier_name": "Apex Pharma Dist",
            "supplier_type": "Wholesaler",
            "city": "Mumbai",
            "state": "Maharashtra",
            "lead_time_mean_days": 3.5,
            "lead_time_sd_days": 0.8,
            "on_time_probability": 0.95,
            "full_fill_probability": 0.92,
            "payment_terms_days": 30,
        },
        headers=admin_headers,
    )
    assert res.status_code == 201
    assert res.json()["supplier_id"] == "SUP_TEST"


def test_medicine_and_inventory_initialization(client, admin_headers, db_session):
    # Create medicine
    payload = {
        "medicine_id": "MED_AMOX_500",
        "generic_name": "Amoxicillin",
        "display_name": "Amoxicillin 500mg Capsule",
        "strength": "500mg",
        "dosage_form": "Capsule",
        "route": "Oral",
        "category_id": "TEST_CAT",
        "primary_supplier_id": "SUP_TEST",
        "unit_of_measure": "strip",
        "pack_size": 10,
        "storage_condition": "Room Temperature",
        "unit_cost_inr": 45.0,
        "unit_price_inr": 72.0,
        "composition_status": "VERIFIED_STANDARD_REFERENCE",
    }
    res = client.post("/api/v1/medicines", json=payload, headers=admin_headers)
    assert res.status_code == 201
    med_data = res.json()
    assert med_data["medicine_id"] == "MED_AMOX_500"

    # Verify inventory was automatically initialized for this medicine
    inv = db_session.query(InventoryCurrent).filter(InventoryCurrent.medicine_id == "MED_AMOX_500").first()
    assert inv is not None
    assert inv.closing_stock == 0
    assert inv.stock_status == "OUT_OF_STOCK"

    # Test list medicines
    res = client.get("/api/v1/medicines?search=amoxicillin")
    assert res.status_code == 200
    paginated = res.json()
    assert paginated["total"] >= 1
    assert any(m["medicine_id"] == "MED_AMOX_500" for m in paginated["data"])

    # Test get single medicine
    res = client.get("/api/v1/medicines/MED_AMOX_500")
    assert res.status_code == 200
    assert res.json()["display_name"] == "Amoxicillin 500mg Capsule"
    assert res.json()["category"]["category_name"] == "Test Antibiotics"
    assert res.json()["primary_supplier"]["supplier_name"] == "Apex Pharma Dist"


def test_transaction_receipt_and_open_order_reduction(client, staff_headers, db_session):
    # Set on_order_units in inventory to test Sec 9.2: purchase receipt reduces open orders
    inv = db_session.query(InventoryCurrent).filter(InventoryCurrent.medicine_id == "MED_AMOX_500").first()
    inv.on_order_units = 150
    db_session.commit()

    # Staff records a purchase receipt of 100 units
    res = client.post(
        "/api/v1/transactions",
        json={
            "medicine_id": "MED_AMOX_500",
            "transaction_type": "RECEIPT",
            "quantity": 100,
            "reference_number": "PO-1001",
            "notes": "Incoming batch received",
        },
        headers=staff_headers,
    )
    assert res.status_code == 201
    tx = res.json()
    assert tx["stock_before"] == 0
    assert tx["stock_after"] == 100
    assert tx["quantity"] == 100

    # Verify inventory table is updated and on_order_units reduced
    db_session.refresh(inv)
    assert inv.closing_stock == 100
    assert inv.on_order_units == 50  # 150 - 100 = 50
    assert inv.stock_status in ["LOW_STOCK", "IN_STOCK"]


def test_negative_stock_prevention(client, staff_headers, db_session):
    # Current stock is 100 units. Attempt to sell 150 units.
    res = client.post(
        "/api/v1/transactions",
        json={
            "medicine_id": "MED_AMOX_500",
            "transaction_type": "SALE",
            "quantity": 150,
            "reference_number": "BILL-999",
            "notes": "Overselling attempt",
        },
        headers=staff_headers,
    )
    # Must fail with 400 Bad Request
    assert res.status_code == 400
    err = res.json()
    assert "detail" in err or "error" in err

    # Verify inventory is NOT deducted
    inv = db_session.query(InventoryCurrent).filter(InventoryCurrent.medicine_id == "MED_AMOX_500").first()
    db_session.refresh(inv)
    assert inv.closing_stock == 100


def test_valid_sale_and_inventory_kpis(client, staff_headers, admin_headers, db_session):
    # Valid sale of 40 units
    res = client.post(
        "/api/v1/transactions",
        json={
            "medicine_id": "MED_AMOX_500",
            "transaction_type": "SALE",
            "quantity": 40,
            "reference_number": "BILL-1002",
        },
        headers=staff_headers,
    )
    assert res.status_code == 201
    tx = res.json()
    assert tx["stock_before"] == 100
    assert tx["stock_after"] == 60

    # Verify inventory summary endpoint
    res = client.get("/api/v1/inventory/summary")
    assert res.status_code == 200
    summary = res.json()
    assert summary["total_skus"] >= 1
    assert summary["total_units_in_stock"] >= 60

    # Update replenishment parameters (manager/admin)
    res = client.patch(
        "/api/v1/inventory/MED_AMOX_500/parameters",
        json={"reorder_point": 80, "safety_stock": 40, "moq": 60},
        headers=admin_headers,
    )
    assert res.status_code == 200
    inv_data = res.json()
    assert inv_data["reorder_point"] == 80
    assert inv_data["safety_stock"] == 40


def test_settings_crud(client, admin_headers, staff_headers):
    # Admin can list settings
    res = client.get("/api/v1/settings")
    assert res.status_code == 200

    # Staff forbidden to update setting
    res = client.patch(
        "/api/v1/settings/pharmacy_name",
        json={"value": "PharmaStock SuperStore"},
        headers=staff_headers,
    )
    assert res.status_code == 403

    # Admin can update setting
    res = client.patch(
        "/api/v1/settings/pharmacy_name",
        json={"value": "PharmaStock SuperStore"},
        headers=admin_headers,
    )
    assert res.status_code == 200
    assert res.json()["value"] == "PharmaStock SuperStore"


def test_void_transaction_and_export(client, staff_headers, admin_headers, db_session):
    # Staff performs a sale of 10 units
    res = client.post(
        "/api/v1/transactions",
        json={
            "medicine_id": "MED_AMOX_500",
            "transaction_type": "SALE",
            "quantity": 10,
            "reference_number": "BILL-TO-VOID",
        },
        headers=staff_headers,
    )
    assert res.status_code == 201
    sale_tx = res.json()
    orig_tx_id = sale_tx["id"]
    stock_after_sale = sale_tx["stock_after"]

    # Staff cannot void (requires manager/admin)
    res = client.post(
        f"/api/v1/transactions/{orig_tx_id}/void",
        json={"reason": "Customer returned wrong item immediately"},
        headers=staff_headers,
    )
    assert res.status_code == 403

    # Admin voids the sale
    res = client.post(
        f"/api/v1/transactions/{orig_tx_id}/void",
        json={"reason": "Customer returned wrong item immediately"},
        headers=admin_headers,
    )
    assert res.status_code == 200
    void_tx = res.json()
    assert void_tx["stock_after"] == stock_after_sale + 10

    # Attempting to void again must fail
    res = client.post(
        f"/api/v1/transactions/{orig_tx_id}/void",
        json={"reason": "Duplicate void attempt"},
        headers=admin_headers,
    )
    assert res.status_code in [400, 422]

    # Test CSV export
    res = client.get("/api/v1/transactions/export")
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    assert "Transaction ID" in res.text
    assert "Amoxicillin 500mg Capsule" in res.text

