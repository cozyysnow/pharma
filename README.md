# PharmaStock IQ — Pharmacy Stock-Out Prediction & Decision Support System

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![React 19](https://img.shields.io/badge/React-19-61dafb.svg)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178c6.svg)](https://www.typescriptlang.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4+-38bdf8.svg)](https://tailwindcss.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

PharmaStock IQ is an enterprise clinical pharmacy inventory intelligence platform combining multi-step machine learning demand forecasting, deterministic stock-out risk assessment, and human-in-the-loop replenishment decision support.

---

## 🌟 Key Features

- **Multi-Step Demand Forecasting:** Time-series forecasting across 85 medicines and 11 therapeutic categories with strictly enforced zero future data leakage.
- **Explainable Stock-Out Risk:** Deterministic risk scoring ($0-100$) and classification (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`) computed from lead-time demand, stock coverage, and safety stock buffers.
- **Step-by-Step Calculation Chain:** Transparent mathematical breakdown and feature attribution for every medicine.
- **Human-in-the-Loop Procurement:** Multi-stage replenishment recommendations (`PENDING` $\to$ `ACCEPTED` $\to$ `ORDERED` / `DISMISSED`) enforcing Supplier Minimum Order Quantities (MOQ). **No autonomous external ordering.**
- **Real-Time Alerting Engine:** 5 alert types (`HIGH_RISK`, `LOW_STOCK`, `REPLENISHMENT_REQUIRED`, `DEMAND_SPIKE`, `FORECAST_DEVIATION`) with automatic deduplication and condition auto-resolution.
- **Atomic Concurrency:** Transaction ledger with row-level database locking strictly blocking negative inventory states.

---

## 🏗️ System Architecture

```
                    ┌─────────────────────────┐
                    │   React 19 Frontend     │
                    │  Vite + TypeScript + TW │
                    └───────────┬─────────────┘
                                │ REST API (/api/v1)
                                ▼
                    ┌─────────────────────────┐
                    │     FastAPI Backend     │
                    │   Pydantic + RBAC Guard │
                    └───────────┬─────────────┘
          ┌─────────────────────┼─────────────────────┐
          ▼                     ▼                     ▼
┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
│  ML Forecasting   │ │ Risk & Sufficiency│ │ Alert & Workflow  │
│ Gradient Boosting │ │ Calculator Engine │ │ Auto-Dedup Engine │
└───────────────────┘ └───────────────────┘ └───────────────────┘
          │                     │                     │
          └─────────────────────┼─────────────────────┘
                                ▼
                    ┌─────────────────────────┐
                    │   SQLite / PostgreSQL   │
                    │   SQLAlchemy 2.0 ORM    │
                    └─────────────────────────┘
```

---

## 🚀 Quick Start & Installation

### Prerequisites
- Python 3.11+
- Node.js 18+ & npm
- Git

### 1. Backend Setup
```bash
# Clone the repository
git clone https://github.com/pharmastock-iq/pharmastock-iq.git
cd pharma

# Activate virtual environment
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations & seed administrator
alembic upgrade head
python scripts/seed_admin.py

# Launch FastAPI server
uvicorn backend.app.main:app --reload --port 8000
```
- API Documentation (Swagger): `http://localhost:8000/docs`
- Public Health Check: `http://localhost:8000/health`

### 2. Frontend Setup
```bash
# In a separate terminal:
cd frontend
npm install

# Start Vite dev server
npm run dev
```
- Application Web Interface: `http://localhost:5173`

---

## 🔐 Default Authentication Credentials

The system initializes with an administrative account and role-based test profiles:

| Role | Email | Password | Permissions |
|---|---|---|---|
| **Administrator** | `admin@pharmastock.local` | `AdminPassword123!` | Full system administration, ML retraining, user management |
| **Inventory Manager** | `manager@pharmastock.local` | `ManagerPassword123!` | Master catalog edits, replenishment approval, risk re-runs |
| **Pharmacy Staff** | `staff@pharmastock.local` | `StaffPassword123!` | Prescription dispensing, receipts, transaction logging |

---

## 🧪 Testing Suite

Run the full automated test suite covering unit calculations, ML leakage tests, and end-to-end integration:

```bash
# Run all backend tests
pytest backend/tests -v

# Run ML Data Leakage tests specifically
pytest backend/tests/test_ml.py -v

# Run Deterministic Risk Math tests
pytest backend/tests/test_risk.py -v

# Run Alerts & Replenishment Workflow tests
pytest backend/tests/test_alerts_replenishment.py -v

# Run Complete Pipeline Integration test
pytest backend/tests/test_pipeline_integration.py -v
```

### Frontend Build Verification
```bash
cd frontend
npm run build
```
Executes TypeScript type-checking (`tsc -b`) and Vite production bundle generation.

---

## 📊 Machine Learning & Reproducibility

To re-run ML model training and regenerate multi-step forecasts:

```bash
# 1. Train candidate models and select champion
python backend/scripts/train_models.py

# 2. Generate 30-day recursive forecasts across all 85 medicines
python backend/scripts/generate_forecasts.py

# 3. Cross-check risk formula match against historical ground-truth
python backend/scripts/cross_check_risk.py
```

---

## 📁 Repository Structure

```
pharma/
├── backend/
│   ├── alembic/                # Database migrations
│   ├── app/
│   │   ├── api/v1/             # REST endpoints (auth, medicines, risk, alerts, etc.)
│   │   ├── core/               # Configuration, security, logging, errors
│   │   ├── db/models/          # SQLAlchemy domain models
│   │   ├── dataset/            # Importer, validators, preprocessors
│   │   ├── ml/                 # Feature engineering, baselines, training
│   │   ├── schemas/            # Pydantic request & response models
│   │   ├── services/           # Business logic & domain services
│   │   └── main.py             # FastAPI entrypoint & middleware
│   ├── scripts/                # CLI administration & verification scripts
│   └── tests/                  # Pytest test suite
├── docs/
│   ├── api-contract.md         # Full REST API specification
│   ├── DEMO_WALKTHROUGH.md     # 10-minute presentation guide
│   ├── RISK_CROSS_CHECK_REPORT.md # Historical cross-check verification
│   └── pharmastock_postman_collection.json # Ready-to-import API tests
├── frontend/
│   ├── src/
│   │   ├── api/                # API client layer (typed REST calls)
│   │   ├── components/         # Design system & domain components
│   │   ├── context/            # AuthContext & ToastContext
│   │   ├── pages/              # 13 application views
│   │   └── types/              # TypeScript schemas mirroring backend
│   ├── package.json
│   └── vite.config.ts
├── req.md                      # Product Requirements Document
├── tasks.md                    # Project development phase task breakdown
└── README.md                   # System documentation
```

---

## 📋 Definition of Done Checklist

- [x] All 10 development phases completed strictly in order
- [x] Zero mock imports in production paths (`VITE_USE_MOCKS=false`)
- [x] Multi-step forecast generated for all 85 medicines
- [x] Deterministic risk formulas unit-tested against hand-computed scenarios
- [x] Negative stock attempts blocked with atomic row-locking
- [x] Replenishment workflow requires human decision; no auto-orders
- [x] Alerts deduplicate on recurrence and auto-resolve when conditions clear
- [x] Historical risk cross-check report generated (`docs/RISK_CROSS_CHECK_REPORT.md`)
- [x] Postman collection committed (`docs/pharmastock_postman_collection.json`)
- [x] Frontend builds cleanly with zero TypeScript errors (`tsc -b`)
