# Data Quality Report

Dataset: IBM Telco Customer Churn (raw file)

Shape before cleaning: **7043** rows x **21** columns
Shape after cleaning: **7043** rows x **21** columns

## Missing / blank values

| Column | Blank/missing count |
| --- | --- |
| TotalCharges | 11 |

## Customer ID integrity

| Check | Result |
| --- | --- |
| Missing customer IDs | 0 |
| Duplicated customer IDs | 0 |
| Malformed customer IDs | -1 |
| Unique customers | 7043 |

Fully duplicated rows (ignoring customerID): **22**

## Data-type validation

| Column | Status |
| --- | --- |
| tenure | ok |
| MonthlyCharges | ok |
| TotalCharges | ok |
| gender | ok |
| SeniorCitizen | ok |
| Partner | ok |
| Dependents | ok |
| PhoneService | ok |
| MultipleLines | ok |
| InternetService | ok |
| OnlineSecurity | ok |
| OnlineBackup | ok |
| DeviceProtection | ok |
| TechSupport | ok |
| StreamingTV | ok |
| StreamingMovies | ok |
| Contract | ok |
| PaperlessBilling | ok |
| PaymentMethod | ok |
| Churn | ok |

## Outlier investigation (reported, not removed)

| Column | Count | Min | Max | Mean | IQR outliers | z>3 outliers |
| --- | --- | --- | --- | --- | --- | --- |
| tenure | 7043 | 0.00 | 72.00 | 32.37 | 0 | 0 |
| MonthlyCharges | 7043 | 18.25 | 118.75 | 64.76 | 0 | 0 |
| TotalCharges | 7043 | 0.00 | 8684.80 | 2279.73 | 0 | 0 |

## Categorical value inspection

### gender

| Value | Count |
| --- | --- |
| Male | 3555 |
| Female | 3488 |

### SeniorCitizen

| Value | Count |
| --- | --- |
| No | 5901 |
| Yes | 1142 |

### Partner

| Value | Count |
| --- | --- |
| No | 3641 |
| Yes | 3402 |

### Dependents

| Value | Count |
| --- | --- |
| No | 4933 |
| Yes | 2110 |

### PhoneService

| Value | Count |
| --- | --- |
| Yes | 6361 |
| No | 682 |

### MultipleLines

| Value | Count |
| --- | --- |
| No | 3390 |
| Yes | 2971 |
| No phone service | 682 |

### InternetService

| Value | Count |
| --- | --- |
| Fiber optic | 3096 |
| DSL | 2421 |
| No | 1526 |

### OnlineSecurity

| Value | Count |
| --- | --- |
| No | 3498 |
| Yes | 2019 |
| No internet service | 1526 |

### OnlineBackup

| Value | Count |
| --- | --- |
| No | 3088 |
| Yes | 2429 |
| No internet service | 1526 |

### DeviceProtection

| Value | Count |
| --- | --- |
| No | 3095 |
| Yes | 2422 |
| No internet service | 1526 |

### TechSupport

| Value | Count |
| --- | --- |
| No | 3473 |
| Yes | 2044 |
| No internet service | 1526 |

### StreamingTV

| Value | Count |
| --- | --- |
| No | 2810 |
| Yes | 2707 |
| No internet service | 1526 |

### StreamingMovies

| Value | Count |
| --- | --- |
| No | 2785 |
| Yes | 2732 |
| No internet service | 1526 |

### Contract

| Value | Count |
| --- | --- |
| Month-to-month | 3875 |
| Two year | 1695 |
| One year | 1473 |

### PaperlessBilling

| Value | Count |
| --- | --- |
| Yes | 4171 |
| No | 2872 |

### PaymentMethod

| Value | Count |
| --- | --- |
| Electronic check | 2365 |
| Mailed check | 1612 |
| Bank transfer (automatic) | 1544 |
| Credit card (automatic) | 1522 |

### Churn

| Value | Count |
| --- | --- |
| No | 5174 |
| Yes | 1869 |

## Cleaning notes

- TotalCharges contained whitespace-only entries; all mapped rows had tenure == 0 and were filled with 0.0 (no full month billed).
- Outliers are investigated and reported but deliberately not removed (observational study).
- SeniorCitizen was relabelled from 0/1 to No/Yes for readability.
- No rows were dropped during cleaning.