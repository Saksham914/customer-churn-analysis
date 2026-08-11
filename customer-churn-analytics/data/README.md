# Data Directory

## Raw dataset

**`raw/WA_Fn-UseC_-Telco-Customer-Churn.csv`**

Source: IBM Telco Customer Churn dataset (public, IBM developer sample data).

This file contains the historical telecom customer records used for the
analysis: 7,043 customers x 21 columns.

If you need to re-download it, the canonical source is:

```
https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv
```

Place the file in `data/raw/` with the name:
`WA_Fn-UseC_-Telco-Customer-Churn.csv`

### Column reference

| Column | Description |
|--------|-------------|
| customerID | Unique customer identifier |
| gender | Customer gender (Female/Male) |
| SeniorCitizen | Whether the customer is a senior citizen |
| Partner | Whether the customer has a partner |
| Dependents | Whether the customer has dependents |
| tenure | Months the customer has been with the company (0-72) |
| PhoneService | Whether the customer has phone service |
| MultipleLines | Multiple lines status |
| InternetService | Internet service type (DSL/Fiber optic/No) |
| OnlineSecurity | Online security add-on subscription |
| OnlineBackup | Online backup add-on subscription |
| DeviceProtection | Device protection add-on subscription |
| TechSupport | Tech support add-on subscription |
| StreamingTV | Streaming TV add-on subscription |
| StreamingMovies | Streaming movies add-on subscription |
| Contract | Contract type (Month-to-month/One year/Two year) |
| PaperlessBilling | Whether billing is paperless |
| PaymentMethod | Payment method used |
| MonthlyCharges | Monthly recurring charges (USD) |
| TotalCharges | Lifetime charges (USD) |
| Churn | Whether the customer churned (Yes/No) |

## Processed data

**`processed/customer_churn_clean.csv`** — cleaned dataset produced by the
pipeline (`python run_analysis.py`). It is identical in row count to the raw
file; only values were normalized (numeric `TotalCharges`, readable
`SeniorCitizen`, blank `TotalCharges` filled for tenure-0 customers).

**`processed/customer_churn.db`** — SQLite database created from the cleaned
dataset with a single `customers` table. Used by the SQL analysis scripts.
