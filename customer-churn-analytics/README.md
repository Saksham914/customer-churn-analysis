# Customer Churn Analytics & Retention Intelligence

A portfolio-quality, purely observational data analysis project that quantifies
customer churn and its association with demographics, contracts, tenure,
services, payment methods and charges in a telecom customer base — and turns
those observations into evidence-based retention recommendations.

> **This is a data science / analytics project.** It deliberately uses **no
> machine learning, no predictive modeling, and no causal claims**. Every
> number in this repository is computed from the actual dataset at runtime.

---

## Business Problem

A telecom provider wants to understand **who churns and why the revenue exposed
to churn is large**. The goal is not to predict churn but to:

- Measure the overall churn and retention rates.
- Profile churned customers across demographic, contract, tenure, service and
  payment dimensions.
- Quantify the monthly revenue associated with customers who churned.
- Identify high-risk / high-value customer segments.
- Test which relationships are statistically significant.
- Turn findings into prioritized retention actions.

## Dataset

**IBM Telco Customer Churn** (public IBM sample data) — 7,043 customers x 21
columns. It contains demographic, service, account and billing attributes per
customer, with a binary `Churn` flag.

| Attribute group | Columns |
|---|---|
| Demographics | `gender`, `SeniorCitizen`, `Partner`, `Dependents` |
| Tenure | `tenure` (0-72 months) |
| Services | `PhoneService`, `MultipleLines`, `InternetService`, `OnlineSecurity`, `OnlineBackup`, `DeviceProtection`, `TechSupport`, `StreamingTV`, `StreamingMovies` |
| Account | `Contract`, `PaperlessBilling`, `PaymentMethod`, `MonthlyCharges`, `TotalCharges` |
| Target | `Churn` |

## Objectives

1. Clean and validate the dataset, documenting all quality issues.
2. Compute overall churn and retention rates.
3. Profile churn by demographics, contract, tenure, services, payment method,
   charges and value segments.
4. Quantify revenue associated with churned customers.
5. Build a business segmentation (New/Established/Loyal x Low/High value).
6. Run statistical hypothesis tests (alpha = 0.05).
7. Answer business questions with SQL against a SQLite database.
8. Produce charts and a final business-insights report.

## Tech Stack

Python 3.11+ · Pandas · NumPy · SciPy · Statsmodels · Matplotlib · Seaborn ·
Plotly · SQLite · Jupyter · Pytest

## Project Structure

```
customer-churn-analytics/
├── data/
│   ├── raw/                      # IBM Telco Churn CSV
│   ├── processed/                # cleaned CSV + SQLite database
│   └── README.md
├── notebooks/
│   ├── 01_data_cleaning.ipynb
│   ├── 02_eda.ipynb
│   ├── 03_churn_analysis.ipynb
│   ├── 04_segmentation.ipynb
│   └── 05_statistics.ipynb
├── src/
│   ├── data_cleaning.py          # cleaning + data-quality reporting
│   ├── segmentation.py           # analytical features + value segments
│   ├── churn_analysis.py         # churn/retention rate computations
│   ├── revenue_analysis.py       # revenue associated with churn
│   ├── statistics.py             # hypothesis tests
│   ├── visualization.py          # matplotlib/seaborn + plotly charts
│   └── insights.py               # final business insights report
├── sql/
│   ├── churn_analysis.sql
│   ├── revenue_analysis.sql
│   └── business_questions.sql
├── reports/
│   ├── figures/                  # all generated charts
│   ├── analysis_results/         # CSV/JSON/markdown results
│   ├── data_quality_report.md
│   └── final_business_insights.md
├── tests/
│   └── test_analysis.py          # 25 pytest tests
├── run_analysis.py               # end-to-end pipeline
├── requirements.txt
├── README.md
└── .gitignore
```

## Data Cleaning

- Stripped whitespace from all text columns.
- **`TotalCharges`** contained 11 whitespace-only values. These all belonged to
  tenure-0 customers, so they were converted to numeric and filled with `0.0`
  (no full month billed) — verified, not guessed.
- Relabelled `SeniorCitizen` from 0/1 to No/Yes.
- No missing values, no duplicate `customerID`s, no duplicated rows.
- Outliers on `tenure` / `MonthlyCharges` / `TotalCharges` were investigated
  and **reported but not removed** (observational study).

Results are in `reports/data_quality_report.md` and
`reports/analysis_results/data_quality_summary.json`.

## Analytical Features

- **`tenure_group`** — 0-6, 7-12, 13-24, 25-36, 37-48, 49-60, 61+ months.
- **`monthly_charge_group`** — Low (< $40), Medium ($40-$90), High (>= $90).
- **`total_services`** — count of subscribed services (0-9).
- **`customer_value_segment`** — New (<= 12 mo) / Established (13-36) /
  Loyal (> 36) x Low (< $60/mo) / High value.

All thresholds are documented analytical decisions, not model outputs.

## EDA

Key distributions:

- **Tenure** is right-skewed with a large cluster of new customers
  (median 29 months).
- **Monthly charges** span $18-$119 with a bimodal shape (phone-only vs.
  fiber bundles).
- **Churn balance**: 26.5% churned / 73.5% retained.

## Churn Analysis

Overall churn and retention rates:

| Metric | Value |
|---|---|
| Total customers | 7,043 |
| Churned | 1,869 |
| Retained | 5,174 |
| **Churn rate** | **26.5%** |
| **Retention rate** | **73.5%** |

![Overall churn](reports/figures/01_overall_churn.png)

### Churn by dimension (actual results)

| Dimension | Highest-churn category | Churn rate |
|---|---|---|
| Contract | Month-to-month | **42.7%** (vs 11.3% one-year, 2.8% two-year) |
| Tenure | 0-6 months | **52.9%** (vs 6.6% at 61+ months) |
| Internet service | Fiber optic | **41.9%** (vs 19.0% DSL, 7.4% no internet) |
| Payment method | Electronic check | **45.3%** (vs 15.2% credit card auto) |
| Senior citizen | Senior citizens | **41.7%** (vs 23.6% non-seniors) |
| Tech support | Not subscribed | **41.6%** (vs 11.8% subscribed) |
| Online security | Not subscribed | **41.8%** (vs 11.5% subscribed) |
| Value segment | New + High Value | **64.0%** |

![Churn by contract](reports/figures/02_churn_by_contract.png)
![Churn by tenure](reports/figures/03_churn_by_tenure.png)
![Churn by internet service](reports/figures/04_churn_by_internet.png)
![Churn by payment method](reports/figures/05_churn_by_payment.png)

## Revenue Analysis

Revenue figures are the **monthly charges associated with customers who were
observed to churn** — an exposure measure, not a forecast of future losses.

| Metric | Value |
|---|---|
| Total monthly revenue | **$456,117** |
| Revenue of churned customers | **$139,131** (30.5% of monthly revenue) |
| Revenue of retained customers | $316,986 |
| Avg monthly charge (churned) | $74.44 |
| Avg monthly charge (retained) | $61.27 |
| Avg tenure (churned) | 18.0 months |
| Avg tenure (retained) | 37.6 months |

![Revenue associated with churn](reports/figures/10_revenue_associated_with_churn.png)
![Revenue by segment](reports/figures/14_revenue_by_segment.png)

## Segmentation

Six business segments (tenure tier x value tier), computed with deterministic
rules:

| Segment | Customers | Churn rate | Monthly revenue |
|---|---|---|---|
| New + Low Value | 1,133 | 32.0% | $38,014 |
| **New + High Value** | **1,053** | **64.0%** | **$84,616** |
| Established + Low Value | 795 | 9.8% | $26,961 |
| Established + High Value | 1,061 | 37.3% | $90,427 |
| Loyal + Low Value | 979 | 4.9% | $31,500 |
| **Loyal + High Value** | **2,022** | **15.3%** | **$184,598** |

- **New + High Value** is the priority early-intervention segment: highest
  churn (64.0%) while carrying meaningful revenue.
- **Loyal + High Value** is the revenue anchor: 2,022 customers contributing
  $184.6k/mo (≈40% of total monthly revenue) at a 15.3% churn rate.

![Customer segmentation](reports/figures/11_customer_segmentation_churn.png)
![Churn heatmap](reports/figures/12_churn_heatmap.png)
![Retention by tenure](reports/figures/13_retention_by_tenure.png)

## Statistical Analysis

Alpha = 0.05. Significance indicates an **association** in this dataset, never
causation.

| Test | Statistic | df | p-value | Conclusion |
|---|---|---|---|---|
| Chi-square: Contract vs Churn | 1184.60 | 2 | 5.86e-258 | Significant |
| Chi-square: InternetService vs Churn | 732.31 | 2 | 9.57e-160 | Significant |
| Chi-square: PaymentMethod vs Churn | 648.14 | 3 | 3.68e-140 | Significant |
| Mann-Whitney U: MonthlyCharges vs Churn | 6,003,125.5 | — | 3.31e-54 | Significant |
| Mann-Whitney U: Tenure vs Churn | 2,515,538.0 | — | 2.42e-208 | Significant |

Full details (hypotheses, contingency tables, normality checks) are in
`reports/analysis_results/statistical_tests.md`.

## SQL Analysis

The pipeline loads the cleaned data into a SQLite database
(`data/processed/customer_churn.db`) and runs 20 named queries across three
files:

- `sql/churn_analysis.sql` — totals, churn rate, churn by contract / internet /
  payment / tenure / segment.
- `sql/revenue_analysis.sql` — charges by churn status, revenue by contract /
  internet / segment / tenure / payment.
- `sql/business_questions.sql` — highest-churn & highest-revenue segments,
  high-charge churned customers, month-to-month churned customers, high-risk
  profile (month-to-month + fiber optic + electronic check), service-gap
  churn, tenure averages.

All query results are written to
`reports/analysis_results/sql_query_results.md`.

## Key Findings

1. **Contract:** 42.7% of month-to-month customers churned — the single
   strongest observed churn signal.
2. **Tenure:** churn peaks in the first 6 months (52.9%) and drops to 6.6%
   for 61+ month customers.
3. **Internet:** fiber optic customers churned at 41.9%, roughly twice DSL
   (19.0%).
4. **Payment:** electronic check payers churned at 45.3%; automatic payment
   methods were below 17%.
5. **Support/security gaps:** no tech support (41.6%) and no online security
   (41.8%) are associated with much higher churn.
6. **Charges:** churned customers averaged $74.44/month vs $61.27 for retained.
7. **Revenue exposure:** 30.5% of monthly recurring revenue ($139k) is
   associated with customers who churned.
8. **Segments:** New + High Value churns most (64.0%); Loyal + High Value
   anchors revenue ($184.6k/mo at 15.3% churn).

## Business Recommendations

1. **Target early-tenure attrition** — build an onboarding / first-90-day
   engagement program for the 0-6 month cohort (52.9% churn).
2. **Shift month-to-month customers to longer commitments** — test retention
   offers at renewal; this is the largest churning segment.
3. **Enroll electronic check payers in automatic payments** — automatic
   methods show materially lower observed churn.
4. **Investigate fiber optic service experience** — high churn on a
   high-value service.
5. **Close support/security gaps** — test proactive offers of tech support and
   online security.
6. **Prioritize New + High Value** — combines the highest churn rate with
   meaningful revenue.
7. **Protect the revenue base** — loyalty programming for Loyal + High Value
   customers.

## Limitations

- Observational study: associations, not causal effects.
- Historical snapshot: no event timing, so lead/lag effects are unknown.
- Documented segmentation thresholds; different thresholds change results.
- Revenue figures measure revenue associated with churned customers, not
  forecast losses.
- 11 tenure-0 customers have `TotalCharges = 0` by construction.

## Future Improvements

- Add longitudinal / event-time data to study churn timing.
- Track cohort churn over time instead of a single snapshot.
- Add cost data to estimate the ROI of specific retention programs.
- Broaden the analysis to price-sensitivity and satisfaction survey data.
- Use SQL window functions for rolling cohort retention metrics.

## Installation

```bash
# Python 3.11+ recommended
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## How to Run

Place the raw dataset at `data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv`
(see `data/README.md`).

Run the full pipeline (cleaning -> EDA -> churn -> revenue -> segmentation ->
statistics -> SQL -> charts -> reports):

```bash
python run_analysis.py
```

Run the automated test suite:

```bash
pytest tests/
```

Explore the notebooks:

```bash
jupyter notebook notebooks/
```

## Generated Artifacts

- `reports/data_quality_report.md` — data-quality assessment
- `reports/final_business_insights.md` — findings + recommendations
- `reports/analysis_results/` — CSV/JSON/markdown results for every analysis
- `reports/figures/` — 16 static PNG charts + 4 interactive Plotly HTML charts
- `data/processed/customer_churn_clean.csv` — cleaned dataset
- `data/processed/customer_churn.db` — SQLite database for SQL analysis
