# Validation Report - Pharmacy Stock-Out Prediction Dataset Pack

**Result: 56/56 checks passed.** All checks re-read the CSV files from disk (independent of the generator's in-memory state).

## Dataset summary

- Daily records: 155,210 (85 medicines x 1,826 days, 2021-01-01 to 2025-12-31)
- Suppliers: 15 | Categories: 11 | Replenishment orders: 11,390 | Disruption events: 47
- Target `stockout_next_7d` prevalence: 18.79%
- Medicines with verified-standard composition: 78; flagged UNVERIFIED_REQUIRES_REVIEW: 7

## Check results

| group | check | result | detail |
|---|---|---|---|
| Structure | Total daily records == 155,210 | PASS | 155210/155210/155210 |
| Structure | 85 medicines | PASS |  |
| Structure | 15 suppliers | PASS |  |
| Structure | 11 categories | PASS |  |
| Structure | Date range 2021-01-01..2025-12-31, 1,826 days | PASS |  |
| Structure | Every medicine has all 1,826 days (no gaps/duplicates) | PASS |  |
| Structure | record_id unique and identical across 3 daily files | PASS |  |
| Structure | Calendar has 1,826 unique dates | PASS |  |
| Keys | PK uniqueness (medicine, supplier, category, order, event) | PASS |  |
| Keys | ID formats consistent (MEDnnn/SUPnn/CATnn/POnnnnnnn/RECnnnnnn) | PASS |  |
| Keys | FK medicines.category_id -> categories | PASS |  |
| Keys | FK medicines.primary_supplier_id -> suppliers | PASS |  |
| Keys | FK daily/orders medicine_id -> medicines | PASS |  |
| Keys | FK orders/bridge/events supplier_id -> suppliers | PASS |  |
| Keys | Every category has >=1 medicine; every supplier is primary for >=1 medicine | PASS | min meds/category=6, min meds/supplier=5 |
| Keys | Order suppliers belong to the medicine's supplier bridge | PASS |  |
| Keys | Modelling table category/supplier match medicines master | PASS |  |
| Medicine master | No duplicate (generic, strength, dosage form) | PASS |  |
| Medicine master | No missing generic name/ingredients/strength/form/status | PASS |  |
| Medicine master | Unverified compositions are flagged (not guessed): strength='UNVERIFIED' iff flagged | PASS | 7 flagged, 78 standard-reference |
| Medicine master | Statuses limited to the two allowed values | PASS |  |
| Medicine master | Verified rows have no 'UNVERIFIED' text in ingredients/strength | PASS |  |
| Medicine master | Pack size positive; units per pack in {1,10} | PASS |  |
| Quality | No nulls in daily tables | PASS |  |
| Quality | No negative inventory values | PASS |  |
| Quality | No negative demand/sales/lost-sales/revenue | PASS |  |
| Inventory logic | closing = opening + received - sold - wastage | PASS |  |
| Inventory logic | opening(t+1) = closing(t) | PASS |  |
| Inventory logic | units_sold <= opening + received | PASS |  |
| Inventory logic | Sales identical across inventory/demand/model tables | PASS |  |
| Inventory logic | sold = min(demand, available); lost = demand - sold | PASS |  |
| Inventory logic | stockout_flag = (lost_sales_units > 0) | PASS |  |
| Inventory logic | revenue = units_sold * unit_price (to 0.01) | PASS |  |
| Replenishment | Orders placed within 2021-2025 only | PASS |  |
| Replenishment | Delivery date > order date; lead_time matches dates | PASS |  |
| Replenishment | Received qty <= ordered; status consistent | PASS |  |
| Replenishment | In-transit orders have null delivery fields and delivery would be after 2025-12-31 | PASS |  |
| Replenishment | Ordered/received quantities are multiples of pack size | PASS |  |
| Replenishment | Expected delivery after order date | PASS |  |
| Replenishment | Daily units_received == sum of orders delivered that day (per medicine/date) | PASS | 11355 receipt days |
| Replenishment | Daily units_ordered_today == orders placed that day | PASS |  |
| Labels | Independent recomputation of stockout_next_7d matches for all 155,210 rows | PASS |  |
| Labels | Label is binary, no nulls | PASS |  |
| Labels | Look-ahead file has 85 x 7 rows covering 2026-01-01..07 | PASS |  |
| Labels | If a stock-out occurs tomorrow, label is 1 (consistency) | PASS |  |
| Labels | Positive-class prevalence in 5%-40% (usable class balance) | PASS | 18.793% |
| Features | sales_7d_avg recomputes from raw sales (no look-ahead) | PASS |  |
| Features | stockout_days_last_30d recomputes (trailing only) | PASS |  |
| Features | Model-table stock/on-order/reorder fields equal inventory table | PASS |  |
| Plausibility | ORS demand peaks in summer/monsoon months (May-Jul) | PASS | peak month=5 |
| Plausibility | Cough syrup demand peaks in Nov-Feb | PASS | peak month=11 |
| Plausibility | Sunday demand lowest weekday | PASS |  |
| Plausibility | Lead times within 1-30 days | PASS | max=22.0 |
| Plausibility | Stock-out rate per medicine between 0% and 50% (heterogeneous, none degenerate) | PASS | min=1.81%, max=13.91% |
| Plausibility | Both label classes present for most medicines (>=90%) | PASS | 85/85 |
| Plausibility | Medicines with zero stock-outs | PASS | 0 medicines |

## Target and stock-out rate by year

| year | rows | stockout_today_rate | label_rate |
|---|---|---|---|
| 2021 | 31025 | 0.0522 | 0.1787 |
| 2022 | 31025 | 0.0581 | 0.1933 |
| 2023 | 31025 | 0.0554 | 0.1823 |
| 2024 | 31110 | 0.0573 | 0.188 |
| 2025 | 31025 | 0.0611 | 0.1973 |

## Target rate by category

| category_id | category | medicines | label_rate |
|---|---|---|---|
| CAT01 | Analgesics & Antipyretics | 8 | 0.1963 |
| CAT02 | Antibiotics | 9 | 0.1886 |
| CAT03 | Cardiovascular | 9 | 0.2183 |
| CAT04 | Antidiabetics | 8 | 0.1397 |
| CAT05 | Gastrointestinal | 8 | 0.2127 |
| CAT06 | Respiratory & Allergy | 8 | 0.1827 |
| CAT07 | Antifungals & Antiparasitics | 7 | 0.1912 |
| CAT08 | Neurology & Psychiatry | 8 | 0.2215 |
| CAT09 | Vitamins & Supplements | 7 | 0.147 |
| CAT10 | Dermatology & Topicals | 6 | 0.1583 |
| CAT11 | Endocrine, Urology & Others | 7 | 0.1959 |

## Order status

| status | orders |
|---|---|
| Received | 10262 |
| Partially_Received | 1093 |
| In_Transit_At_Period_End | 35 |

## Flagged (unverified) medicines

| medicine_id | generic_name | strength | composition_note |
|---|---|---|---|
| MED008 | Paracetamol + Ibuprofen | UNVERIFIED | Fixed-dose combination: strength/ratio varies by market and manufacturer; confirm against product label before use. Indicative only: 325 mg + 400 mg. |
| MED017 | Ofloxacin + Ornidazole | UNVERIFIED | Fixed-dose combination: strength/ratio varies by market and manufacturer; confirm against product label before use. Indicative only: 200 mg + 500 mg. |
| MED026 | Telmisartan + Amlodipine | UNVERIFIED | Fixed-dose combination: strength/ratio varies by market and manufacturer; confirm against product label before use. Indicative only: 40 mg + 5 mg. |
| MED034 | Metformin + Glimepiride | UNVERIFIED | Fixed-dose combination: strength/ratio varies by market and manufacturer; confirm against product label before use. Indicative only: 500 mg + 1 mg. |
| MED042 | Pantoprazole + Domperidone | UNVERIFIED | Fixed-dose combination: strength/ratio varies by market and manufacturer; confirm against product label before use. Indicative only: 40 mg + 30 mg (SR). |
| MED050 | Levocetirizine + Montelukast | UNVERIFIED | Fixed-dose combination: strength/ratio varies by market and manufacturer; confirm against product label before use. Indicative only: 5 mg + 10 mg. |
| MED072 | Multivitamin + Multimineral | UNVERIFIED | Composition is product-specific; no standard formulation exists. |

## Label definition

`stockout_next_7d` = 1 if `lost_sales_units > 0` (demand exceeded available stock) on any of days t+1 ... t+7 for the same medicine. Rows in the final 7 days of 2025 are labelled using a simulated look-ahead (`stockout_label_lookahead_2026.csv`); no row has a missing label. Features use data up to and including day t only.

## Limitations

- All inventory, demand, sales, orders, prices, suppliers and disruptions are **synthetic**; suppliers are fictional. Do not use for real procurement or clinical decisions.
- Composition 'verification' means agreement with standard INN / WHO Model List / pharmacopoeial reference knowledge; **no live regulatory database (CDSCO, DrugBank, RxNorm) lookup was possible** in the offline build environment. A pharmacist should review before production use.
- Fixed-dose combinations and multivitamins are flagged UNVERIFIED_REQUIRES_REVIEW; strengths were deliberately not asserted.
- Demand follows a seasonal x weekday x trend x spike x gamma-Poisson generator; real demand has promotions, prescribing shifts, regional outbreaks and substitution not modelled.
- Replenishment uses a single (s,S)-type rule with daily review; real pharmacies use mixed manual/automatic ordering. Lost sales are not back-ordered and there is no substitution between medicines.
- Stock-out frequency is tuned to give a usable class balance and may differ from real pharmacies. Models trained here will not transfer without re-training on real data.
- `unit_price_inr`/cost are illustrative and not market prices. Expiry is simplified to random wastage; no batch/lot tracking.
- Look-ahead 2026 simulation is not part of the daily tables; orders placed in 2026 are not exported.
- Seasons follow a generic north-India pattern; no public holiday calendar is included.