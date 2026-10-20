# PharmaStock IQ — REST API Contract

> **Version:** 1.0.0  
> **Base URL:** `/api/v1`  
> **Specification Reference:** Derived from `req.md` Sections 8, 9, 10, 11, 12, 13, 14, 15, 16, 22.

---

## Standard Response Envelopes & Conventions

### Successful Paginated Response
```json
{
  "data": [ ... ],
  "total": 85,
  "page": 1,
  "page_size": 20,
  "total_pages": 5
}
```

### Error Response Format (RFC 7807 Compliant)
```json
{
  "error": {
    "code": "INSUFFICIENT_STOCK",
    "message": "Transaction would result in negative inventory (closing stock: 12, attempted reduction: 20).",
    "details": {
      "medicine_id": "MED002",
      "current_stock": 12,
      "requested_quantity": 20
    }
  }
}
```

---

## 1. Authentication & RBAC

### `POST /auth/login`
- **Request:**
  ```json
  {
    "email": "admin@pharmastock.local",
    "password": "SecurePassword123!"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "refresh_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "id": 1,
      "email": "admin@pharmastock.local",
      "name": "Dr. Sarah Mitchell",
      "role": "ADMIN",
      "is_active": true
    }
  }
  ```

### `POST /auth/refresh`
- **Request:** `{ "refresh_token": "eyJhbGci..." }`
- **Response (200 OK):** `{ "access_token": "...", "expires_in": 3600 }`

### `GET /auth/me`
- **Headers:** `Authorization: Bearer <token>`
- **Response (200 OK):** Current User object

---

## 2. Medicines & Master Catalog

### `GET /medicines`
- **Query Parameters:**
  - `search` (string, optional)
  - `category_id` (string, optional)
  - `supplier_id` (string, optional)
  - `is_active` (boolean, optional)
  - `page` (int, default 1)
  - `page_size` (int, default 20)
  - `sort_by` (string, default "medicine_id")
  - `sort_dir` ("asc" | "desc", default "asc")
- **Response (200 OK):** `PaginatedResponse<Medicine>`

### `GET /medicines/{medicine_id}`
- **Response (200 OK):** `Medicine` object with embedded `category` and `primary_supplier`.

### `POST /medicines` (Admin/Manager)
- **Request:**
  ```json
  {
    "medicine_id": "MED086",
    "display_name": "Pantoprazole 40mg",
    "generic_name": "Pantoprazole Sodium",
    "category_id": "CAT04",
    "primary_supplier_id": "SUP01",
    "dosage_form": "Tablet",
    "strength": "40mg",
    "pack_size": 10,
    "unit_of_measure": "strip",
    "unit_cost_inr": 45.0,
    "unit_price_inr": 68.0,
    "storage_condition": "Room Temperature"
  }
  ```
- **Response (201 Created):** Created `Medicine`

### `PATCH /medicines/{medicine_id}` (Admin/Manager)
- **Request:** Partial fields to update
- **Response (200 OK):** Updated `Medicine`

### `POST /medicines/{medicine_id}/deactivate` (Admin)
- **Response (200 OK):** `{ "status": "deactivated" }`

---

## 3. Categories & Suppliers

### `GET /categories`
- **Response (200 OK):** `Category[]`

### `GET /suppliers`
- **Response (200 OK):** `Supplier[]`

### `POST /suppliers` (Admin/Manager)
- **Request:** `SupplierCreate`
- **Response (201 Created):** `Supplier`

---

## 4. Current Inventory Positions

### `GET /inventory`
- **Query Parameters:** `search`, `category_id`, `risk_level`, `stock_status`, `page`, `page_size`
- **Response (200 OK):** `PaginatedResponse<InventoryItem>`

### `GET /inventory/{medicine_id}`
- **Response (200 OK):** `InventoryItem`

### `PATCH /inventory/{medicine_id}/parameters` (Admin/Manager)
- **Request:**
  ```json
  {
    "safety_stock": 250,
    "reorder_point": 650,
    "moq": 100
  }
  ```
- **Response (200 OK):** Updated `InventoryItem`

---

## 5. Transactions & Stock Movements

### `GET /transactions`
- **Query Parameters:** `medicine_id`, `transaction_type`, `date_from`, `date_to`, `page`, `page_size`
- **Response (200 OK):** `PaginatedResponse<Transaction>`

### `POST /transactions`
- **Request:**
  ```json
  {
    "medicine_id": "MED001",
    "transaction_type": "SALE",
    "quantity": 10,
    "reference_number": "INV-2025-00192",
    "notes": "Prescription dispensing"
  }
  ```
- **Response (201 Created):** `Transaction`
- **Error (400 Bad Request):** If stock would drop below 0 (`INSUFFICIENT_STOCK`).

---

## 6. Demand Forecasting & ML Pipeline

### `GET /forecasts/{medicine_id}`
- **Query Parameters:**
  - `horizon` (7 | 14 | 30, default 30)
  - `model` ("XGBoost" | "GradientBoosting", optional)
- **Response (200 OK):**
  ```json
  {
    "medicine_id": "MED002",
    "model": "Gradient Boosting Regressor",
    "horizon_days": 30,
    "run_date": "2025-12-31T23:00:00Z",
    "points": [
      {
        "date": "2026-01-01",
        "predicted_demand": 56.4,
        "lower_bound": 47.8,
        "upper_bound": 65.0,
        "is_forecast": true
      }
    ]
  }
  ```

### `POST /ml/train` (Admin Only)
- **Trigger async model retrain.** Returns `202 Accepted` with task ID.

---

## 7. Stock-Out Risk & Decision Engine

### `GET /risk`
- **Query Parameters:** `risk_level`, `category_id`, `search`, `page`, `page_size`, `sort_by`, `sort_dir`
- **Response (200 OK):** `PaginatedResponse<RiskResult>`

### `GET /medicines/{medicine_id}/calculation`
- **Response (200 OK):**
  ```json
  {
    "medicine_id": "MED002",
    "expected_daily_demand": 56.4,
    "closing_stock": 120,
    "coverage_days": 2.1,
    "lead_time_days": 7.0,
    "safety_stock": 300,
    "required_stock": 695,
    "risk_score": 88,
    "risk_level": "HIGH",
    "explanation": "Coverage (2.1 days) is strictly shorter than supplier lead time (7 days). Remaining stock is 120 units."
  }
  ```

### `POST /risk/run` (Manager/Admin)
- **Recomputes risk classifications across all 85 medicines.**

---

## 8. Replenishment Recommendations

### `GET /replenishment`
- **Query Parameters:** `status` ("PENDING" | "ACCEPTED" | "ORDERED" | "DISMISSED")
- **Response (200 OK):** `Recommendation[]`

### `POST /replenishment/{id}/accept` (Manager/Admin)
- **Response (200 OK):** Updated `Recommendation` with `status: "ACCEPTED"`.

### `POST /replenishment/{id}/order-placed` (Manager/Admin)
- **Response (200 OK):** Updated `Recommendation` with `status: "ORDERED"`. Increases `open_order_qty`.

### `POST /replenishment/{id}/dismiss` (Manager/Admin)
- **Request:** `{ "reason": "Alternative brand stock available" }`
- **Response (200 OK):** Updated `Recommendation` with `status: "DISMISSED"`.

---

## 9. Alerts & Notifications

### `GET /alerts`
- **Query Parameters:** `severity`, `alert_type`, `status`, `medicine_id`
- **Response (200 OK):** `Alert[]`

### `POST /alerts/{id}/acknowledge`
- **Response (200 OK):** Updated `Alert` (`status: "ACKNOWLEDGED"`).

### `POST /alerts/{id}/resolve`
- **Response (200 OK):** Updated `Alert` (`status: "RESOLVED"`).

### `POST /alerts/{id}/dismiss`
- **Response (200 OK):** Updated `Alert` (`status: "DISMISSED"`).

### `POST /alerts/bulk-acknowledge`
- **Request:** `{ "ids": ["ALT001", "ALT002"] }`
- **Response (200 OK):** `{ "acknowledged_count": 2 }`

---

## 10. Dashboard & System Status

### `GET /dashboard/summary`
- **Response (200 OK):** Aggregated metrics:
  - `total_skus`: 85
  - `total_stock_value`: INR sum
  - `stockout_items_count`: integer
  - `critical_risk_count`: integer
  - `pending_orders_count`: integer
  - `active_alerts_count`: integer
  - `risk_distribution`: counts by LOW, MEDIUM, HIGH, CRITICAL
  - `category_stock`: inventory value per category
  - `top_risk_medicines`: top 10 highest risk score items

### `GET /health`
- **Response (200 OK):** `{ "status": "ok", "timestamp": "...", "database": "connected" }`
