# PRD — Pharmacy Stock-Out Prediction & Inventory Decision Support System

| | |
|---|---|
| **Document type** | Product Requirements Document / primary implementation specification |
| **Intended builder** | Antigravity (AI coding agent), supervised by a human developer |
| **Project level** | B.Tech live project — must be demonstrable, explainable, and runnable locally |
| **Hard constraints** | No Docker. UI-first. Module-by-module. Human-in-the-loop decisions only. |
| **Status** | Project idea finalized (fixed). Dataset already inspected and validated (fixed). |

---

## 0. READ THIS FIRST (Instructions to Antigravity)

1. **The project idea in Section 1 is fixed.** Do not rewrite, shorten, or change its scope.
2. **Do not build the whole application in one generation.** Build **one phase at a time** (Section 24). Begin with **Phase 1: UI Foundation**. Complete it, verify it against its exit criteria, report, and only then continue.
3. **Before each major module**, post a short plan: what will be built, which files/components will be created or modified, and how it will be verified.
4. **Never fabricate** dataset values, ML metrics, or dashboard numbers. Mock data is allowed **only** in Phases 1–2 and only inside `frontend/src/mocks/`. Final numbers must come from the real database/ML pipeline.
5. **Never use Docker**, Docker Compose, Kubernetes, or containerized development anywhere.
6. **Do not add technologies** that are not listed in Section 19.
7. **Do not rewrite working code** unnecessarily. Prefer small, verified increments.
8. **The data dictionary and validation report are the source of truth for column names.** They are expected at `docs/dataset/DATA_DICTIONARY.md` and `docs/dataset/VALIDATION_REPORT.md`. **Read them before Phase 4/5. Never guess column names.** If they are missing, stop and ask the human developer to add them. (Section 9.3 lists the *logical* fields the system needs; the physical column names come from the dictionary.)
9. Keep the system appropriate for a B.Tech project: simple, modular, explainable. No enterprise over-engineering (no microservices, message queues, Kubernetes, multi-tenant logic, etc.).

---

## 1. Project Idea (FIXED — verbatim source of truth)

> The proposed Pharmacy Stock-Out Prediction & Inventory Decision Support System is a web-based, intelligent pharmacy inventory management and decision-support application designed to move medicine inventory management from a reactive approach based only on current stock levels toward a predictive and data-driven approach. The system will analyze historical medicine demand, sales transactions, inventory levels, supplier information, supplier lead times, safety stock, replenishment information, and other relevant inventory factors to predict future medicine demand and identify medicines that may face stock-outs before they occur. The project uses a structured pharmacy dataset containing approximately 155,210 daily records across 85 medicines, 11 medicine categories, and 15 suppliers, covering the period from 2021 to 2025, with information related to medicine demand, sales, inventory, suppliers, stock availability, replenishment, and stock-out conditions. The system will first provide a dataset management and validation module through which the available dataset can be uploaded, inspected, validated, cleaned, processed, and mapped to the required system fields before being used by the machine-learning pipeline. The data-processing component will handle missing-value checks, duplicate detection, data-type validation, date processing, feature preparation, and other preprocessing requirements. Historical demand will then be analyzed using features such as previous demand values, lag features, rolling averages, day-of-week patterns, seasonal patterns, trends, and other relevant variables available in the dataset. The machine-learning component will evaluate suitable forecasting approaches, beginning with simple baseline methods such as historical or rolling averages and comparing them with appropriate machine-learning or statistical models such as Gradient Boosting, Random Forest, Linear Regression, ARIMA, or Exponential Smoothing depending on the characteristics of the available data. Chronological training, validation, and testing will be used so that future information is not incorrectly used to predict the past, and model performance will be evaluated using appropriate metrics such as MAE, RMSE, and MAPE. After forecasting expected medicine demand, the system will calculate expected daily demand and stock coverage using current available stock and predicted demand, estimate expected demand during the supplier lead-time period, consider safety stock and replenishment information, calculate required stock, and determine whether the available inventory is sufficient to meet expected demand until replenishment. Based on these calculations, each medicine can be assigned a stock-out risk level such as LOW, MEDIUM, or HIGH, allowing the system to identify medicines that require attention before an actual stock-out occurs. The system will then generate understandable risk alerts and replenishment recommendations, including information such as current stock, predicted demand, stock coverage, supplier lead time, required stock, risk level, and recommended replenishment quantity where the available data supports such calculations. The application will provide a centralized interactive dashboard where authorized users can monitor total medicines, current inventory, stock levels, stock-out risks, demand forecasts, recent transactions, replenishment requirements, alerts, trends, and reports through tables, charts, cards, and visual indicators. The system will also contain inventory management functionality for maintaining medicine information and stock status, transaction management for recording sales, purchases, returns, adjustments, damaged or expired stock where applicable, and inventory updates based on transactions. The backend will be developed using Python and FastAPI, providing REST APIs, business logic, authentication, data processing, inventory calculations, forecasting services, risk analysis, and communication with the database and machine-learning components, while the frontend will be developed using React with TypeScript to provide a responsive and user-friendly interface. PostgreSQL will be used for structured storage of medicines, suppliers, inventory records, transactions, forecasts, risk results, alerts, users, and related system information, while Python libraries such as Pandas, NumPy, Scikit-learn, and suitable statistical/time-series libraries will be used for data processing, feature engineering, model training, forecasting, and evaluation. Development and API testing can be performed using tools such as VS Code, Git/GitHub, Postman or Insomnia, PostgreSQL, and pgAdmin, and the project will be developed without Docker, using a direct local development setup. The application will be designed modularly so that the dataset management, database, authentication, medicine management, inventory, transactions, preprocessing, forecasting, stock-out risk analysis, alerts, dashboard, reporting, and testing components can be developed and verified individually before final integration. The system will follow a human-in-the-loop decision-support approach, meaning that predictions and recommendations will assist authorized pharmacy staff but the final decision regarding replenishment or purchasing will remain under human control. The project will not perform autonomous purchasing and will not provide medical diagnosis, treatment, dosage, prescription, or other clinical recommendations. The available dataset has been validated for this project with no missing values or duplicate medicine-date records, consistent inventory calculations, valid stock-coverage and replenishment calculations, and checks indicating no identified future-data leakage; it contains historical demand information including quantity sold and unmet demand, making it suitable for the proposed forecasting task. The system is therefore intended to provide an integrated solution that combines inventory management, historical demand analysis, machine-learning-based demand forecasting, stock coverage calculation, stock-out risk detection, replenishment recommendations, alerts, visualization, and reporting into one platform, helping pharmacy staff identify potential shortages earlier, understand future inventory requirements, and make faster and more informed inventory decisions while keeping the final operational decisions with authorized users.

---

## 2. Consistency & Technical-Alignment Review

The idea is **internally consistent and technically feasible** with the chosen stack. The review below identifies points where the idea is silent or where a naive implementation would go wrong. None of them change the project scope; each has a **resolution that this PRD adopts**.

| # | Finding | Why it matters | Resolution adopted in this PRD |
|---|---|---|---|
| R1 | **Dataset ends 2025-12-31, but the system is used "live".** | "Current stock" and "next N days" need a reference date. | Introduce a configurable **`as_of_date`**. After import, `as_of_date = last dataset date` and the *current inventory snapshot* is initialized from each medicine's final record. New transactions advance the live state. Forecasts start from the day after `as_of_date`/latest data date (Sec. 9.5). |
| R2 | **Dataset = daily aggregates; app also has a Transactions module.** | Two different representations of "sales". | Dataset rows are stored as **historical daily records** (read-only history, used for ML/analytics). Transactions module records **new operational events** going forward and updates current stock. Transactions after the dataset end can be aggregated to daily demand for future retraining (Sec. 9.5, 13). |
| R3 | **Dataset already contains pre-computed stock coverage, required stock, replenishment flags, and risk label/score.** | Using them as ML features = **target leakage**. Re-deriving them differently = inconsistent numbers. | These columns are **forbidden as ML features** (Sec. 12.4). The app **recomputes** them from forecasts using the *same definitions as the data dictionary*, and uses the dataset's versions only to **cross-check** the formulas (Sec. 14). |
| R4 | **Forecast target must be `demand_quantity = quantity_sold + unmet_demand`**, not sales. | Sales are censored by stock-outs; forecasting sales would under-predict demand exactly when stock-outs occur. | Target is `demand_quantity` everywhere. |
| R5 | **Documented ML-readiness result (GB test MAE 8.072 vs naïve lag-1 10.984) is probably a one-step-ahead result.** | Lead-time demand needs **multi-day** forecasts (7–30+ days). One-step MAE overstates real usefulness. | The pipeline must (a) **reproduce** the documented result as a sanity check (never hard-code it), and (b) also report **multi-step (horizon-aware) backtest metrics** (h = 1, 7, 14, 30 days). Model selection considers both. |
| R6 | **MAPE is undefined/unstable when actual demand = 0 or is small.** | Daily pharmacy demand has small values. | Report MAE and RMSE as primary; MAPE **only on non-zero actuals**; add **WAPE** (sum abs error / sum actual) as the robust percentage metric. |
| R7 | **ARIMA/Exponential Smoothing are per-series models; there are 85 series.** | Fitting 85 × many models is slow and rarely beats global ML. | Use ARIMA/ETS as **candidates on a fixed per-medicine basis with limited order search** (or on a representative subset if runtime is excessive). Do not spend effort beyond what's needed; select models by measured results. |
| R8 | **Risk rule must match the dataset's own risk definition** (validation says "no risk-label/score mismatches"). | Otherwise the app contradicts the dataset. | Default rule in Sec. 15 is used **only if** the data dictionary defines no rule; otherwise implement the dictionary's definition and make thresholds configurable. |
| R9 | **"Damaged/expired stock" implies batch tracking, but the dataset has no batch/expiry detail (assumed — verify).** | Batch tracking is a large scope increase. | Support **DAMAGED** and **EXPIRED** as transaction types that reduce stock. **No batch-level or expiry-date tracking.** |
| R10 | **Training takes time; HTTP requests must not block.** | UX and timeouts. | Training runs as a **FastAPI background task + `ml_runs` status table** (and is also runnable via CLI). No Celery/Redis. |
| R11 | **UI-first with mock data can cause rework** if mock shapes differ from API shapes. | Phase 9 integration risk. | Define TypeScript types and an `api/` service layer **now** (Sec. 7.4) that mirror the planned Pydantic schemas. Mocks are served by the same service functions behind a flag. |
| R12 | **Open orders / MOQ / lead time exist in data but "human ordering" is out of band.** | System must not place orders. | Recommendations have a **human workflow** (Pending → Accepted/Dismissed → "Order Placed (manual)"). Marking "Order Placed" only records an *open order quantity*; it never contacts a supplier. |

---

## 3. Project Overview

**Product name:** Pharmacy Stock-Out Prediction & Inventory Decision Support System (working short name: **PharmaStock IQ**).

**One-line summary:** A web app that forecasts medicine demand, converts forecasts into stock coverage / lead-time demand / required stock, classifies stock-out risk (LOW/MEDIUM/HIGH), and recommends — but never executes — replenishment.

**Core value:** Move from *reactive* ("we ran out") to *predictive* ("we will run out in 6 days; supplier lead time is 9 days; consider ordering N units").

## 4. Problem Statement

Pharmacy inventory is typically managed by looking at current stock only. This ignores demand trends, weekday/seasonal patterns, supplier lead times, and safety stock, so staff discover shortages after they happen, or over-stock slow movers. Unmet demand (customers who could not be served) is rarely measured. Staff need an early-warning and decision-support tool that is understandable, not a black box.

## 5. Objectives

1. Provide a professional dashboard showing inventory, risks, forecasts, alerts, and replenishment needs.
2. Forecast daily medicine demand using chronologically-validated models that are compared against baselines.
3. Compute stock coverage, lead-time demand, required stock, replenishment need, and risk level with transparent formulas.
4. Generate understandable alerts and replenishment **recommendations** with explanations.
5. Support medicine, supplier, inventory, and transaction management with correct stock updates.
6. Provide dataset import/validation/preprocessing tooling around the already-validated dataset.
7. Keep a human in control of every purchasing decision.
8. Run entirely locally without Docker; be easy to demo and explain.

## 6. Scope

### 6.1 In scope
Authentication & role-based authorization; dataset management; medicines, suppliers, inventory, transactions; preprocessing & feature engineering; demand forecasting (baselines + candidate models + evaluation + selection); stock coverage, lead-time demand, required stock, risk classification, explanations; alerts; replenishment recommendations (with human workflow); dashboard; reports/exports (CSV, and PDF optional-stretch); settings; testing.

### 6.2 Out of scope (explicit)
Automatic purchasing or supplier ordering; email/SMS/WhatsApp delivery (in-app alerts only); medical diagnosis, treatment, dosage, prescriptions, or medicine recommendations for patients; patient or prescription data; batch/expiry tracking; multi-pharmacy / multi-branch; billing/POS/invoicing/payments; supplier portals; Docker or any container tooling; real-time streaming; deep-learning models.

### 6.3 Limitations to display in UI
A persistent but unobtrusive notice (footer of Risk/Replenishment/Forecast pages and Settings → About): *"Decision support only. Recommendations require review and approval by authorized pharmacy staff. This system provides no medical advice."*

## 7. Target Users & Roles

| Role | Description | Key permissions |
|---|---|---|
| **Admin** | System owner / project administrator | Everything: users, settings, dataset import, ML training, thresholds |
| **Inventory Manager** | Pharmacy manager / purchasing decision-maker | Medicines, suppliers, all transaction types, run risk analysis, accept/dismiss recommendations, manage alerts, reports |
| **Pharmacy Staff** | Counter / stock staff | View dashboards/inventory/forecasts/risk; record sales & customer returns; acknowledge alerts |

Permission matrix is in Sec. 21.

---

## 8. Functional Requirements

Priority: **M** = must, **S** = should, **C** = could (stretch).

### 8.1 Authentication & Authorization
- FR-AUTH-1 (M) Login with email + password; JWT access token (short-lived) + refresh token or silent re-login.
- FR-AUTH-2 (M) Passwords hashed (bcrypt or argon2). Never stored or logged in plain text.
- FR-AUTH-3 (M) Role-based access control enforced **on the backend**; UI hides unauthorized actions but is not the security boundary.
- FR-AUTH-4 (M) Logout; expired-token handling redirects to login with a toast.
- FR-AUTH-5 (S) Admin can create/deactivate users and change roles. (C) change own password.

### 8.2 Dataset Management
- FR-DS-1 (M) Upload CSV (≤ configurable size, default 100 MB) or "Use bundled dataset" from `data/raw/`.
- FR-DS-2 (M) Preview first N rows, column list, dtypes, row/column counts.
- FR-DS-3 (M) **Schema verification** against the documented schema (72 columns, expected dtypes); report missing/extra/renamed columns.
- FR-DS-4 (M) **Runtime validation** summary: missing values, duplicate record IDs, duplicate (medicine, date), date range & continuity (expected 1,826 days/medicine), valid medicine/supplier IDs, negative values. Expected result for the provided dataset is *all pass*; compare with documented baseline counts (155,210 rows, 85 medicines, 15 suppliers, 11 categories) and show match/mismatch.
- FR-DS-5 (M) **Column mapping**: map dataset columns to required logical fields (Sec. 9.3). For the provided dataset the mapping is pre-filled from the data dictionary and editable.
- FR-DS-6 (M) Import into PostgreSQL (medicines, suppliers, categories, daily history, initial inventory snapshot). Import is **idempotent** (re-import does not duplicate) and logged in `dataset_imports`.
- FR-DS-7 (M) Dataset statistics: row counts, date range, per-category/medicine summaries, demand distribution, stock-out event count, replenishment-required count, unmet-demand total.
- FR-DS-8 (S) Preprocessing run with status + report (what was checked/changed). Do **not** silently alter data; log every change.
- FR-DS-9 (S) Download validation report (JSON/CSV).

### 8.3 Medicine Management
- FR-MED-1 (M) List with search, filter (category, supplier, risk, stock status), sort, pagination.
- FR-MED-2 (M) Create / edit / deactivate (soft delete) medicines. No hard delete if history exists.
- FR-MED-3 (M) Medicine Details page: attributes, current stock, supplier & lead time, demand history chart, forecast chart, risk, recommendation, recent transactions.
- FR-MED-4 (M) Fields are inventory-oriented only (name, category, supplier, unit, reorder parameters). **No dosage, indications, or clinical guidance fields.**

### 8.4 Supplier Management
- FR-SUP-1 (M) List/create/edit/deactivate suppliers (name, contact info, default lead time, notes).
- FR-SUP-2 (M) View medicines supplied by a supplier and lead-time summary.
- FR-SUP-3 (S) Supplier summary cards (number of medicines, avg lead time, medicines currently at HIGH risk).

### 8.5 Inventory Management
- FR-INV-1 (M) Inventory table: current stock, safety stock, reorder level (if in data), open order qty, MOQ, stock status (In stock / Low / Out), risk level, coverage days.
- FR-INV-2 (M) Stock changes **only** through transactions (ledger principle), never by direct edit, except via an Adjustment transaction with reason.
- FR-INV-3 (M) Stock status derived rules documented (Sec. 15.6).
- FR-INV-4 (S) Inventory summary cards (total SKUs, total units, # low, # out, # at risk).

### 8.6 Transaction Management
- FR-TXN-1 (M) Record: **SALE, PURCHASE (stock received), CUSTOMER_RETURN, SUPPLIER_RETURN, ADJUSTMENT (±, reason required), DAMAGED, EXPIRED**.
- FR-TXN-2 (M) Each transaction atomically updates current stock inside a DB transaction with row locking; negative stock is **rejected** with a clear error.
- FR-TXN-3 (M) PURCHASE reduces the medicine's open order quantity (not below 0).
- FR-TXN-4 (M) Transactions are **immutable**; corrections are done with a reversing adjustment (optionally a "void" entry that creates an offsetting transaction).
- FR-TXN-5 (M) List with filter (date range, type, medicine, user), search, sort, pagination, CSV export.
- FR-TXN-6 (S) Optional: when a SALE is rejected for insufficient stock, offer "Record unmet demand" which stores an `unmet_demand_events` count for that day (feeds future retraining). Mark as stretch; do not block core flow.

### 8.7 Demand Forecasting
- FR-FC-1 (M) Train/evaluate pipeline (Sec. 12) triggered by Admin; shows run status and results.
- FR-FC-2 (M) Forecast page: pick a medicine → history + forecast chart with horizon selector (7/14/30 days, bounded by max supported horizon), model name, and error band (if available).
- FR-FC-3 (M) Model comparison table (baselines vs candidates) with MAE, RMSE, MAPE (non-zero), WAPE, per horizon; selected model highlighted with the reason.
- FR-FC-4 (M) Forecasts persisted in `forecasts` tied to `model_run_id` and `generated_at`.
- FR-FC-5 (S) Category-level aggregate forecast view.

### 8.8 Stock-Out Risk & Decision Support
- FR-RISK-1 (M) For each active medicine compute: predicted daily demand, stock coverage days, lead-time demand, safety stock, required stock, inventory position, shortfall, risk level (LOW/MEDIUM/HIGH), risk score, and a human-readable explanation.
- FR-RISK-2 (M) Risk page: sortable/filterable table, risk distribution chart, drill-down side panel showing the calculation chain.
- FR-RISK-3 (M) "Run risk analysis" action (Admin/Manager) that recomputes using the latest forecasts and current stock; results stored in `risk_results` with timestamp.
- FR-RISK-4 (S) Risk-level cross-check against the dataset's risk labels on historical dates (validation tool, Admin only).

### 8.9 Alerts
- FR-AL-1 (M) Alert types: **HIGH_RISK, LOW_STOCK, REPLENISHMENT_REQUIRED, DEMAND_SPIKE, FORECAST_DEVIATION**.
- FR-AL-2 (M) Severity (CRITICAL/WARNING/INFO), status (OPEN/ACKNOWLEDGED/RESOLVED/DISMISSED), message with the numbers behind it.
- FR-AL-3 (M) De-duplication: one open alert per (medicine, type); re-evaluation updates rather than duplicates; auto-resolve when the condition clears.
- FR-AL-4 (M) Alerts page with filters (type, severity, status, medicine), bulk acknowledge, header bell with unread count.
- FR-AL-5 (M) In-app only (no email/SMS).

### 8.10 Replenishment Recommendations
- FR-REP-1 (M) Generate a recommendation when inventory position < required stock (Sec. 16), including current stock, open orders, predicted demand, coverage, lead time, safety stock, required stock, MOQ, recommended quantity, supplier, risk level, and an explanation.
- FR-REP-2 (M) Human workflow: **PENDING → ACCEPTED / DISMISSED → ORDER_PLACED (manual)**. Dismiss requires an optional reason. Accept/Order Placed records user + timestamp.
- FR-REP-3 (M) "Order Placed (manual)" increases the medicine's `open_order_qty` by the entered quantity (editable, default = recommended qty). **No external call, no supplier communication.**
- FR-REP-4 (M) Recommendations carry the banner "Recommendation only — requires staff approval."
- FR-REP-5 (S) Export recommendations as CSV for the staff to use in their own purchasing process.

### 8.11 Dashboard
See Sec. 18.2.

### 8.12 Reports
- FR-RPT-1 (M) Reports: Inventory Status, Stock-Out Risk, Replenishment Recommendations, Transactions (date range), Forecast Summary, Model Performance, Alerts Summary.
- FR-RPT-2 (M) Filters (date range, category, supplier, risk) and **CSV export**.
- FR-RPT-3 (C) PDF export.

### 8.13 Settings
- FR-SET-1 (M) Profile; theme preference (light/dark optional); about page with limitations notice.
- FR-SET-2 (M, Admin) Risk thresholds, alert thresholds (e.g., demand-spike %), default forecast horizon, `as_of_date` info, service level / z-value for safety-stock fallback.
- FR-SET-3 (M, Admin) User management.
- FR-SET-4 (S, Admin) Model management (active model, retrain button).

---

## 9. Dataset Structure & Usage

### 9.1 Validated dataset facts (fixed — do not re-derive or contradict)

| Property | Value |
|---|---|
| Records | ~155,210 (85 medicines × 1,826 days) |
| Columns | 72 |
| Medicines / categories / suppliers | 85 / 11 / 15 |
| Period | 2021-01-01 → 2025-12-31 (daily) |
| Units sold (total) | 5,067,888 |
| Unmet demand (total units) | 100,883 |
| Stock-out events | 2,590 |
| Replenishment-required records | 5,423 |
| Nature | **Synthetic**; no patient or prescription information |
| Validation | 17/17 checks passed: 0 missing values; 0 duplicate record IDs; 0 duplicate medicine/date combinations; 0 fully duplicated rows; valid medicine & supplier IDs; no inventory-accounting, stock-coverage, lead-time-demand, required-stock, or replenishment-calculation errors; no risk label/score mismatches; no identified future-data leakage |
| Target definition | `demand_quantity = quantity_sold + unmet_demand` |
| Documented ML-readiness | Gradient Boosting test MAE **8.072** vs naïve lag-1 baseline **10.984** (a reference to *verify*, never to hard-code in UI) |

> **Do not generate a replacement dataset. Do not create fake data and present it as the project dataset.** The real dataset file is placed by the developer at `data/raw/<dataset_file>.csv`. If the file is absent, the Dataset Management page must show a clear "Dataset not found — place file at …" state rather than inventing data.

### 9.2 Runtime verification (light)
On import, verify: column set matches the documented schema; row count ≈ 155,210; 85 distinct medicines; 15 suppliers; 11 categories; date range; no null/duplicate keys. Show pass/fail per check. This is a **runtime confirmation**, not a rebuild of the validation study.

### 9.3 Logical fields the system needs
The physical column names come from `DATA_DICTIONARY.md`. The mapping table is stored in code (`backend/app/dataset/column_map.py`) and displayed in the Dataset Management → Column Mapping tab.

| Logical field | Purpose |
|---|---|
| record_id | Unique row key |
| date | Time index |
| medicine_id, medicine_name | Medicine identity |
| category | Medicine category (11) |
| supplier_id, supplier_name | Supplier identity (15) |
| quantity_sold | Observed sales |
| unmet_demand | Observed lost demand |
| demand_quantity | **Forecast target** (= sold + unmet) |
| opening_stock / closing_stock / current stock | Inventory state |
| stock_out_flag | Stock-out indicator (analytics/validation only) |
| lead_time_days | Supplier lead time |
| safety_stock | Safety stock |
| reorder_level / reorder_point (if present) | Low-stock logic |
| MOQ (minimum order quantity) | Replenishment rounding |
| open_orders / on_order qty | Inventory position |
| stock_coverage_days | Dataset-computed coverage (**cross-check only; not a feature**) |
| lead_time_demand | Dataset-computed LTD (**cross-check only**) |
| required_stock | Dataset-computed required stock (**cross-check only**) |
| replenishment_required, replenishment_qty | Dataset-computed (**cross-check only**) |
| risk_label, risk_score | Dataset-computed (**cross-check only**) |
| calendar/seasonal/other attributes | Candidate features **if causally available** (see 12.4) |

> Antigravity must classify each of the 72 columns into one of: **KEY**, **STATIC ATTRIBUTE**, **TARGET COMPONENT**, **KNOWN-IN-ADVANCE (calendar)**, **OBSERVED-AFTER-THE-FACT (leakage-prone)**, **DERIVED-FROM-TARGET/INVENTORY (forbidden as feature)**. Save this classification to `docs/dataset/COLUMN_CLASSIFICATION.md` in Phase 5 and have the human developer review it before ML begins.

### 9.4 How the dataset is stored
- Raw file stays untouched in `data/raw/`.
- `medicines`, `suppliers`, `categories` are populated from distinct dataset values.
- `daily_records` holds the history rows needed by the app and ML (keys, demand components, inventory state, lead time, safety stock, MOQ, open orders, and dataset-computed cross-check columns). Do **not** create a 72-column duplicate table unless the column classification shows they are needed.
- Processed ML-ready frame is cached as `data/processed/features_v<N>.parquet` (or CSV if parquet is unavailable); it is reproducible from the DB/raw via script.

### 9.5 `as_of_date` & live operation
- After the first import: `as_of_date = max(date)` (2025-12-31).
- `inventory_current` is initialised per medicine from its last daily record (closing stock, open orders, safety stock, MOQ, lead time).
- Forecasts and risk are computed for dates `as_of_date + 1 … as_of_date + H`.
- When new transactions are recorded, `inventory_current` changes immediately. Daily demand from new SALE transactions can be aggregated into `daily_records`-compatible rows (source = `TRANSACTIONS`) for future retraining; the UI labels data source (DATASET vs LIVE).
- The system must **not** pretend the real calendar date is 2025-12-31. The UI shows "Data as of: <as_of_date>" in the header.

---

## 10. System Architecture

```
┌───────────────────────────────────────────────────────────┐
│ React + TypeScript (Vite) — runs on localhost:5173        │
│ Pages · Components · API service layer · TanStack Query   │
└───────────────▲───────────────────────────────────────────┘
                │ REST / JSON over HTTP (JWT)
┌───────────────┴───────────────────────────────────────────┐
│ FastAPI — runs on localhost:8000                          │
│  Routers → Services (business logic) → Repositories/ORM   │
│  ├─ Auth & RBAC          ├─ Inventory & Transaction svc   │
│  ├─ Dataset svc          ├─ Risk & Replenishment svc      │
│  ├─ ML pipeline (pkg)    ├─ Alert svc · Report svc        │
└───────────────▲───────────────────────────────────────────┘
                │ SQLAlchemy 2.0 / psycopg
┌───────────────┴───────────────────────────────────────────┐
│ PostgreSQL (local install, managed via pgAdmin)           │
└───────────────────────────────────────────────────────────┘
        ML artifacts on disk: backend/ml_artifacts/ (joblib) + metadata in DB
```

Principles: layered backend (router → service → repository); ML code isolated in `app/ml/` and callable by services and CLI; deterministic seeds; configuration via `.env`; no Docker.

### 10.1 Key data flows
1. **Import flow:** CSV → validate → map → write `suppliers/categories/medicines/daily_records` → init `inventory_current` → log `dataset_imports`.
2. **Training flow:** `daily_records` → preprocess → features → chronological split → baselines + candidates → metrics → select → refit → save artifact + `ml_runs` row.
3. **Forecast flow:** active model + latest history → multi-step forecast per medicine → `forecasts`.
4. **Risk flow:** `forecasts` + `inventory_current` (+ lead time, safety stock, MOQ, open orders) → risk calculator → `risk_results` → alert engine → `alerts` → replenishment engine → `replenishment_recommendations`.
5. **Transaction flow:** POST transaction → validate → lock inventory row → apply delta → write transaction → (optionally mark risk results *stale* and show "Re-run analysis" prompt).
6. **UI flow:** pages call `/api/v1/...` via the service layer; TanStack Query handles caching/loading/error.

---

## 11. Frontend Architecture

### 11.1 Stack
Vite + React 18 + TypeScript (strict). React Router, TanStack Query, TanStack Table, React Hook Form + Zod, Axios, Tailwind CSS with a small hand-built component set (shadcn/ui-style on Radix primitives is allowed), Recharts, lucide-react icons, date-fns. Vitest + React Testing Library for tests.

### 11.2 Structure
```
frontend/src/
  app/            # router, providers, layout shell
  components/
    ui/           # Button, Card, Badge, Input, Select, Modal, Drawer, Tabs, Toast, Tooltip, Skeleton, Table, Pagination...
    layout/       # Sidebar, Header, PageHeader, AppShell
    charts/       # LineForecastChart, BarChart, RiskDonut, Sparkline, StockGauge
    domain/       # RiskBadge, StockStatusBadge, KpiCard, MedicineSelect, AlertItem, RecommendationCard
    feedback/     # EmptyState, ErrorState, LoadingState, ConfirmDialog
  pages/          # one folder per page (Login, Dashboard, Inventory, ...)
  api/            # axios client + one service file per module (returns typed promises)
  mocks/          # ISOLATED mock data (Phases 1–2 only); chosen by VITE_USE_MOCKS=true
  hooks/ lib/ types/ styles/ utils/
```

### 11.3 Mock-data rules
- `frontend/src/mocks/` is the **only** place for mock data. Components and pages never import mock files directly; they call `api/*` service functions.
- Each service function has a mock branch (`import.meta.env.VITE_USE_MOCKS`) returning data of the **exact TypeScript type** that the real API will return.
- Mock data must be realistic (plausible medicine names, categories, stock levels, lead times, risk distributions), clearly labelled in a code comment as MOCK, and must **not** be presented as the real dataset. In Phase 9 the mocks folder is disabled; remove it before final submission or leave it unused behind the flag.
- Medicine names in mocks are illustrative; no dosage/clinical text.

### 11.4 State & error handling
Server state via TanStack Query (retry policy, stale times). Global error boundary. Axios interceptor attaches JWT and handles 401 (redirect to login) and 5xx (toast). Every list/chart/detail has **loading, empty, and error states** (Sec. 17.4).

---

## 12. Machine-Learning Architecture

Pipeline: **Dataset → Preprocessing → Feature Engineering → Chronological Split → Baseline Models → Candidate Models → Evaluation → Model Selection → Forecast Generation**

### 12.1 Code layout (`backend/app/ml/`)
```
ml/
  config.py          # horizons, split dates, seeds, feature list
  preprocessing.py   # type coercion, date handling, sorting, checks, continuity
  features.py        # lag/rolling/calendar/static features (leakage-safe)
  split.py           # chronological split + rolling-origin backtest folds
  baselines.py       # naive, seasonal naive, rolling means
  models.py          # sklearn candidates + statsmodels wrappers
  evaluate.py        # MAE, RMSE, MAPE(non-zero), WAPE, per-horizon, per-medicine
  train.py           # orchestrates training, selection, refit, artifact save
  forecast.py        # multi-step forecast generation
  registry.py        # save/load artifacts (joblib) + metadata
scripts/
  train_models.py    # CLI entry (reproducible)
  generate_forecasts.py
```

### 12.2 Preprocessing
- Parse dates; sort by (medicine_id, date); assert one row per medicine-date; assert contiguous daily index per medicine (expected 1,826 days).
- Type validation and coercion for numeric columns; assert non-negativity of demand.
- Recompute `demand_quantity` and assert equality with `quantity_sold + unmet_demand` (consistency check).
- Missing-value and duplicate checks (expected: none; checks still run and report).
- **No imputation, outlier removal, or scaling that uses future data.** If any transformation is fitted (encoders, scalers), fit **on training data only**.

### 12.3 Feature engineering (all computed per medicine, using only information available **before** the forecast day)
| Group | Features |
|---|---|
| Lags | `demand_lag_1, 2, 3, 7, 14, 21, 28` (extend to 365 only if useful and available) |
| Rolling (on `demand.shift(1)`) | mean/std/min/max over 3, 7, 14, 28 days; EWM mean |
| Calendar (known in advance) | day-of-week, day-of-month, week-of-year, month, quarter, is-weekend, day-of-year sine/cosine (annual seasonality), holiday flag only if in data |
| Trend | difference between short and long rolling means; slope of last 28 days; time index |
| Seasonal | same-weekday lag (7, 14), same-period-last-year demand if available (lag 364/365) |
| Static medicine attributes | category (encoded), supplier (encoded), lead time, medicine-level historical mean demand (computed from **training window only**) |
| Other dataset variables | Only if the classification proves they are known at forecast time (e.g., planned promotion/price if such fields exist) |

### 12.4 Data-leakage prevention (MANDATORY)
1. Chronological split only; **no random shuffling** for primary evaluation.
2. Rolling statistics computed with `shift(1)` before rolling, so the window never includes the target day.
3. **Forbidden as model inputs:** same-day `quantity_sold`, `unmet_demand`, `demand_quantity`, stock-out flag, closing stock/coverage, required stock, lead-time demand, replenishment flags/quantities, risk label/score, and any column derived from them for time ≥ t. (Their *lagged* values are allowed only if the classification confirms they are computed solely from data up to t−1, and only if they demonstrably help; default is **exclude**.)
4. Target encodings/medicine-level statistics computed on the training window only.
5. Scalers/encoders fit on training data, applied to validation/test.
6. Hyperparameter tuning uses the validation period (or rolling-origin folds **inside the training period**); the test period is touched **once** for the final report.
7. Production forecast for dates after 2025-12-31 uses only data ≤ 2025-12-31 (plus live transactions if added).
8. Include an automated **leakage test** (Sec. 22.6): shifting future values must not change earlier predictions; feature list must not intersect the forbidden list.

### 12.5 Chronological split
| Partition | Default period | Use |
|---|---|---|
| Train | 2021-01-01 → 2023-12-31 | Fit models |
| Validation | 2024-01-01 → 2024-12-31 | Tune/select |
| Test | 2025-01-01 → 2025-12-31 | Final, one-time report |

Dates are configurable in `ml/config.py`. After selection, **refit the chosen model on train + validation** (hyper-parameters frozen) — and, for production forecasting, optionally on all data through the final date — then save the artifact. Document which window each reported metric used.

### 12.6 Models
**Baselines (always run first):** naïve lag-1; seasonal naïve (lag-7); 7-day rolling mean; 28-day rolling mean; per-medicine historical mean.

**Candidates (evaluate; do not add more without justification):**
1. Linear Regression (with the lag/rolling/calendar features) — simple interpretable reference
2. Random Forest Regressor
3. Gradient Boosting (scikit-learn `GradientBoostingRegressor`, or `HistGradientBoostingRegressor` if runtime requires; document the choice) — reproduce the documented ML-readiness setup first
4. ARIMA (statsmodels, small order grid; per medicine or representative subset)
5. Exponential Smoothing / Holt-Winters (statsmodels; weekly seasonality)

Global ML models (1–3) train **one model across all 85 medicines** using medicine/category features; statistical models (4–5) are per-series. Record training time per model. Skip a candidate and document why if it is clearly infeasible; **do not pad the comparison**.

### 12.7 Evaluation
- Metrics: **MAE, RMSE** (primary), **MAPE** (computed only where actual > 0, noting count excluded), **WAPE** (robust).
- Report: overall, per-category, per-medicine (top/bottom 10), and **per forecast horizon** (h = 1, 7, 14, 30) using a multi-step backtest that mimics production (forecast from an origin date with no access to later actuals). Use several origin dates across the test year (e.g., every 30 days) to get stable numbers.
- **Reproduction check:** the one-step Gradient Boosting vs lag-1 comparison should be reproduced in the same *ballpark* as documented (MAE 8.072 vs 10.984). Differences are reported honestly in the Model Performance page; never forced to match.
- Selection rule (documented, deterministic): lowest validation MAE averaged over h ∈ {1, 7, 14, 30}, tie-broken by simplicity/training time; must beat the best baseline on validation; confirm on test. Store the rule and numbers in `ml_runs.selection_reason`.
- Residual standard deviation per medicine (validation) is stored to build approximate prediction intervals and safety-stock fallback.

### 12.8 Forecast generation
- Default horizon 30 days (config; must be ≥ the maximum supplier lead time in the data, check at runtime and warn otherwise).
- **Recursive multi-step** forecasting for ML models (feed predictions back into lag/rolling features) — implemented carefully so each step uses only earlier predictions/actuals. If multi-step error at long horizons is poor, a **direct multi-horizon** variant may be evaluated; adopt only if measurably better.
- Output per medicine/day: `predicted_demand`, `lower`, `upper` (approx. interval), `model_run_id`.
- Clip negative predictions to 0; round only for display (store floats).

### 12.9 Reproducibility
Fixed random seeds; saved config (feature list, split dates, hyper-parameters, library versions) in `ml_runs.config_json`; `pip freeze` captured in the run metadata; CLI `python scripts/train_models.py` reproduces the run; artifacts versioned `model_<runid>.joblib`.

---

## 13. Inventory & Demand Terminology

| Term | Definition (as used in this system) |
|---|---|
| Demand (`demand_quantity`) | `quantity_sold + unmet_demand` |
| Current stock (on-hand) | Units physically available now (`inventory_current.current_stock`) |
| Open orders | Units ordered (manually, outside the system) but not yet received |
| Inventory position | `current_stock + open_order_qty` |
| Lead time (L) | Supplier lead time in days (per medicine/supplier) |
| Safety stock (SS) | Buffer units (dataset field; fallback formula in 14.4) |
| MOQ | Minimum order quantity |

---

## 14. Stock Coverage, Lead-Time Demand & Required Stock

> **Single rule:** if `DATA_DICTIONARY.md` defines a formula for any of the quantities below, **the dictionary's definition wins** (validation confirmed those dataset calculations are correct). The formulas here are the default/expected definitions and must be **verified against the dataset's own columns in Phase 7** by a cross-check script (reporting match rate). If a mismatch is found, adjust to the dictionary and document the change.

Let `d̂(k)` be the forecast demand for day *k* after `as_of_date`, and `L` = lead time days (integer; round up fractional), `S` = current on-hand stock.

### 14.1 Expected daily demand
`expected_daily_demand = mean( d̂(1) … d̂(L) )` (mean forecast over the lead-time window; if L > horizon, raise a data warning and use the available horizon). A second figure, `avg_daily_demand_next_7d`, is displayed for UI context.

### 14.2 Stock coverage (days)
`stock_coverage_days = S / expected_daily_demand` (if expected_daily_demand = 0 → coverage = ∞, store as `NULL` with `coverage_capped = 999` for sorting). More precise variant (shown in the drill-down): **days until stock-out** = smallest *k* such that `Σ_{i=1..k} d̂(i) ≥ S`.

### 14.3 Lead-time demand
`lead_time_demand (LTD) = Σ_{k=1..L} d̂(k)`

### 14.4 Safety stock
Use the dataset's `safety_stock` value (stored per medicine in `inventory_current`; editable by Manager). Fallback if absent: `SS = z × σ_d × √L`, where σ_d is the validation residual standard deviation, and *z* from the configured service level (default 95% → 1.65).

### 14.5 Required stock
`required_stock = LTD + SS`
(Interpreted as the stock needed on hand **at the moment of ordering** to cover demand until the new order arrives while keeping the safety buffer.)

### 14.6 Sufficiency check ("is inventory enough until replenishment?")
- `covers_lead_time = (S ≥ LTD)`
- `above_required = (S ≥ required_stock)`
- `shortfall = max(0, required_stock − inventory_position)`
- `days_of_cover_vs_lead_time = stock_coverage_days − L` (negative → expected stock-out before a new order could arrive)

---

## 15. Stock-Out Risk Classification

### 15.1 Default rule (use dictionary's rule if defined — see R8)
| Level | Condition |
|---|---|
| **HIGH** | `S ≤ 0` **or** `S < LTD` (cannot cover demand during the lead time) |
| **MEDIUM** | `S ≥ LTD` **and** `S < required_stock` (covers lead time but eats into safety stock) |
| **LOW** | `S ≥ required_stock` |

Open orders do **not** change the level but are **shown** next to it and considered in the recommendation (Sec. 16). *(If the dictionary's rule factors open orders in, follow it.)*

### 15.2 Risk score (0–100, for sorting)
Default: `risk_score = clamp(100 × (1 − S / required_stock), 0, 100)` (if required_stock = 0 → 0). Thresholds for levels are stored in `settings` and editable by Admin; default consistency with 15.1 is maintained by a unit test.

### 15.3 Risk explanation (template-based, no LLM needed)
Generated string with real numbers, e.g.:
> "HIGH risk: 120 units on hand, but expected demand over the 9-day supplier lead time is 168 units (≈18.7/day). Stock would last about 6.4 days. Required stock (incl. safety stock of 40) is 208. Open orders: 0."

### 15.4 Output record (`risk_results`)
medicine_id, forecast_run_id/model_run_id, as_of_date, current_stock, open_order_qty, expected_daily_demand, stock_coverage_days, days_until_stockout, lead_time_days, lead_time_demand, safety_stock, required_stock, shortfall, risk_score, risk_level, explanation, computed_at.

### 15.5 Cross-check vs dataset
Admin-only tool: for a sampled set of historical dates, recompute risk using dataset values and compare with the dataset's `risk_label`; show agreement %. Expected ≈ 100% for the formulas defined by the dictionary. Informational; does not block releases but must be run once in Phase 7.

### 15.6 Stock status (separate from risk; instantaneous)
`OUT_OF_STOCK` if S = 0; `LOW_STOCK` if S ≤ reorder level (or ≤ safety stock if no reorder level); else `IN_STOCK`.

---

## 16. Replenishment Recommendations

For each active medicine after risk analysis:

```
inventory_position = current_stock + open_order_qty
raw_need           = required_stock − inventory_position
if raw_need ≤ 0  → no recommendation (or auto-resolve existing pending one)
else:
    qty = max(raw_need, MOQ)
    qty = ceil(qty)                      # integer units
    (if a pack/order-multiple exists in data: round up to that multiple)
```
Optional enhancement (S): add a configurable **review-period buffer**: `+ expected_daily_demand × review_days` (default 0) so one order covers more than the bare minimum. Keep default = 0 for transparency.

Each recommendation stores: medicine, supplier, current stock, open orders, expected daily demand, coverage days, lead time, lead-time demand, safety stock, required stock, MOQ, recommended qty, risk level, priority (HIGH risk first, then days-until-stock-out ascending), explanation, status, timestamps, decision user.

**Priority & urgency:** `urgent` if days_until_stockout < lead_time (an order today still arrives too late → also highlights "consider expediting/alternative supplier" **as a generic note, not an action by the system**).

**Human workflow:** `PENDING → ACCEPTED | DISMISSED`, `ACCEPTED → ORDER_PLACED (manual)`. `ORDER_PLACED` updates `open_order_qty`. The system never contacts any supplier. Replenishment recommendations are regenerated each risk run; PENDING ones are updated, decided ones are preserved.

Where the dataset lacks a needed field (e.g., MOQ), the recommendation is still produced with `MOQ = 1` and a visible note "MOQ not available".

---

## 17. UI / UX Requirements

### 17.1 Visual identity
Must look like a **professional pharmacy inventory & analytics product**, not a generic AI dashboard.
- **Palette:** calm clinical teal/green primary (e.g., teal-700 `#0F766E`), deep slate neutrals, white surfaces, soft gray page background `#F5F7F8`. Accent blue for info. **Risk colors:** LOW green, MEDIUM amber, HIGH red — always accompanied by an icon/text label (never color alone, for accessibility).
- **Typography:** one humanist sans (Inter or IBM Plex Sans) + tabular-numeral monospace/tabular figures for quantities. Clear scale: 12/14/16/20/24/32.
- **Spacing:** 4-pt grid; cards use 16–24 px padding; consistent 8/12/16/24 gaps.
- **Shape/elevation:** 8 px radius cards, 1 px borders, minimal shadows. No gradients-on-everything, no purple/neon "AI" styling, no decorative emoji.
- **Iconography:** lucide-react, 16/20 px, consistent stroke.
- **Density:** data-dense but readable tables (zebra optional, sticky header, row hover, right-aligned numerics).
- Optional dark mode (C).

### 17.2 Layout
Left **Sidebar** (collapsible; icons + labels; role-aware items; active highlight), top **Header** (page title/breadcrumb, global search, "Data as of" chip, notification bell with count, user menu). Content max-width ~1440 px. **Responsive:** ≥1280 full layout; 768–1279 collapsed sidebar, 2-column cards; <768 off-canvas sidebar, single column, tables become horizontally scrollable or card-lists.

### 17.3 Shared components (Phase 1 deliverables)
Buttons (primary/secondary/ghost/destructive, sizes, loading), cards (KPI, chart, list), badges (risk, status), tables (sortable, selectable, paginated, sticky header), forms (text, number, select, date, textarea, validation messages), modals/drawers/confirm dialogs, dropdown menus, search input with debounce, filter bar (chips + dropdowns + reset), toasts, tabs, tooltips, skeleton loaders, empty/error/loading state components, pagination, breadcrumbs, date-range picker, stat delta indicators, progress/coverage bar.

### 17.4 Loading / empty / error states (required for **every** data view)
- **Loading:** skeletons matching the layout (no bare spinners for tables/charts).
- **Empty:** icon + explanation + primary action (e.g., "No transactions yet — Record a transaction").
- **Error:** message, safe technical hint, **Retry** button; 401 → login; 403 → "Not authorized" page; 404 page; offline/network error banner.
- **Forms:** inline validation, disabled-while-submitting, success toast, failure toast with message.

### 17.5 Search / filter / sort
- Tables: server-side pagination (page, page_size), sort by column, multi-filter; URL query params reflect state (shareable/back-button-safe).
- Global search (header): medicines by name/ID → navigates to Medicine Details.
- Debounced 300 ms; clear-all filters; persisted filter state per page (session).

### 17.6 Accessibility & polish
Keyboard navigation, focus rings, ARIA labels on icon buttons, contrast ≥ WCAG AA, `prefers-reduced-motion` respected, consistent number/date formatting (en-IN or configurable), units shown.

---

## 18. Frontend Pages (detailed)

Routes: `/login`, `/`, `/inventory`, `/medicines`, `/medicines/:id`, `/transactions`, `/forecast`, `/risk`, `/replenishment`, `/alerts`, `/datasets`, `/reports`, `/settings`.

### 18.1 Login
Centered card, product mark, email/password, validation, error message for bad credentials, loading state, disabled while submitting, "Decision support only" footer note. Optional demo-credentials hint in dev only.

### 18.2 Dashboard
- **KPI cards (top row):** Total Medicines; Total Units in Stock; High-Risk Medicines; Medium-Risk Medicines; Replenishment Needed; Open Alerts. Each shows value + small context (e.g., delta vs. previous run if available).
- **Charts:** Risk distribution (donut); Stock-coverage distribution (bar by coverage bucket); Demand trend (line: last 90 days actual + forecast next 30 days, aggregate or selectable category); Top 10 medicines by risk (horizontal bars with coverage days); Inventory by category (bar); Replenishment quantity by supplier (bar).
- **Tables/lists:** "Needs attention" (top 10 HIGH-risk with coverage, lead time, recommended qty, link); Recent transactions (last 10); Latest alerts (last 8) with severity icons.
- **Controls:** category filter, "Run risk analysis" button (role-restricted) with last-run timestamp; model chip ("Model: <name>, trained <date>").
- All values from API (mock in Phase 2). Empty-state when no risk run exists: "Run risk analysis to see predictions."

### 18.3 Inventory
KPI strip; filter bar (category, supplier, stock status, risk, search); table: Medicine, Category, Supplier, Current Stock, Safety Stock, Reorder Level, Open Orders, Coverage Days (with progress bar), Lead Time, Risk badge, Stock-status badge, actions; row click → details; export CSV. Bulk actions limited (export).

### 18.4 Medicines
Table with search/filter/sort; **Add Medicine** modal/drawer; edit; deactivate (confirm); category and supplier selects. Role-gated actions. Includes a **Suppliers** tab (list/add/edit suppliers, medicines per supplier, avg lead time).

### 18.5 Medicine Details
Header (name, ID, category, supplier, risk badge, stock-status badge) and tabs:
- **Overview:** key numbers (current stock, open orders, coverage, lead time, safety stock, required stock, MOQ), risk explanation card, active recommendation card (with accept/dismiss).
- **Demand history:** line chart (daily/weekly toggle, date-range selector, sold vs unmet stacked).
- **Forecast:** history + forecast chart with interval band, horizon selector, lead-time window shaded, model info.
- **Inventory & calculation:** step-by-step "forecast → coverage → lead-time demand → required stock → risk" visual (the **explainability panel**).
- **Transactions:** filtered table for this medicine.
- **Edit** drawer.

### 18.6 Transactions
Filter bar (date range, type, medicine, user); table (Date/time, Type badge, Medicine, Quantity (+/−), Resulting stock, Reference/notes, User); **New Transaction** modal (type, medicine autocomplete, quantity, date (default now), supplier for purchases, reason for adjustments/damaged/expired, notes) with live preview "Stock will change from X to Y" and error if negative; summary cards (today's sales, receipts, adjustments); export CSV.

### 18.7 Demand Forecast
Medicine selector (searchable), horizon toggle (7/14/30), chart (history, forecast, interval), model-info card (name, trained on, selection reason), **Model comparison** tab (baselines vs candidates table: MAE/RMSE/MAPE/WAPE per horizon; bar chart), **Backtest** tab (actual vs predicted on test period), category-aggregate tab, "Generate forecasts" (Admin) with run status.

### 18.8 Stock-Out Risk
KPI strip (HIGH/MEDIUM/LOW counts), filter (risk level, category, supplier), table (Medicine, Current Stock, Predicted Daily Demand, Coverage Days, Lead Time, Lead-time Demand, Safety Stock, Required Stock, Shortfall, Risk badge, score bar), **row drawer** with the calculation chain + explanation, "Run risk analysis" with timestamp, staleness banner if transactions occurred after last run, decision-support notice.

### 18.9 Replenishment
Tabs: Pending / Accepted / Ordered / Dismissed / All. Cards or table: medicine, supplier, risk, current stock, open orders, required stock, lead time, MOQ, **recommended qty**, urgency flag, explanation. Actions: Accept, Dismiss (reason), Mark Order Placed (manual, editable qty, optional PO reference note) with confirm dialog stating "This does not place an order with the supplier." Group-by-supplier view; export CSV.

### 18.10 Alerts
Filter (type, severity, status, medicine); list/table with severity icon, message (with numbers), medicine link, timestamps; acknowledge / resolve / dismiss; bulk acknowledge; unread count mirrored in header bell; empty state "No active alerts".

### 18.11 Dataset Management
Stepper layout: **1 Source** (upload or bundled file) → **2 Preview** (table, dtypes) → **3 Schema verification** (pass/fail list vs documented 72-column schema) → **4 Validation** (checks with expected vs actual; mirrors documented 17 checks where applicable at runtime) → **5 Column mapping** → **6 Preprocess** (report) → **7 Import** (progress, result, `as_of_date`). Plus **Statistics** tab and **Import history** table. Admin only for import/preprocess.

### 18.12 Reports
Report type cards/select, filters, preview table + chart, **Export CSV** (PDF stretch), generated-at stamp, empty state when no data.

### 18.13 Settings
Tabs: Profile; Thresholds & Parameters (Admin); Users (Admin: table, add, role change, activate/deactivate); Model (active model, retrain, last run info); About (version, limitations/disclaimer, dataset provenance "synthetic, no patient data").

---

## 19. Tech Stack & Dependencies

**No Docker/containers.** Direct local setup.

### 19.1 Required software
| Software | Version |
|---|---|
| Node.js | 20 LTS or newer (with npm) |
| Python | 3.11 or 3.12 |
| PostgreSQL | 15 or 16 (local install) |
| pgAdmin 4 | current |
| VS Code (or Antigravity IDE) | current |
| Git + GitHub account | current |
| Postman or Insomnia | current |

### 19.2 Backend (`requirements.txt`, pin versions when generated)
fastapi, uvicorn[standard], pydantic v2, pydantic-settings, sqlalchemy 2.x, alembic, psycopg[binary] (v3), python-multipart, PyJWT (or python-jose), passlib[argon2] or bcrypt, pandas, numpy, scikit-learn, statsmodels, joblib, pyarrow (optional, for parquet), python-dotenv; dev: pytest, pytest-cov, httpx, ruff (or flake8), black. Optional: scipy (statsmodels dependency).

### 19.3 Frontend (`package.json`)
react, react-dom, react-router-dom, @tanstack/react-query, @tanstack/react-table, axios, react-hook-form, zod, @hookform/resolvers, recharts, tailwindcss (+ postcss, autoprefixer), lucide-react, date-fns, clsx, tailwind-merge, Radix UI primitives as needed; dev: typescript, vite, @vitejs/plugin-react, vitest, @testing-library/react, @testing-library/jest-dom, eslint, prettier. Optional: Playwright for E2E (C).

### 19.4 Do NOT add
Docker, Redis, Celery, RabbitMQ/Kafka, GraphQL, microservices, Kubernetes, cloud services, TensorFlow/PyTorch, MLflow servers, extra databases.

---

## 20. Backend Architecture

### 20.1 Structure
```
backend/
  app/
    main.py                 # app factory, CORS, routers, exception handlers
    core/                   # config.py, security.py, logging.py, deps.py, errors.py
    db/                     # base.py, session.py, models/ (SQLAlchemy), migrations via alembic/
    schemas/                # Pydantic request/response models
    api/v1/                 # routers: auth, users, medicines, suppliers, inventory,
                            #   transactions, datasets, forecasts, risk, alerts,
                            #   replenishment, dashboard, reports, settings, ml
    services/               # business logic (inventory_service, transaction_service,
                            #   risk_service, replenishment_service, alert_service,
                            #   dataset_service, forecast_service, report_service)
    repositories/           # DB access helpers (optional thin layer)
    dataset/                # column_map.py, validators.py, importer.py
    ml/                     # see Sec. 12.1
  alembic/ alembic.ini
  scripts/                  # train_models.py, generate_forecasts.py, seed_admin.py, import_dataset.py
  tests/                    # unit/ integration/ ml/
  ml_artifacts/             # saved models (git-ignored)
  .env.example
```

### 20.2 Conventions
- API prefix `/api/v1`; JSON; ISO-8601 dates; snake_case in API; consistent response envelopes for lists: `{items, total, page, page_size}`.
- Pydantic validation on all inputs; services contain logic; routers stay thin.
- Standard error format: `{ "error": { "code": "...", "message": "...", "details": ... } }` with correct HTTP status codes.
- Logging: structured, request id, no sensitive data; separate logger for ML runs.
- CORS limited to the local frontend origin.
- Auto-generated OpenAPI docs at `/docs` (used with Postman/Insomnia).
- Long operations (import, training, risk run) return a job/run id; status endpoints poll progress.

---

## 21. Authentication & Authorization

- Users table with hashed passwords, role, active flag, last_login.
- `POST /auth/login` → access token (e.g., 30 min) + refresh token (e.g., 7 days); `POST /auth/refresh`; `GET /auth/me`.
- Dependency `require_role(...)` guards routes.
- Seed script creates the first Admin from `.env` (never hard-coded passwords in source; documented dev defaults only in `.env.example`).
- Rate-limit or lockout after repeated failed logins is optional (C).

**Permission matrix**

| Capability | Admin | Inventory Manager | Pharmacy Staff |
|---|:--:|:--:|:--:|
| View dashboard, inventory, forecasts, risk, alerts | ✔ | ✔ | ✔ |
| Record SALE / CUSTOMER_RETURN | ✔ | ✔ | ✔ |
| Record PURCHASE, SUPPLIER_RETURN, ADJUSTMENT, DAMAGED, EXPIRED | ✔ | ✔ | ✖ |
| Create/edit medicines & suppliers | ✔ | ✔ | ✖ |
| Acknowledge alerts | ✔ | ✔ | ✔ |
| Resolve/dismiss alerts | ✔ | ✔ | ✖ |
| Run risk analysis | ✔ | ✔ | ✖ |
| Accept/dismiss/mark-ordered recommendations | ✔ | ✔ | ✖ |
| Reports / export | ✔ | ✔ | View only |
| Dataset import/preprocess | ✔ | ✖ | ✖ |
| Train models / generate forecasts | ✔ | ✖ | ✖ |
| Settings / thresholds / users | ✔ | ✖ | ✖ |

---

## 22. Database Architecture (PostgreSQL)

Keep tables to what the requirements and dataset need. Use Alembic migrations. `snake_case`, `id` PKs (bigint identity; dataset IDs kept as `code` strings where present), `created_at/updated_at` timestamps.

### 22.1 Tables

**users** — id, name, email (unique), password_hash, role (ENUM admin/manager/staff), is_active, last_login_at, created_at.

**categories** — id, name (unique). *(11 rows from dataset)*

**suppliers** — id, code (unique, dataset supplier ID), name, contact_name, email, phone, default_lead_time_days, notes, is_active, created_at, updated_at.

**medicines** — id, code (unique, dataset medicine ID), name, category_id → categories, supplier_id → suppliers, unit (e.g., strip/bottle/unit), is_active, created_at, updated_at. *(No clinical fields.)*

**inventory_current** — medicine_id (PK, FK → medicines), current_stock (≥0), safety_stock, reorder_level (nullable), moq, lead_time_days, open_order_qty (≥0), as_of_date, updated_at. *(One row per medicine; the live state.)*

**daily_records** — id, medicine_id, date, quantity_sold, unmet_demand, demand_quantity, opening_stock, closing_stock, stock_out_flag, lead_time_days, safety_stock, moq, open_order_qty, plus dataset-computed cross-check columns (stock_coverage_days, lead_time_demand, required_stock, replenishment_required, replenishment_qty, risk_label, risk_score) and other columns the classification (Sec. 9.3) marks as needed; `source` (DATASET/LIVE), `import_id` FK. **Unique (medicine_id, date).** Indexes on (medicine_id, date) and (date).

**transactions** — id, medicine_id, type (ENUM), quantity (positive integer; direction implied by type), stock_before, stock_after, txn_datetime, supplier_id (nullable), reason (nullable), reference (nullable), notes, created_by → users, voided_of_id (nullable self-FK). Indexes on (medicine_id, txn_datetime), (type), (txn_datetime).

**dataset_imports** — id, filename, file_hash, row_count, column_count, status, validation_json, mapping_json, started_at, finished_at, imported_by.

**ml_runs** — id, status, started_at, finished_at, config_json (features, split dates, params, versions), metrics_json (all candidates × horizons), selected_model_name, selection_reason, artifact_path, is_active, created_by.

**forecasts** — id, ml_run_id, medicine_id, forecast_date, horizon_day (1..H), predicted_demand, lower, upper, generated_at. Unique (ml_run_id, medicine_id, forecast_date). *(Keep only the latest N runs to limit size.)*

**risk_results** — fields in Sec. 15.4, plus id, ml_run_id; index on (computed_at), (risk_level). Keep latest run as "current" via `is_current` flag or by max(computed_at).

**replenishment_recommendations** — id, medicine_id, supplier_id, risk_result_id, recommended_qty, current_stock, open_order_qty, expected_daily_demand, coverage_days, lead_time_days, lead_time_demand, safety_stock, required_stock, moq, risk_level, priority_rank, is_urgent, explanation, status (PENDING/ACCEPTED/DISMISSED/ORDER_PLACED), decided_by, decided_at, decision_note, ordered_qty, created_at, updated_at.

**alerts** — id, medicine_id (nullable), type (ENUM), severity, status, title, message, data_json, dedup_key, created_at, acknowledged_by/at, resolved_at.

**app_settings** — key (PK), value_json, updated_by, updated_at. (Thresholds, horizon, service level, review days, demand-spike %, deviation %.)

**audit_log** (S) — id, user_id, action, entity, entity_id, detail_json, created_at. (Light-weight; for transactions, decisions, imports, training.)

### 22.2 Relationships
categories 1—N medicines; suppliers 1—N medicines; medicines 1—1 inventory_current; medicines 1—N daily_records / transactions / forecasts / risk_results / replenishment_recommendations / alerts; ml_runs 1—N forecasts; risk_results 1—N replenishment_recommendations (latest); users 1—N transactions/decisions; dataset_imports 1—N daily_records.

### 22.3 Integrity rules
`CHECK (current_stock >= 0)`, `CHECK (open_order_qty >= 0)`, positive quantities on transactions, FKs with `ON DELETE RESTRICT`, soft-delete via `is_active`. Stock updates happen in a single DB transaction using `SELECT … FOR UPDATE` on the `inventory_current` row.

### 22.4 Transaction stock effects
| Type | Stock effect |
|---|---|
| SALE | − quantity |
| PURCHASE | + quantity; open_order_qty −= min(quantity, open_order_qty) |
| CUSTOMER_RETURN | + quantity |
| SUPPLIER_RETURN | − quantity |
| ADJUSTMENT | ± (explicit sign; reason required) |
| DAMAGED | − quantity (reason required) |
| EXPIRED | − quantity |

---

## 23. API Requirements (`/api/v1`)

Auth required (Bearer JWT) except `/auth/login`. All list endpoints support `page`, `page_size`, `sort`, `order`, and relevant filters.

| Module | Endpoints |
|---|---|
| **Auth** | `POST /auth/login`, `POST /auth/refresh`, `POST /auth/logout`, `GET /auth/me` |
| **Users** (Admin) | `GET /users`, `POST /users`, `PATCH /users/{id}`, `POST /users/{id}/deactivate` |
| **Categories** | `GET /categories` |
| **Suppliers** | `GET /suppliers`, `POST /suppliers`, `GET /suppliers/{id}`, `PATCH /suppliers/{id}`, `GET /suppliers/{id}/medicines` |
| **Medicines** | `GET /medicines` (search, category, supplier, risk, status), `POST /medicines`, `GET /medicines/{id}`, `PATCH /medicines/{id}`, `POST /medicines/{id}/deactivate`, `GET /medicines/{id}/history?from&to&granularity`, `GET /medicines/{id}/calculation` (explainability chain) |
| **Inventory** | `GET /inventory` (filters), `GET /inventory/summary`, `GET /inventory/{medicine_id}`, `PATCH /inventory/{medicine_id}/parameters` (safety stock, reorder level, MOQ, lead time — Manager/Admin; audit-logged) |
| **Transactions** | `GET /transactions`, `POST /transactions`, `GET /transactions/{id}`, `POST /transactions/{id}/void`, `GET /transactions/summary`, `GET /transactions/export` |
| **Datasets** (Admin) | `POST /datasets/upload`, `GET /datasets/bundled`, `GET /datasets/{id}/preview`, `POST /datasets/{id}/verify-schema`, `POST /datasets/{id}/validate`, `GET/PUT /datasets/{id}/mapping`, `POST /datasets/{id}/preprocess`, `POST /datasets/{id}/import`, `GET /datasets/imports`, `GET /datasets/statistics`, `GET /datasets/{id}/report` |
| **ML / Forecast** | `POST /ml/train` (Admin; async), `GET /ml/runs`, `GET /ml/runs/{id}`, `GET /ml/runs/{id}/metrics`, `POST /ml/runs/{id}/activate`, `POST /forecasts/generate` (Admin), `GET /forecasts/{medicine_id}?horizon`, `GET /forecasts/aggregate?category`, `GET /forecasts/backtest/{medicine_id}` |
| **Risk** | `POST /risk/run`, `GET /risk` (filters), `GET /risk/summary`, `GET /risk/{medicine_id}`, `GET /risk/crosscheck` (Admin) |
| **Replenishment** | `GET /replenishment`, `GET /replenishment/{id}`, `POST /replenishment/{id}/accept`, `POST /replenishment/{id}/dismiss`, `POST /replenishment/{id}/order-placed`, `GET /replenishment/export` |
| **Alerts** | `GET /alerts`, `GET /alerts/unread-count`, `POST /alerts/{id}/acknowledge`, `POST /alerts/{id}/resolve`, `POST /alerts/{id}/dismiss`, `POST /alerts/bulk-acknowledge` |
| **Dashboard** | `GET /dashboard/summary`, `GET /dashboard/charts` (risk distribution, coverage buckets, demand trend, top risk, inventory by category, replenishment by supplier), `GET /dashboard/needs-attention`, `GET /dashboard/recent-transactions` |
| **Reports** | `GET /reports/{type}` (JSON), `GET /reports/{type}/export?format=csv` |
| **Settings** | `GET /settings`, `PUT /settings` (Admin), `GET /system/status` (health, as_of_date, active model, last runs), `GET /health` (public) |

Async operations (`/datasets/.../import`, `/ml/train`, `/forecasts/generate`, `/risk/run`) return `{ "job_id" | "run_id", "status" }` and expose status via the corresponding GET.

**There is intentionally no endpoint that places a purchase order or contacts a supplier.**

### 23.1 Alert rules (engine)
| Type | Trigger (defaults, configurable) | Severity |
|---|---|---|
| HIGH_RISK | risk_level = HIGH | CRITICAL |
| LOW_STOCK | stock_status LOW_STOCK/OUT_OF_STOCK | WARNING / CRITICAL if out |
| REPLENISHMENT_REQUIRED | pending recommendation exists | WARNING (CRITICAL if urgent) |
| DEMAND_SPIKE | mean forecast demand next 7 days > recent 28-day actual mean × (1 + spike%) (default 30%) | WARNING |
| FORECAST_DEVIATION | over last N days of **live** data, WAPE > threshold (default 40%) or actual demand > upper bound on k consecutive days — only applicable once live data exists | INFO/WARNING |

Every alert message includes the numbers that triggered it.

---

## 24. Development Phases (STRICT ORDER)

> **Antigravity must execute exactly one phase at a time.** After each phase: (1) run the verification checklist, (2) summarize what was built and any deviations, (3) wait for human confirmation (or explicit instruction) before starting the next phase. Do not start Phase N+1 code during Phase N.

### Phase 1 — UI Foundation (START HERE)
**Build:** Vite + React + TS project; Tailwind config with design tokens (Sec. 17.1); **AppShell** (Sidebar, Header, PageHeader, routing skeleton for all 13 routes with placeholder pages); the **shared component library** (Sec. 17.3); toast system; skeleton/empty/error components; responsive behaviour; a hidden dev-only **`/_styleguide`** route showcasing every component and state.
**Files:** `frontend/` scaffold, `components/ui/*`, `components/layout/*`, `components/feedback/*`, `styles/`, `app/router`.
**No backend. No real data.** Only static demo content inside the styleguide.
**Exit criteria:** `npm run dev` works; `npm run build` and `tsc --noEmit` and `eslint` pass; styleguide shows all components with loading/empty/error variants; layout verified at 1440, 1024, 768, 390 px widths; keyboard focus visible; no console errors; look-and-feel approved by human.

### Phase 2 — Complete UI Screens (mock data)
**Build:** all 13 pages (Sec. 18) using the `api/` service layer + `mocks/` (Sec. 11.3) with typed models in `src/types` that mirror Sec. 22/23 shapes; charts; tables with sort/filter/pagination (client-side against mocks, written so server-side params are already in the service signatures); modals/forms with Zod validation; role-aware menu items (mock current user switcher in dev).
**Exit criteria:** every page reachable and navigable; every data view demonstrates loading/empty/error states (toggle via dev flag); forms validate; responsive; no mock imports outside `api/` and `mocks/`; types compile; human sign-off. **Export `docs/api-contract.md` listing every endpoint + TS type the UI expects** (feeds Phase 3).

### Phase 3 — Backend Foundation
**Build:** FastAPI project structure (Sec. 20.1), `config` with `.env`, DB session, logging, error handlers, health endpoint, Alembic init, auth (login/refresh/me, hashing, JWT), RBAC dependency, user seed script, basic users API; Postman/Insomnia collection.
**Exit criteria:** server runs with `uvicorn`; `/docs` loads; login works; role guards tested; pytest for auth/RBAC passes.

### Phase 4 — Database & Core Application
**Build:** models + migrations for Sec. 22; CRUD & logic for categories, suppliers, medicines, inventory_current, transactions (with stock effects & locking), users; settings; alerts/replenishment/risk/forecast **tables** (schema only, populated later). Seed from **real dataset medicines/suppliers** is deferred to Phase 5; for now use a tiny **test fixture** (in `tests/fixtures`, never presented as the dataset).
**Exit criteria:** migrations apply on a fresh DB; transaction rules tested (negative stock blocked, concurrency lock, purchase reduces open orders, void); API matches `docs/api-contract.md` for these modules.

### Phase 5 — Dataset Integration
**Build:** dataset service: upload/bundled file, preview, schema verification, runtime validation, column mapping, **column classification doc**, preprocessing, idempotent import into DB, init `inventory_current`, statistics; Dataset Management page wired to real APIs.
**Exit criteria:** import of the **real** dataset yields 155,210 rows / 85 medicines / 15 suppliers / 11 categories / 1,826 days per medicine; duplicate import is a no-op; stats match the documented figures (5,067,888 sold; 100,883 unmet; 2,590 stock-outs; 5,423 replenishment-required); page works with loading/error states; `COLUMN_CLASSIFICATION.md` reviewed.

### Phase 6 — Machine Learning
**Build:** `app/ml/*` per Sec. 12; CLI scripts; `/ml` and `/forecasts` APIs; Forecast page wired.
**Order:** preprocessing → features → split → baselines → reproduce documented GB-vs-lag-1 check → candidates → horizon-aware evaluation → selection → refit → artifact → forecast generation.
**Exit criteria:** reproducible run (same seed → same metrics); metrics table stored and shown; leakage tests pass; selected model beats best baseline on validation and test (if not, report honestly and select the best baseline — do not fabricate improvement); forecasts persisted for all 85 medicines.

### Phase 7 — Stock-Out Risk & Decision Support
**Build:** risk service (Sec. 14–15), calculation chain endpoint, explanations, risk run API, cross-check against dataset formulas, Risk page + Medicine Details calculation tab wired.
**Exit criteria:** unit tests for coverage/LTD/required stock/risk with hand-computed cases and edge cases (zero demand, zero stock, L > horizon, missing MOQ); cross-check report generated (match rate documented); results visible in UI.

### Phase 8 — Alerts & Replenishment
**Build:** alert engine (Sec. 23.1) with dedup/auto-resolve; replenishment engine (Sec. 16) and workflow endpoints; Alerts + Replenishment pages wired; header bell count.
**Exit criteria:** deterministic tests for each alert type; recommendation maths tested (MOQ rounding, open orders); workflow transitions enforced; confirmed that **no code path** contacts a supplier or auto-orders; "Order Placed" updates open orders correctly.

### Phase 9 — Frontend/Backend Integration
**Build:** switch every page to real APIs; wire dashboard, inventory, medicines, transactions, reports; set `VITE_USE_MOCKS=false`; remove hard-coded values; verify loading/empty/error states with real latencies; fix contract mismatches.
**Exit criteria:** grep shows no mock imports in production paths; every dashboard number traceable to an API/DB source; end-to-end demo flow works (Sec. 27).

### Phase 10 — Testing & Final Integration
**Build:** complete tests (Sec. 25), edge cases, performance checks, security checks, UI polish pass, README with setup, demo script, final report assets (screenshots, metrics).
**Exit criteria:** Definition of Done (Sec. 28) satisfied.

---

## 25. Testing Strategy

| Layer | Tooling | What to test |
|---|---|---|
| Backend unit | pytest | Stock-effect rules, coverage/LTD/required-stock/risk functions, replenishment maths (MOQ, open orders), alert rules, dedup, permission checks |
| Backend integration | pytest + httpx TestClient + a **separate local test database** | Auth flow, RBAC, CRUD, transactions with locking, dataset import (small fixture), risk run → alerts → recommendations pipeline, error formats |
| Database | pytest + Alembic | Migrations up/down, constraints (negative stock blocked), unique keys, FK restrictions |
| Dataset | pytest | Schema verify, validators detect injected faults (nulls, dup keys, bad dates) on a **tiny test fixture**, idempotent import, row/medicine counts on the real dataset (marked `@pytest.mark.real_data`) |
| ML | pytest | Feature leakage tests, split boundaries (no overlap, strictly chronological), reproducibility (same seed → same output), metric functions on hand-computed cases, forecast shape/non-negativity, baseline < candidate comparison recorded not asserted |
| Frontend unit | Vitest + RTL | Components (badges, tables, forms validation), hooks, formatters |
| Frontend integration | Vitest + MSW or mock service layer | Pages render loading/empty/error/data states, filters/sorting, role-based UI |
| API manual | Postman/Insomnia collection | Every endpoint, happy + error paths (committed to repo) |
| E2E (S) | Playwright | Login → dashboard → run risk → view recommendation → accept → mark ordered → record purchase |
| Responsive/manual | Browser devtools | 1440/1024/768/390 px |
| Non-functional | Manual + scripts | Query timing, page load, import time |

**Edge cases checklist:** zero demand; zero stock; negative stock attempt; very large quantities; lead time longer than forecast horizon; missing MOQ; medicine with no history; inactive medicine; duplicate transaction submission (idempotency/double-click); token expiry mid-session; empty database; stale risk results after new transactions; dataset with extra/missing/renamed columns; wrong file type; huge file; concurrent transactions on one medicine.

### 25.1 ML leakage tests (explicit)
1. Feature-list ∩ forbidden-list = ∅.
2. Mutating actual demand at dates ≥ t must not change features/predictions for dates < t.
3. Train max date < validation min date < test min date.
4. Rolling features at row t equal rolling of data ≤ t−1 (hand-checked sample).
5. Scalers/encoders are fitted on train only (assert via fit data hash/length).

---

## 26. Non-Functional Requirements

**Performance:** list endpoints respond < 500 ms for typical filters with indexes (local); dashboard summary < 1 s; chart endpoints use pre-aggregated queries; forecast/risk reads served from stored tables (no on-request model inference except explicit "generate"); training may take minutes and runs async with progress; dataset import of ~155k rows < 2–3 min using bulk insert (`COPY`/`executemany`/chunked pandas `to_sql`); frontend initial load < 3 s on local; table pagination server-side; avoid N+1 queries.
**Reliability:** transactional stock updates; idempotent import; graceful errors; safe retries.
**Usability:** consistent UI, clear explanations, plain-language alerts.
**Maintainability:** modular code, typed (TS strict, Python type hints), linted, README per major folder.
**Portability:** Windows/macOS/Linux local setup; no container dependency.
**Explainability:** every risk and recommendation shows the inputs and formula chain.
**Accessibility:** WCAG AA contrast, keyboard operable.
**Observability (light):** structured logs, `/system/status`.

### 26.1 Security
Password hashing; JWT with expiry; RBAC on every protected route; Pydantic validation; SQLAlchemy parameterized queries (no raw string SQL); CORS restricted to local origin; file-upload checks (extension, size cap, content sniffing, store outside web root, sanitized filename); secrets only in `.env` (git-ignored; `.env.example` committed); no secrets or PII in logs; generic login error messages; HTTP security headers where simple; dependency pinning; audit trail for stock-affecting and decision actions; no clinical data stored; dataset documented as synthetic. Frontend: token storage in memory + refresh token in httpOnly cookie (preferred) or `localStorage` with documented trade-off; escape output (React default), no `dangerouslySetInnerHTML`.

---

## 27. Local Development Setup (no Docker)

### 27.1 One-time setup
1. Install Node 20+, Python 3.11/3.12, PostgreSQL 15/16, pgAdmin, Git, VS Code/Antigravity, Postman/Insomnia.
2. In pgAdmin (or `psql`): create DB `pharmastock` and a role `pharmastock_user` with password; also create `pharmastock_test` for tests.
3. Clone repo; `cd backend`; `python -m venv .venv`; activate; `pip install -r requirements.txt`.
4. Copy `backend/.env.example` → `backend/.env` and set: `DATABASE_URL=postgresql+psycopg://pharmastock_user:<password>@localhost:5432/pharmastock`, `TEST_DATABASE_URL=…/pharmastock_test`, `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS`, `CORS_ORIGINS=http://localhost:5173`, `DATASET_PATH=../data/raw/<file>.csv`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `ML_ARTIFACT_DIR=./ml_artifacts`.
5. `alembic upgrade head`; `python scripts/seed_admin.py`.
6. `cd frontend`; `npm install`; copy `.env.example` → `.env` with `VITE_API_BASE_URL=http://localhost:8000/api/v1` and `VITE_USE_MOCKS=true|false`.
7. Place the dataset at `data/raw/` and the docs at `docs/dataset/`.

### 27.2 Run
- Backend: `uvicorn app.main:app --reload --port 8000` (docs at `/docs`).
- Frontend: `npm run dev` (http://localhost:5173).
- Train: `python scripts/train_models.py`; forecast: `python scripts/generate_forecasts.py` (or via Admin UI).
- Tests: `pytest` (backend), `npm test` (frontend).

### 27.3 Demo script (for viva/presentation)
Login (Manager) → Dashboard (data-as-of, KPIs) → Dataset Management (show verified/imported dataset) → Forecast (compare baseline vs model, show metrics honestly) → Risk (drill into one HIGH medicine: forecast → coverage → LTD → required stock → risk) → Replenishment (accept → "Order Placed (manual)") → record a PURCHASE transaction (open orders drop, stock rises) → re-run risk (level changes) → Alerts → Reports export. Emphasize the human-in-the-loop principle.

---

## 28. Folder / Project Structure

```
pharmastock-iq/
├─ README.md
├─ PRD.md
├─ .gitignore                 # .env, .venv, node_modules, ml_artifacts, data/processed, __pycache__
├─ data/
│  ├─ raw/                    # real dataset (not committed if large; documented)
│  └─ processed/              # cached feature files
├─ docs/
│  ├─ dataset/                # DATA_DICTIONARY.md, VALIDATION_REPORT.md, COLUMN_CLASSIFICATION.md
│  ├─ api-contract.md
│  └─ screenshots/
├─ frontend/                  # see Sec. 11.2
├─ backend/                   # see Sec. 20.1
└─ postman/                   # Postman/Insomnia collection export
```

---

## 29. Error Handling Requirements

- **Backend:** domain exceptions (`InsufficientStockError`, `NotFoundError`, `ValidationFailed`, `ForbiddenError`, `ConflictError`) mapped to HTTP 400/404/409/422/403; unexpected errors → 500 with generic message + logged traceback + request id; validation errors return field-level details.
- **Frontend:** global error boundary; per-query error states with retry; form-level and field-level errors; toasts for transient failures; distinct UI for 401/403/404/500/network; never show raw stack traces.
- **ML/dataset jobs:** failures captured in run/import record (`status=FAILED`, `error_message`), visible in UI, safe to retry.

---

## 30. Integration Strategy

1. **Contract-first:** `docs/api-contract.md` (from Phase 2) is the shared contract; backend Pydantic schemas must match the TS types; any change is made in both and noted.
2. **Module-by-module wiring (Phase 9 order):** Auth → Medicines/Suppliers → Inventory → Transactions → Dataset → Forecast → Risk → Replenishment → Alerts → Dashboard → Reports → Settings. After each, set that module's service functions to real mode, verify, then continue.
3. Keep the mock flag until the last module is wired; then disable globally.
4. Verify numbers: spot-check dashboard KPIs against SQL queries in pgAdmin.

---

## 31. Final Testing (Phase 10 acceptance run)

Full regression: backend + frontend suites green; fresh-DB bootstrap from scratch following README (migrate → seed → import real dataset → train → forecast → risk → alerts → recommendations) succeeds in order; Postman collection passes; responsive check; role checks (log in as each role and verify permitted/blocked actions); edge-case checklist; performance spot checks; screenshots captured; metrics/figures in the report come from the app/DB.

---

## 32. Definition of Done

The project is complete when **all** are true:

- [ ] Runs locally end-to-end with **no Docker** using the steps in Sec. 27.
- [ ] All 13 pages implemented, responsive, with loading/empty/error states, using **real data** (no hard-coded dashboard values).
- [ ] Real dataset imported and verified (155,210 rows; 85/15/11; 2021-01-01→2025-12-31; stats match documented figures); no fabricated data anywhere.
- [ ] Preprocessing, features, chronological split, baselines, candidates, evaluation (MAE/RMSE/MAPE-non-zero/WAPE, per horizon), selection, and forecasting implemented and **reproducible**; all reported metrics come from actual runs.
- [ ] Leakage prevention implemented and tested (Sec. 12.4, 25.1).
- [ ] Coverage, lead-time demand, required stock, safety stock, replenishment need, risk level/score, and explanations implemented, unit-tested, and cross-checked against the dataset's definitions.
- [ ] Alerts (5 types) with dedup/auto-resolve; recommendations with the human workflow; **no autonomous ordering anywhere**.
- [ ] Medicine, supplier, inventory, and transaction management work with correct, transactional stock updates and RBAC.
- [ ] Authentication and authorization enforced server-side per Sec. 21.
- [ ] Test suites pass; Postman collection committed; edge cases handled.
- [ ] No clinical/diagnosis/dosage/prescription content; disclaimer visible; dataset documented as synthetic.
- [ ] README (setup, run, train, test, demo script) and screenshots complete; code lint/type checks pass.
- [ ] Project is demonstrable and explainable within a ~10-minute presentation.

---

## 33. Open Items for the Human Developer

1. Provide `DATA_DICTIONARY.md` and `VALIDATION_REPORT.md` under `docs/dataset/` and the dataset file under `data/raw/` **before Phase 4/5** (the physical column names and the exact definitions of coverage, required stock, replenishment, and risk come from them).
2. Confirm the maximum supplier lead time in the data (determines the minimum forecast horizon; default 30 days assumes ≤ 30).
3. Confirm whether the dataset includes MOQ, open orders, reorder level, and pack/order-multiple columns (affects Sec. 16 notes).
4. Decide whether PDF export is wanted (stretch) and whether dark mode is wanted (stretch).
5. Approve the train/validation/test years (default 2021–23 / 2024 / 2025).

---

## 34. Glossary
**Demand** — sold + unmet units. **Unmet demand** — units wanted but not available. **Stock-out** — stock reached zero. **Lead time** — days from ordering to receipt. **Lead-time demand** — forecast demand during lead time. **Safety stock** — buffer. **Required stock** — lead-time demand + safety stock. **Inventory position** — on-hand + open orders. **MOQ** — minimum order quantity. **MAE/RMSE/MAPE/WAPE** — forecast error metrics. **Chronological split** — train on earlier dates, validate/test on later dates. **Leakage** — using information unavailable at prediction time.

---

### START INSTRUCTION
**Begin now with Phase 1 — UI Foundation (Sec. 24). Post a short plan (files/components to be created and how you will verify), build only Phase 1, run the exit-criteria checks, report, and stop for confirmation before Phase 2.**
