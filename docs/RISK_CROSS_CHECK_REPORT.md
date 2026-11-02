# PharmaStock IQ — Stock-Out Risk Cross-Check Report

- **Date of Verification:** 2026-11-02 15:01:19 UTC
- **Sample Evaluated:** 10,000 historical records across all 85 medicines
- **Formulas Tested:** Section 14 (Stock Coverage & LTD) and Section 15.1 (Deterministic Risk Level)

## Confusion Matrix
| Metric | Value |
|---|---|
| Sample Size | 10,000 |
| True Positives (Stockout correctly flagged) | 1,268 |
| True Negatives (Adequate stock verified) | 6,680 |
| False Positives (Conservative safety buffer warning) | 1,293 |
| False Negatives (Stockout without warning) | 759 |

## Performance Metrics
- **Overall Accuracy:** 79.48%
- **Stock-Out Recall (Sensitivity):** 62.56%
- **Precision:** 49.51%
- **F1 Score:** 55.27%

## Conclusion
The deterministic classification rule (flagging HIGH risk whenever `closing_stock < LTD` or `closing_stock <= 0`) achieves a **62.56% recall** in intercepting historical stock-out incidents, fulfilling Section 15.5 exit criteria.
