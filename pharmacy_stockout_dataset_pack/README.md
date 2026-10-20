# Pharmacy Stock-Out Prediction - Synthetic Dataset Pack

155,210 daily records = 85 medicines x 1,826 days (2021-01-01..2025-12-31), 15 suppliers, 11 categories.
**All transactional data is synthetic** (seed 20260101); see `validation_report.md` for checks and limitations.

| File | Purpose |
|---|---|
| medicines.csv | Master: generic name, salt form, strength, dosage form, composition_status |
| categories.csv / suppliers.csv / medicine_suppliers.csv / supplier_disruption_events.csv / calendar.csv | Dimensions |
| inventory_daily.csv | Stock movements and reorder policy per medicine-day |
| demand_sales_daily.csv | Demand, sales, lost sales, price, revenue |
| replenishment_orders.csv | Purchase orders with lead time and fill |
| stockout_prediction_dataset.csv | Modelling table: features + target `stockout_next_7d` |
| stockout_label_lookahead_2026.csv | Simulated 2026-01-01..07 flags used to label the last 7 days of 2025 |
| data_dictionary.csv | Column descriptions |
| validation_checks.csv / validation_report.md | Validation outcomes |
| generate_dataset_pack.py | Regenerates and validates everything |

Join key: `record_id` (daily files), `medicine_id`, `supplier_id`, `category_id`.
Suggested split: time-based (train 2021-2023, validation 2024, test 2025); avoid random splits.
Medicines flagged `UNVERIFIED_REQUIRES_REVIEW` have strength intentionally withheld.
