# PharmaStock IQ — Task Breakdown

> Derived from [req.md](file:///c:/Users/kc/Downloads/pharma/req.md) on 2026-10-20.
> Phases are executed strictly in order. Each phase must pass its exit criteria before the next begins.

---

## Phase 1 — UI Foundation (COMPLETED)

| # | Task | Files / Deliverables | Status | Exit Criteria |
|---|------|---------------------|:------:|---------------|
| 1.1 | Scaffold Vite + React + TypeScript project | `frontend/` with `vite.config.ts`, `tsconfig.json`, `package.json` | [x] DONE | `npm run dev` starts; `tsc --noEmit` passes |
| 1.2 | Install all frontend dependencies (React Router, TanStack Query/Table, Tailwind CSS, Recharts, Axios, React Hook Form, Zod, Lucide, date-fns, clsx, tailwind-merge) | `package.json` updated | [x] DONE | `npm install` clean; no peer-dep errors |
| 1.3 | Configure Tailwind with design tokens (palette: teal-700 primary, slate neutrals, risk colors; typography: Inter font; spacing: 4pt grid; radius: 8px) | `tailwind.config.ts`, `src/styles/globals.css` | [x] DONE | Design tokens compile; colors/fonts match Sec. 17.1 |
| 1.4 | Build AppShell layout — collapsible Sidebar + Header (page title, "Data as of" chip, notification bell, user menu) | `components/layout/Sidebar.tsx`, `Header.tsx`, `AppShell.tsx`, `PageHeader.tsx` | [x] DONE | Sidebar collapses; header shows all elements; responsive at 1440/1024/768/390 |
| 1.5 | Set up React Router with all 13 routes + placeholder pages | `app/router.tsx`, `pages/` (Login, Dashboard, Inventory, Medicines, MedicineDetails, Transactions, Forecast, Risk, Replenishment, Alerts, Datasets, Reports, Settings) | [x] DONE | Every route reachable; 404 fallback works |
| 1.6 | Build shared UI components: Button, Card, Badge, Input, Select, Modal, Drawer, Tabs, Toast, Tooltip, Skeleton, Pagination, Breadcrumbs | `components/ui/*` (one file per component) | [x] DONE | Each component renders correctly; loading/disabled states work |
| 1.7 | Build Table component (sortable headers, pagination, sticky header, row hover, right-aligned numerics, zebra optional) | `components/ui/Table.tsx`, `components/ui/DataTable.tsx` | [x] DONE | Sorting and pagination functional |
| 1.8 | Build form components: TextInput, NumberInput, SelectInput, DateInput, TextArea, SearchInput (debounced), FilterBar, DateRangePicker | `components/ui/form/*` | [x] DONE | Zod validation messages display; debounce works |
| 1.9 | Build feedback components: EmptyState, ErrorState, LoadingState, ConfirmDialog, Toast system | `components/feedback/*` | [x] DONE | Each state renders icon + explanation + action button |
| 1.10 | Build domain components: KpiCard, RiskBadge, StockStatusBadge, StatDelta | `components/domain/*` | [x] DONE | Badges show correct colors for LOW/MEDIUM/HIGH and IN_STOCK/LOW/OUT |
| 1.11 | Build chart wrapper components: LineForecastChart, BarChart, RiskDonut, Sparkline, StockGauge (coverage progress bar) | `components/charts/*` | [x] DONE | Recharts renders; responsive |
| 1.12 | Create `/_styleguide` dev route showcasing every component with all states (loading, empty, error, variants) | `pages/Styleguide.tsx` | [x] DONE | Visual review of all components at 1440/1024/768/390px |
| 1.13 | Responsive verification + keyboard focus + accessibility pass | All layout + UI components | [x] DONE | Focus rings visible; ARIA labels on icon buttons; no console errors |
| 1.14 | Lint + type-check + build verification | — | [x] DONE | `npm run build`, `tsc -b` cleanly passes with zero errors |

**Phase 1 overall exit:** Passed. `npm run dev` works; styleguide shows all components; responsive at 4 widths; keyboard nav verified; zero build/lint errors.

---

## Phase 2 — Complete UI Screens (Mock Data) (COMPLETED)

| # | Task | Files / Deliverables | Status | Exit Criteria |
|---|------|---------------------|:------:|---------------|
| 2.1 | Define TypeScript types mirroring DB schemas (User, Medicine, Supplier, Category, InventoryItem, Transaction, DailyRecord, Forecast, RiskResult, Recommendation, Alert, DatasetImport, MlRun, AppSettings) | `src/types/*.ts` | [x] DONE | Types compile; match Sec. 22 table shapes |
| 2.2 | Create API service layer with mock flag (`VITE_USE_MOCKS`) — one service file per module | `src/api/` (auth, medicines, suppliers, inventory, transactions, datasets, forecasts, risk, replenishment, alerts, dashboard, reports, settings) | [x] DONE | Service functions return typed promises; mock branch works |
| 2.3 | Create realistic mock data (plausible medicine names, categories, 85 meds, 15 suppliers, 11 categories, risk distributions) | `src/mocks/*.ts` | [x] DONE | Mock data is realistic; clearly labeled MOCK in comments |
| 2.4 | Build Login page (centered card, product mark, email/password, validation, loading, error) | `pages/Login/` | [x] DONE | Form validates; loading/error states render |
| 2.5 | Build Dashboard page (KPI cards, charts: risk donut, coverage distribution, demand trend, top-10 risk, inventory by category, replenishment by supplier; needs-attention table, recent transactions, latest alerts) | `pages/Dashboard/` | [x] DONE | All 6 KPI cards, 6 charts, 2 tables render with mock data |
| 2.6 | Build Inventory page (KPI strip, filter bar, table with coverage progress bar, risk/status badges, CSV export) | `pages/Inventory/` | [x] DONE | Filter/sort/pagination work; badges correct |
| 2.7 | Build Medicines page (table + search/filter/sort, Add/Edit modals, deactivate, Suppliers tab) | `pages/Medicines/` | [x] DONE | CRUD forms validate; role-gated actions |
| 2.8 | Build Medicine Details page (header + 5 tabs: Overview, Demand History, Forecast, Inventory & Calculation, Transactions) | `pages/MedicineDetails/` | [x] DONE | All tabs render; charts show history + forecast |
| 2.9 | Build Transactions page (filter bar, table, New Transaction modal with live stock preview, summary cards, CSV export) | `pages/Transactions/` | [x] DONE | 7 transaction types; "Stock will change X→Y" preview; negative stock error |
| 2.10 | Build Demand Forecast page (medicine selector, horizon toggle, chart, model info, Model Comparison tab, Backtest tab, Category aggregate tab) | `pages/Forecast/` | [x] DONE | Chart renders history + forecast + interval; comparison table shows metrics |
| 2.11 | Build Stock-Out Risk page (KPI strip, filter, table with calculation drawer, "Run risk analysis" button, staleness banner) | `pages/Risk/` | [x] DONE | Drill-down drawer shows calculation chain + explanation |
| 2.12 | Build Replenishment page (tabs: Pending/Accepted/Ordered/Dismissed/All, cards/table, Accept/Dismiss/Order Placed actions with confirm dialogs) | `pages/Replenishment/` | [x] DONE | Workflow transitions; "does not place order" disclaimer; group-by-supplier view |
| 2.13 | Build Alerts page (filter, list with severity icons, acknowledge/resolve/dismiss, bulk acknowledge, header bell count) | `pages/Alerts/` | [x] DONE | 5 alert types render; unread count in header |
| 2.14 | Build Dataset Management page (stepper: Source → Preview → Schema → Validation → Mapping → Preprocess → Import; Statistics tab; Import History) | `pages/Datasets/` | [x] DONE | Stepper navigation works; all 7 steps render |
| 2.15 | Build Reports page (report type selector, filters, preview table + chart, Export CSV) | `pages/Reports/` | [x] DONE | 7 report types selectable; CSV export button |
| 2.16 | Build Settings page (tabs: Profile, Thresholds/Parameters, Users, Model, About with disclaimer) | `pages/Settings/` | [x] DONE | Admin-only tabs hidden for other roles; disclaimer visible |
| 2.17 | Implement dev-only role switcher for testing role-aware UI | `components/dev/RoleSwitcher.tsx` | [x] DONE | Menu items hide/show per role |
| 2.18 | Loading/empty/error state toggle (dev flag) for every data view | All pages | [x] DONE | Each page shows all 3 states via dev toggle |
| 2.19 | Export API contract document | `docs/api-contract.md` | [x] DONE | Lists every endpoint + TS type the UI expects |
| 2.20 | Full responsive + navigation verification | — | [x] DONE | Every page reachable; no mock imports outside `api/` and `mocks/`; types compile |

**Phase 2 overall exit:** Passed. All 13 pages functional with mock/API data layer; forms validate; responsive at 1440/1024/768/390; types compile; `api-contract.md` exported.


---

## Phase 3 — Backend Foundation (COMPLETED)

| # | Task | Files / Deliverables | Status | Exit Criteria |
|---|------|---------------------|:------:|---------------|
| 3.1 | Scaffold FastAPI project structure | `backend/app/main.py`, `core/`, `db/`, `schemas/`, `api/v1/`, `services/`, `.env.example` | [x] DONE | `uvicorn app.main:app --reload` starts |
| 3.2 | Config management with pydantic-settings + `.env` | `core/config.py`, `.env.example` | [x] DONE | All settings load from env vars |
| 3.3 | Database session setup (SQLAlchemy 2.0 + psycopg) | `db/session.py`, `db/base.py` | [x] DONE | DB connection works |
| 3.4 | Alembic initialization + initial migration | `alembic/`, `alembic.ini` | [x] DONE | `alembic upgrade head` runs clean |
| 3.5 | Error handling (domain exceptions → HTTP status codes, standard error format) | `core/errors.py`, exception handlers in `main.py` | [x] DONE | Errors return `{error: {code, message, details}}` |
| 3.6 | Logging setup (structured, request ID) | `core/logging.py` | [x] DONE | Request IDs in log output |
| 3.7 | User model + migration | `db/models/user.py` | [x] DONE | Users table created |
| 3.8 | Auth service (password hashing, JWT access/refresh tokens) | `core/security.py`, `services/auth_service.py` | [x] DONE | Tokens generated; passwords hashed with bcrypt/argon2 |
| 3.9 | Auth API routes (login, refresh, logout, me) | `api/v1/auth.py` | [x] DONE | Login returns tokens; `/auth/me` returns user |
| 3.10 | RBAC dependency (`require_role`) | `core/deps.py` | [x] DONE | Role guards block unauthorized access |
| 3.11 | Admin seed script | `scripts/seed_admin.py` | [x] DONE | Creates admin from `.env` vars |
| 3.12 | Users API (Admin: list, create, update, deactivate) | `api/v1/users.py` | [x] DONE | CRUD works; only Admin can access |
| 3.13 | Health endpoint | `api/v1/health.py` → `GET /health`, `GET /system/status` | [x] DONE | Returns 200 with status info |
| 3.14 | CORS configuration (localhost:5173 only) | `main.py` | [x] DONE | Frontend can call backend |
| 3.15 | Pytest setup + auth/RBAC tests | `tests/` | [x] DONE | Tests pass with test database |

**Phase 3 overall exit:** Passed. Uvicorn server runs on port 8000; `/health` returns 200 OK; live login works; role guards tested; 9/9 pytest tests green.


---

## Phase 4 — Database & Core Application

| # | Task | Files / Deliverables | Exit Criteria |
|---|------|---------------------|---------------|
| 4.1 | [x] DB models: categories, suppliers, medicines, inventory_current, daily_records, transactions | `db/models/*.py` | All tables with correct relationships, constraints, indexes |
| 4.2 | [x] DB models: dataset_imports, ml_runs, forecasts, risk_results, replenishment_recommendations, alerts, app_settings, audit_log | `db/models/*.py` | Schema-only tables created |
| 4.3 | [x] Alembic migrations for all tables | `alembic/versions/` | `alembic upgrade head` on fresh DB succeeds |
| 4.4 | [x] Pydantic schemas (request/response models for all modules) | `schemas/*.py` | Schemas match `api-contract.md` types |
| 4.5 | [x] Categories API (GET /categories) | `api/v1/categories.py` | Returns list of categories |
| 4.6 | [x] Suppliers CRUD API + medicines-per-supplier | `api/v1/suppliers.py`, `services/supplier_service.py` | List/create/edit/deactivate; medicines by supplier |
| 4.7 | [x] Medicines CRUD API (search, filter by category/supplier/risk/status, sort, pagination) | `api/v1/medicines.py`, `services/medicine_service.py` | Full CRUD; soft-delete if history exists |
| 4.8 | [x] Inventory API (list with filters, summary, parameters update) | `api/v1/inventory.py`, `services/inventory_service.py` | KPI summary; parameter edits audit-logged |
| 4.9 | [x] Transaction service (stock effects with row locking, negative stock rejection, void, purchase reduces open orders) | `services/transaction_service.py` | Atomic stock updates; all 7 types; concurrency safe |
| 4.10 | [x] Transactions API (list, create, void, summary, export) | `api/v1/transactions.py` | Filters, pagination, CSV export |
| 4.11 | [x] Settings API (get/update app settings) | `api/v1/settings.py` | Admin-only update |
| 4.12 | [x] Test fixtures (tiny, non-dataset data for testing) | `tests/conftest.py` | Used by integration tests; isolated test SQLite DB |
| 4.13 | [x] Integration tests (transaction rules, concurrency, constraints) | `tests/test_core_api.py` | Negative stock blocked; purchase reduces open orders; void works; 16/16 tests pass |

**Phase 4 overall exit:** Passed. Migrations applied; transaction engine strictly rejects negative stock with HTTP 400; purchase receipts reduce `on_order_units`; admin voids generate reversing transactions; CSV export functional; 16/16 pytest test suite passed 100%.

---

## Phase 5 — Dataset Integration (COMPLETED)

| # | Task | Files / Deliverables | Status | Exit Criteria |
|---|------|---------------------|:------:|---------------|
| 5.1 | Column mapping module (logical → physical column names from data dictionary) | `dataset/column_map.py` | [x] DONE | Maps all columns across all CSV files |
| 5.2 | Dataset upload / bundled-file detection | `services/dataset_service.py` | [x] DONE | Upload CSV or detect `data/raw/*.csv` |
| 5.3 | Preview endpoint (first N rows, column list, dtypes, counts) | `api/v1/datasets.py` | [x] DONE | Preview renders correctly |
| 5.4 | Schema verification (expected columns per CSV, dtypes, missing/extra/renamed) | `dataset/validators.py` | [x] DONE | Reports pass/fail per column |
| 5.5 | Runtime validation (missing values, duplicates, date range, medicine/supplier counts, negatives) | `dataset/validators.py` | [x] DONE | All checks run; expected all-pass for provided dataset |
| 5.6 | Column classification document (KEY, STATIC, TARGET, KNOWN-IN-ADVANCE, OBSERVED, DERIVED-FORBIDDEN) | `docs/dataset/COLUMN_CLASSIFICATION.md` | [x] DONE | All columns classified; human review requested |
| 5.7 | Preprocessing (type coercion, date handling, sorting, consistency checks, logging every change) | `dataset/preprocessor.py` | [x] DONE | Report generated; no silent alterations |
| 5.8 | Idempotent import (medicines, suppliers, categories, daily_records, init inventory_current) | `dataset/importer.py` | [x] DONE | 155,210 rows; 85 medicines; 15 suppliers; 11 categories; re-import is no-op |
| 5.9 | Dataset statistics endpoint | `api/v1/datasets.py` | [x] DONE | Stats match documented figures |
| 5.10 | Wire Dataset Management page to real APIs | Frontend `pages/Datasets/` | [x] DONE | Stepper works end-to-end with real data |
| 5.11 | Copy dataset files to `data/raw/` | `data/raw/` | [x] DONE | All CSV files from dataset pack placed correctly |

**Phase 5 overall exit:** Passed. Real dataset verified and imported; 155,210 daily records, 85 medicines, 15 suppliers, 11 categories; idempotent re-import verified; dataset validation checks 100% green; all tests pass.

---

## Phase 6 — Machine Learning (COMPLETED)

| # | Task | Files / Deliverables | Status | Exit Criteria |
|---|------|---------------------|:------:|---------------|
| 6.1 | ML config (horizons, split dates 2021-23/2024/2025, seeds, feature list) | `ml/config.py` | [x] DONE | Configurable; dates match Sec. 12.5 |
| 6.2 | Preprocessing module (type coercion, sort, assert one row per medicine-date, demand_quantity consistency) | `ml/preprocessing.py` | [x] DONE | All assertions pass on real data |
| 6.3 | Feature engineering (lags, rolling stats with shift(1), calendar, trend, seasonal, static medicine attributes) | `ml/features.py` | [x] DONE | Features computed per-medicine; no future data leakage |
| 6.4 | Chronological split + rolling-origin backtest folds | `ml/split.py` | [x] DONE | Train < validation < test; no overlap |
| 6.5 | Baseline models (naïve lag-1, seasonal lag-7, 7-day rolling mean, 28-day rolling mean, historical mean) | `ml/baselines.py` | [x] DONE | All 5 baselines produce predictions |
| 6.6 | Reproduce documented GB vs lag-1 check (MAE ~8.072 vs ~10.984 ballpark) | `ml/models.py` | [x] DONE | One-step comparison in same ballpark; reported honestly |
| 6.7 | Candidate models (Linear Regression, Random Forest, Gradient Boosting, ARIMA subset, ETS subset) | `ml/models.py` | [x] DONE | All candidates trained; training time recorded |
| 6.8 | Evaluation module (MAE, RMSE, MAPE non-zero, WAPE; per-horizon h=1,7,14,30; per-medicine; multi-step backtest) | `ml/evaluate.py` | [x] DONE | Metrics computed at all granularities |
| 6.9 | Model selection (lowest validation MAE averaged over horizons, must beat best baseline) | `ml/train.py` | [x] DONE | Selection rule documented; stored in `ml_runs.selection_reason` |
| 6.10 | Refit on train+validation, save artifact (joblib) + metadata | `ml/registry.py`, `ml_artifacts/` | [x] DONE | Artifact saved; config_json captured |
| 6.11 | Multi-step recursive forecast generation (30-day default, clip negatives) | `ml/forecast.py` | [x] DONE | Forecasts for all 85 medicines; non-negative |
| 6.12 | CLI scripts for training and forecasting | `scripts/train_models.py`, `scripts/generate_forecasts.py` | [x] DONE | Reproducible from command line |
| 6.13 | ML/Forecast API endpoints (train async, runs, metrics, activate, generate forecasts, get forecasts) | `api/v1/ml.py`, `api/v1/forecasts.py` | [x] DONE | Async training with status; forecasts served |
| 6.14 | Wire Forecast page to real APIs | Frontend `pages/Forecast/` | [x] DONE | Real metrics and charts |
| 6.15 | Leakage tests (feature list ∩ forbidden = ∅, temporal integrity, scaler fit checks) | `tests/ml/` | [x] DONE | All 5 leakage tests pass |

**Phase 6 overall exit:** Passed. Reproducible training; metrics stored; selected model (Gradient Boosting, Val MAE 16.518 vs Lag-1 23.912) beats baseline; 2,550 forecast points persisted across 85 medicines; 5/5 leakage tests pass 100%.

---

## Phase 7 — Stock-Out Risk & Decision Support

| # | Task | Files / Deliverables | Exit Criteria |
|---|------|---------------------|---------------|
| 7.1 | Risk calculator service (expected daily demand, stock coverage, lead-time demand, safety stock, required stock, sufficiency check) | `services/risk_service.py` | Formulas match Sec. 14 |
| 7.2 | Risk classification (LOW/MEDIUM/HIGH per Sec. 15.1, score 0-100) | `services/risk_service.py` | Classification matches rules |
| 7.3 | Risk explanation generation (template-based with real numbers) | `services/risk_service.py` | Human-readable explanations generated |
| 7.4 | Risk run endpoint (recompute using latest forecasts + current stock) | `api/v1/risk.py` | Results stored in `risk_results` with timestamp |
| 7.5 | Calculation chain endpoint (explainability for medicine details) | `api/v1/medicines.py` → `/medicines/{id}/calculation` | Returns step-by-step calculation |
| 7.6 | Cross-check script (compare app-computed risk vs dataset's risk_label on historical dates) | `scripts/cross_check_risk.py` | Match rate documented |
| 7.7 | Unit tests (zero demand, zero stock, L > horizon, missing MOQ, edge cases) | `tests/unit/test_risk.py` | All hand-computed cases pass |
| 7.8 | Wire Risk page + Medicine Details calculation tab | Frontend pages | Real risk data displayed |

**Phase 7 overall exit:** Risk calculations unit-tested; cross-check run; UI shows calculation chain + explanations.

---

## Phase 8 — Alerts & Replenishment

| # | Task | Files / Deliverables | Exit Criteria |
|---|------|---------------------|---------------|
| 8.1 | Alert engine (5 types: HIGH_RISK, LOW_STOCK, REPLENISHMENT_REQUIRED, DEMAND_SPIKE, FORECAST_DEVIATION) | `services/alert_service.py` | All 5 types trigger correctly |
| 8.2 | Alert deduplication + auto-resolve when condition clears | `services/alert_service.py` | One open alert per (medicine, type); updates not duplicates |
| 8.3 | Alerts API (list, unread count, acknowledge, resolve, dismiss, bulk acknowledge) | `api/v1/alerts.py` | All endpoints work; header bell count |
| 8.4 | Replenishment engine (inventory position < required stock → recommendation with MOQ rounding) | `services/replenishment_service.py` | Calculations match Sec. 16 |
| 8.5 | Replenishment workflow (PENDING → ACCEPTED/DISMISSED → ORDER_PLACED) | `services/replenishment_service.py` | Transitions enforced; ORDER_PLACED updates open_order_qty |
| 8.6 | Replenishment API (list, accept, dismiss, order-placed, export) | `api/v1/replenishment.py` | No code path contacts supplier or auto-orders |
| 8.7 | Wire Alerts + Replenishment pages | Frontend pages | Real data; "Order Placed" disclaimer visible |
| 8.8 | Tests (each alert type, recommendation maths, MOQ rounding, workflow transitions) | `tests/` | Deterministic tests pass |

**Phase 8 overall exit:** Alerts with dedup/auto-resolve; recommendations with human workflow; no autonomous ordering; tests pass.

---

## Phase 9 — Frontend/Backend Integration

| # | Task | Files / Deliverables | Exit Criteria |
|---|------|---------------------|---------------|
| 9.1 | Wire Auth (login/logout/refresh/token handling) | `api/auth.ts` | Login flow works end-to-end |
| 9.2 | Wire Medicines + Suppliers pages | `api/medicines.ts`, `api/suppliers.ts` | CRUD with real data |
| 9.3 | Wire Inventory page | `api/inventory.ts` | Filters, summary, parameter edits |
| 9.4 | Wire Transactions page | `api/transactions.ts` | All 7 types; live stock preview accurate |
| 9.5 | Wire Dataset Management page (already partially done in 5.10) | `api/datasets.ts` | Full stepper with real upload/import |
| 9.6 | Wire Forecast page | `api/forecasts.ts` | Real charts + metrics |
| 9.7 | Wire Risk page | `api/risk.ts` | Real risk data + calculation drawer |
| 9.8 | Wire Replenishment page | `api/replenishment.ts` | Real workflow actions |
| 9.9 | Wire Alerts page + header bell | `api/alerts.ts` | Real alert data + unread count |
| 9.10 | Wire Dashboard (all KPIs, charts, tables from real APIs) | `api/dashboard.ts` | Every number traceable to API/DB |
| 9.11 | Wire Reports + Settings | `api/reports.ts`, `api/settings.ts` | CSV export works; settings editable |
| 9.12 | Set `VITE_USE_MOCKS=false`; remove/disable mocks | `.env` | No mock imports in production paths |
| 9.13 | Verify loading/empty/error states with real latencies | All pages | States display correctly under real conditions |

**Phase 9 overall exit:** Grep shows no mock imports in prod; every dashboard number from API; end-to-end demo flow works.

---

## Phase 10 — Testing & Final Integration

| # | Task | Files / Deliverables | Exit Criteria |
|---|------|---------------------|---------------|
| 10.1 | Complete backend unit tests (stock effects, risk functions, replenishment maths, alert rules) | `tests/unit/` | All pass |
| 10.2 | Complete backend integration tests (full pipeline: import → train → forecast → risk → alerts → recommendations) | `tests/integration/` | Pipeline runs on test DB |
| 10.3 | Frontend component tests (badges, tables, form validation) | `frontend/src/__tests__/` | Vitest + RTL pass |
| 10.4 | Edge cases: zero demand/stock, negative stock attempt, L > horizon, missing MOQ, inactive medicine, empty DB, stale risk, duplicate transaction, token expiry | `tests/edge_cases/` | All handled gracefully |
| 10.5 | Security checks (RBAC on every route, Pydantic validation, no raw SQL, CORS, file upload checks) | Manual + tests | No unauthorized access; no injection |
| 10.6 | Performance spot checks (list endpoints < 500ms, dashboard < 1s, import < 3min) | Manual | Meets non-functional requirements |
| 10.7 | Responsive UI polish pass (1440/1024/768/390) | Manual | All pages look correct at all widths |
| 10.8 | Postman/Insomnia collection (every endpoint, happy + error paths) | `postman/` | Collection committed to repo |
| 10.9 | README with setup instructions, run commands, train/test/demo script | `README.md` | Fresh-DB bootstrap following README succeeds |
| 10.10 | Screenshots for presentation | `docs/screenshots/` | Key pages captured |
| 10.11 | Final report: all metrics from actual runs, demo script verified | `docs/` | Demonstrable in ~10 min presentation |
| 10.12 | Definition of Done checklist verification | — | All 13 items in Sec. 32 checked |

**Phase 10 overall exit:** All tests green; fresh-DB bootstrap works; Postman collection passes; responsive verified; screenshots captured; README complete; Definition of Done satisfied.

---

## Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| 1 | 1.1 – 1.14 | UI Foundation (components, layout, styleguide) |
| 2 | 2.1 – 2.20 | Complete UI Screens with mock data |
| 3 | 3.1 – 3.15 | Backend Foundation (FastAPI, auth, RBAC) |
| 4 | 4.1 – 4.13 | Database & Core Application (models, CRUD, transactions) |
| 5 | 5.1 – 5.11 | Dataset Integration (import, validation, preprocessing) |
| 6 | 6.1 – 6.15 | Machine Learning (pipeline, training, forecasting) |
| 7 | 7.1 – 7.8 | Stock-Out Risk & Decision Support |
| 8 | 8.1 – 8.8 | Alerts & Replenishment |
| 9 | 9.1 – 9.13 | Frontend/Backend Integration |
| 10 | 10.1 – 10.12 | Testing & Final Integration |

**Total: 119 tasks across 10 phases.**
