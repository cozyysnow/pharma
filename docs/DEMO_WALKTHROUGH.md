# PharmaStock IQ — Viva & Demonstration Walkthrough Guide

> **Target Presentation Time:** 10 minutes  
> **Target Audience:** Technical Examiners, Pharmacy Operations Managers, and Clinical Lead Reviewers.

---

## 1. Quick Start / Environment Setup

### Terminal 1: Backend API Server
```powershell
cd backend
.venv\Scripts\activate
uvicorn backend.app.main:app --reload --port 8000
```
- Open Swagger Documentation: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### Terminal 2: Frontend Single Page Application
```powershell
cd frontend
npm run dev
```
- Open Application: `http://localhost:5173`

---

## 2. Recommended 10-Minute Demonstration Script

### Minute 0:00 – 1:30 | Problem Context & System Login
1. **Navigate to:** `http://localhost:5173/login`
2. **Context:** Retail and hospital pharmacies suffer from recurring stock-outs due to static min-max rules that fail to anticipate lead-time demand spikes and supply disruptions.
3. **Action:** Log in as **Administrator** using:
   - **Email:** `admin@pharmastock.local`
   - **Password:** `AdminPassword123!`
4. **Highlight:** The system enforces Role-Based Access Control (RBAC) across three distinct tiers: `ADMIN`, `INVENTORY_MANAGER`, and `PHARMACY_STAFF`.

---

### Minute 1:30 – 3:30 | Operational Dashboard & Executive Monitoring
1. **Navigate to:** `http://localhost:5173/` (Dashboard)
2. **Key Visual Elements:**
   - **6 Real-time KPI Cards:** Total SKUs (85), Inventory Valuation (₹28.5L+), Critical/High Risk counts, Pending Orders, and Active Alerts.
   - **Stock-Out Risk Donut Chart:** Categorization across Low, Medium, High, and Critical risk tiers.
   - **Category Distribution & 7-Day Trend Charts.**
   - **Needs-Attention Table:** Real-time prioritized list of medicines with highest risk scores.
3. **Action:** Click **"Run Risk Analysis"** in the top right.
   - Live API executes deterministic re-evaluation against all 85 medicines in milliseconds.

---

### Minute 3:30 – 5:30 | Medicine Catalog & Calculation Chain Explainability
1. **Navigate to:** `http://localhost:5173/medicines`
2. **Action:** Search for a high-volume medicine (e.g., `Atorvastatin` or `Pantoprazole`), then click on it to open **Medicine Details**.
3. **Inspect the 5 Detailed Tabs:**
   - **Overview:** Active ingredients, dosage form, supplier lead times (mean ± SD), unit cost/price, and storage condition.
   - **Demand History:** Historical daily demand patterns from the 155,210-row dataset.
   - **Demand Forecast (30 Days):** Recharts visualization displaying predicted demand curves with confidence upper/lower bounds.
   - **Calculation Chain & Risk (Core Technical Feature):** Step-by-step mathematical breakdown:
     - *Step 1:* Expected Daily Demand (EDD) across supplier lead time window.
     - *Step 2:* Current Stock Coverage (Days) = `Closing Stock / EDD`.
     - *Step 3:* Lead-Time Demand (LTD) & Safety Stock buffer ($z \cdot \sigma_d \cdot \sqrt{L}$).
     - *Step 4:* Final Risk Score & Natural-language Template Explanation.
     - *Feature Contributions:* Relative factor weightings (Coverage vs Lead Time, Safety Buffer Deficit, Supplier Delivery Reliability).
   - **Audit Trail:** Historical ledger of transactions.

---

### Minute 5:30 – 7:00 | Stock Transactions & Concurrency Safeguards
1. **Navigate to:** `http://localhost:5173/transactions`
2. **Action 1 — Demonstrating Negative Stock Rejection:**
   - Click **"New Transaction"**.
   - Select an item with low stock (e.g. stock = 12). Attempt to record a `SALE` of 50 units.
   - **Result:** System immediately blocks the submission with an atomic domain rejection error: `"Insufficient stock — transaction would result in negative inventory"`.
3. **Action 2 — Legitimate Dispensing & Live Stock Preview:**
   - Record a valid `SALE` of 5 units.
   - Notice the live preview showing `Stock will change: X → X - 5`.
   - Submit: Closing stock is updated atomically with row-level database locking.

---

### Minute 7:00 – 8:30 | Replenishment Workflow (Human-in-the-Loop)
1. **Navigate to:** `http://localhost:5173/replenishment`
2. **Key Principle:** The system **never** places autonomous purchase orders or contacts suppliers externally. All procurement actions require explicit human review.
3. **Tabs & Filters:** `Pending`, `Accepted`, `Ordered`, `Dismissed`, `All`.
4. **Action:**
   - Identify an urgent recommendation. Notice the calculated recommended quantity enforces supplier **Minimum Order Quantity (MOQ)**.
   - Click **"Accept"** with an authorized manager note.
   - Click **"Order Placed"** and enter a purchase order reference (e.g., `PO-2026-NOV-01`).
   - **Result:** The system moves the recommendation to `ORDERED` and atomically increments the medicine's `on_order_units` (open order position), immediately adjusting future risk calculations.

---

### Minute 8:30 – 10:00 | Alert Engine, Auto-Resolution & Conclusion
1. **Navigate to:** `http://localhost:5173/alerts`
2. **Review:**
   - 5 distinct rule types: `HIGH_RISK`, `LOW_STOCK`, `REPLENISHMENT_REQUIRED`, `DEMAND_SPIKE`, and `FORECAST_DEVIATION`.
   - Alert messages embed exact triggering numerical metrics.
3. **Demonstrate Actions:**
   - Single click **Acknowledge** or **Bulk Acknowledge** for routine alerts.
   - Explain the **Auto-Resolution Engine**: When inventory is replenished or risk abates, active alerts automatically transition to `RESOLVED` with audit stamp `"System Auto-Resolve"`.
4. **Header Notification Bell:** Shows live unread alert badge synced with backend.
5. **Conclusion & Viva Defense:** System satisfies all 10 project development phases, Definition of Done, and zero data-leakage ML pipeline standards.
