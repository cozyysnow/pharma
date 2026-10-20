import pytest
from backend.app.core.security import create_access_token


@pytest.fixture
def admin_headers(admin_user):
    token = create_access_token(subject=admin_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def staff_headers(staff_user):
    token = create_access_token(subject=staff_user.id)
    return {"Authorization": f"Bearer {token}"}


def test_dataset_status_and_preview(client):
    # Status endpoint
    res = client.get("/api/v1/datasets/status")
    assert res.status_code == 200
    status_data = res.json()
    assert "raw_files_count" in status_data
    assert status_data["raw_files_count"] >= 10

    # Preview endpoint
    res = client.get("/api/v1/datasets/preview?filename=stockout_prediction_dataset.csv&limit=5")
    assert res.status_code == 200
    preview = res.json()
    assert preview["filename"] == "stockout_prediction_dataset.csv"
    assert len(preview["rows"]) == 5
    assert len(preview["columns"]) >= 25


def test_dataset_validation(client):
    res = client.post("/api/v1/datasets/validate")
    assert res.status_code == 200
    report = res.json()
    assert report["overall_passed"] is True
    assert report["failed_checks"] == 0
    assert report["passed_checks"] >= 8


def test_dataset_import_flow(client, admin_headers, staff_headers):
    # Staff cannot trigger import
    res = client.post("/api/v1/datasets/import", headers=staff_headers)
    assert res.status_code == 403

    # Admin triggers import
    res = client.post("/api/v1/datasets/import", headers=admin_headers)
    assert res.status_code == 200
    result = res.json()
    assert result["daily_records_count"] == 155210
    assert result["medicines_count"] == 85
    assert result["suppliers_count"] == 15
    assert result["categories_count"] == 11
    assert result["inventory_synced_count"] == 85

    # Re-running import is an idempotent no-op
    res2 = client.post("/api/v1/datasets/import", headers=admin_headers)
    assert res2.status_code == 200
    result2 = res2.json()
    assert result2["was_already_imported"] is True

    # Check statistics endpoint
    res_stats = client.get("/api/v1/datasets/statistics")
    assert res_stats.status_code == 200
    stats = res_stats.json()
    assert stats["total_daily_records"] == 155210
    assert stats["total_medicines"] >= 85
    assert stats["total_suppliers"] >= 15
    assert stats["total_categories"] >= 11
    assert stats["is_complete"] is True
    assert stats["date_range"]["start_date"] == "2021-01-01"
    assert stats["date_range"]["end_date"] == "2025-12-31"
