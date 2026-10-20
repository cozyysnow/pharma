# Dataset Column Classification & Leakage Prevention Guide

## PharmaStock IQ — Feature Classification Taxonomy

Each column across the modelling and operational datasets is classified into exactly one of six structural roles. This classification governs model training, feature extraction, and runtime inference to prevent any temporal data leakage.

---

### Classification Categories

1. **KEY**: Primary keys, foreign keys, or temporal identifiers used for entity resolution, indexing, and alignment. Not used as numeric regressors.
2. **STATIC**: Time-invariant attributes of an entity (e.g. medicine dosage form, category, standard lead time).
3. **TARGET**: The prediction ground truth (e.g. `stockout_next_7d` or future daily demand `demand_t+k`). Must NEVER appear in model feature matrices at inference time.
4. **KNOWN-IN-ADVANCE**: Variables whose values are deterministically known for future time steps (e.g. calendar features, day of week, scheduled holiday, season).
5. **OBSERVED**: Quantities observed and recorded at or up to day $t$ (e.g. current physical closing stock, trailing 7-day average sales, days since last receipt).
6. **DERIVED-FORBIDDEN**: Variables computed using future information or contemporaneous variables that leak the target. Strictly barred from feature sets.

---

### Column-by-Column Classification Table

| Column Name | Classification | Source Table | Rationale & Leakage Safeguards |
|---|---|---|---|
| `record_id` | **KEY** | `stockout_prediction_dataset.csv` | Unique identifier (RECnnnnnn) for each medicine-day pair. |
| `date` | **KEY** | `stockout_prediction_dataset.csv` | Calendar date for chronological splitting and temporal sequencing. |
| `medicine_id` | **KEY** | `medicines.csv` | Primary identifier (MEDnnn) linking master data with daily records. |
| `category_id` | **STATIC** | `categories.csv` | Therapeutic category (CATnn). Categorical feature; constant over time. |
| `supplier_id` | **STATIC** | `suppliers.csv` | Primary contracted vendor (SUPnn). Constant over contract period. |
| `generic_name` | **STATIC** | `medicines.csv` | Active pharmacological entity name. |
| `display_name` | **STATIC** | `medicines.csv` | Formatted clinical label. |
| `strength` | **STATIC** | `medicines.csv` | Clinical strength (e.g. 500 mg, 10 mg/mL). |
| `dosage_form` | **STATIC** | `medicines.csv` | Pharmaceutical form (Tablet, Capsule, Syrup, Injection). |
| `route` | **STATIC** | `medicines.csv` | Administration route (Oral, Topical, Injectable). |
| `unit_of_measure` | **STATIC** | `medicines.csv` | Smallest dispensing unit (tablet, bottle, vial, strip). |
| `pack_size` | **STATIC** | `medicines.csv` | Order pack constraint. |
| `storage_condition` | **STATIC** | `medicines.csv` | Room temperature vs cold chain ($2-8^\circ\text{C}$). |
| `composition_status`| **STATIC** | `medicines.csv` | VERIFIED_STANDARD_REFERENCE vs UNVERIFIED_REQUIRES_REVIEW. |
| `year` | **KNOWN-IN-ADVANCE** | `calendar.csv` | Trend component. Deterministically known for future dates. |
| `month` | **KNOWN-IN-ADVANCE** | `calendar.csv` | Annual seasonality. Deterministically known. |
| `day_of_week` | **KNOWN-IN-ADVANCE** | `calendar.csv` | Weekly seasonality (0 = Monday .. 6 = Sunday). |
| `is_weekend` | **KNOWN-IN-ADVANCE** | `calendar.csv` | Weekend flag (1 for Saturday/Sunday). |
| `season` | **KNOWN-IN-ADVANCE** | `calendar.csv` | Regional seasonal cycle (winter, pre-monsoon, monsoon, post-monsoon). |
| `closing_stock` | **OBSERVED** | `inventory_daily.csv` | End-of-day physical stock balance at day $t$. |
| `on_order_units` | **OBSERVED** | `inventory_daily.csv` | Outstanding purchase orders placed but undelivered by day $t$. |
| `reorder_point` | **OBSERVED** | `inventory_daily.csv` | Inventory replenishment threshold configured for medicine at day $t$. |
| `units_demanded` | **OBSERVED** | `demand_sales_daily.csv` | Total true demand on day $t$. (Used for demand forecasting target at $t+k$). |
| `units_sold` | **OBSERVED** | `demand_sales_daily.csv` | Dispensed sales on day $t$ ($\min(\text{demand}, \text{available})$). |
| `sales_7d_avg` | **OBSERVED** | `stockout_prediction_dataset.csv` | Trailing 7-day average sales through day $t$. |
| `sales_30d_avg` | **OBSERVED** | `stockout_prediction_dataset.csv` | Trailing 30-day average sales through day $t$. |
| `days_of_cover` | **OBSERVED** | `stockout_prediction_dataset.csv` | $\text{closing\_stock} / \text{sales\_30d\_avg}$ capped at 365. |
| `stock_position_cover_days` | **OBSERVED** | `stockout_prediction_dataset.csv` | $(\text{closing\_stock} + \text{on\_order}) / \text{sales\_30d\_avg}$. |
| `days_since_last_receipt` | **OBSERVED** | `stockout_prediction_dataset.csv` | Days elapsed since last vendor shipment delivery. |
| `stockout_days_last_30d` | **OBSERVED** | `stockout_prediction_dataset.csv` | Count of stock-out days during $[t-29, t]$. |
| `supplier_lead_time_mean_days` | **STATIC** | `suppliers.csv` | Contracted supplier baseline lead time. |
| `supplier_full_fill_probability` | **STATIC** | `suppliers.csv` | Contracted probability of receiving complete order quantity. |
| `supplier_disruption_active` | **OBSERVED** | `supplier_disruption_events.csv` | 1 if vendor disruption active on day $t$; 0 otherwise. |
| `unit_price_inr` | **OBSERVED** | `demand_sales_daily.csv` | Unit retail price in INR on day $t$. |
| `stockout_today` | **OBSERVED** | `demand_sales_daily.csv` | 1 if lost sales $> 0$ on day $t$; 0 otherwise. |
| `stockout_next_7d` | **TARGET** | `stockout_prediction_dataset.csv` | **GROUND TRUTH**: 1 if stock-out occurs anywhere in $[t+1, t+7]$. FORBIDDEN as input feature. |
| `lost_sales_units` (day $t$) | **OBSERVED** | `demand_sales_daily.csv` | Daily unmet demand on day $t$. |
| `lost_sales_units` (day $t+k$) | **DERIVED-FORBIDDEN**| Future calculation | Future unmet demand. Directly leaks target. |
| `closing_stock` (day $t+k$) | **DERIVED-FORBIDDEN**| Future inventory | Future stock levels. Strictly barred during inference. |
| `units_sold` (day $t+k$) | **DERIVED-FORBIDDEN**| Future sales | Future sales volume. Strictly barred during inference. |

---

### Enforcement in Pipeline
1. All lag and rolling transformations in `ml/features.py` MUST apply `.shift(1)` to ensure values reflect information available *strictly before* the prediction step.
2. The column `stockout_next_7d` is isolated as `y` and stripped from feature tensor `X`.
3. Multi-step demand forecasts use recursive rollouts where predicted values from step $k-1$ become lagged inputs for step $k$.
