# Customer Churn Analytics & Retention Intelligence

## Final Business Insights

This report synthesizes the analytical findings for the telecom customer base. It is an **observational study**: all findings describe associations observed in the historical dataset. **None of the findings are causal claims.**

---

## Executive Summary

- Dataset: 7,043 customers; 1,869 churned (26.5%).
- Overall retention rate: 73.5%.
- Total monthly revenue: $456,117; $139,131 (30.5%) is associated with customers who churned.
- Churned customers carried a higher average monthly charge ($74 vs $61) and a shorter average tenure (18.0 vs 37.6 months).

---

## Major Findings

### Month-to-month customers show the highest observed churn rate

**FINDING** — Month-to-month customers show the highest observed churn rate

**EVIDENCE** — 42.7% of month-to-month customers churned (3,875 customers), versus 11.3% for one-year and 2.8% for two-year contracts.

**BUSINESS IMPLICATION** — This segment represents a large, recurring and largely avoidable retention opportunity given the size of the month-to-month base.

**RECOMMENDATION** — Investigate incentives that encourage movement to longer-term commitments (e.g., multi-month discounts, mid-term upgrades, loyalty credits) and study the drivers behind month-to-month behavior.

### Churn is highest in the earliest tenure window and declines sharply with tenure

**FINDING** — Churn is highest in the earliest tenure window and declines sharply with tenure

**EVIDENCE** — Customers in the 0-6-month group churned at 52.9%, while customers with 61+ months churned at 6.6%.

**BUSINESS IMPLICATION** — Early-tenure attrition suggests the onboarding and first-bill experience are critical touchpoints; retention effort is more effective where the churn probability is highest.

**RECOMMENDATION** — Design an onboarding / first-90-day engagement program and monitor early-tenure cohorts; the observed retention gains at higher tenure support a 'get through the first year' framing.

### Fiber optic customers churned at roughly twice the rate of DSL and non-internet customers

**FINDING** — Fiber optic customers churned at roughly twice the rate of DSL and non-internet customers

**EVIDENCE** — Fiber optic customers churned at 41.9% versus 19.0% (DSL) and 7.4% (no internet service).

**BUSINESS IMPLICATION** — Fiber optic customers are high-value (higher charges) but their churn rate is elevated, indicating a service-quality or expectation-gap risk worth investigating.

**RECOMMENDATION** — Investigate fiber optic service quality, outage and support experience; bundle proactive service checks or compensation mechanisms for this high-value group.

### Electronic check payers churned at the highest rate of any payment method

**FINDING** — Electronic check payers churned at the highest rate of any payment method

**EVIDENCE** — Electronic check payers churned at 45.3%, versus 19.1% (mailed check), 16.7% (bank transfer automatic) and 15.2% (credit card automatic).

**BUSINESS IMPLICATION** — Payment method is strongly associated with churn. Automatic payment customers show materially lower observed churn.

**RECOMMENDATION** — Promote automatic payment enrollment (bank transfer / credit card) with small incentives and investigate friction points for electronic check payers.

### Customers without tech support or online security churned at much higher rates

**FINDING** — Customers without tech support or online security churned at much higher rates

**EVIDENCE** — Customers without tech support churned at 41.6% versus 11.8% for customers with it; customers without online security churned at 41.8% versus 11.5% for those with it.

**BUSINESS IMPLICATION** — Lack of add-on protective/support services is associated with elevated churn, suggesting engagement and perceived-protection gaps.

**RECOMMENDATION** — Test proactive onboarding of online security and tech support offers, especially for new customers on high-value services.

### Churned customers carried, on average, higher monthly charges

**FINDING** — Churned customers carried, on average, higher monthly charges

**EVIDENCE** — Churned customers had a mean monthly charge of $74 versus $61 for retained customers.

**BUSINESS IMPLICATION** — Higher-bill customers appear more likely to churn, possibly due to price sensitivity or value perception at higher spend levels.

**RECOMMENDATION** — Analyze the value-perception of high-bill customers; consider targeted value adds (discounts, bundled perks) rather than blanket price cuts.

### A significant share of monthly recurring revenue is associated with customers who churned

**FINDING** — A significant share of monthly recurring revenue is associated with customers who churned

**EVIDENCE** — $139,131 of $456,117 total monthly revenue (30.5%) is associated with customers observed to churn.

**BUSINESS IMPLICATION** — This is a direct measure of the revenue surface exposed to churn risk and frames the commercial value of retention.

**RECOMMENDATION** — Prioritize retention spend by balancing churn probability against customer revenue, rather than by churn probability alone.

### Senior citizens show a higher observed churn rate

**FINDING** — Senior citizens show a higher observed churn rate

**EVIDENCE** — Senior citizens churned at 41.7% versus 23.6% for non-seniors.

**BUSINESS IMPLICATION** — Age-segmented needs (support style, usability, communication channels) may not be fully met for this group.

**RECOMMENDATION** — Explore segment-specific support and communication approaches for senior customers and measure their response.

### New + High Value customers churn most; Loyal + High Value customers anchor the revenue base

**FINDING** — New + High Value customers churn most; Loyal + High Value customers anchor the revenue base

**EVIDENCE** — The New + High Value segment shows the highest observed churn rate (64.0%). The Loyal + Low Value segment shows the lowest (4.9%). The Loyal + High Value segment contributes $184,598 in monthly revenue.

**BUSINESS IMPLICATION** — The two-sided nature of the customer base (high-churn early/high-value vs stable late/high-value) requires different retention strategies per segment.

**RECOMMENDATION** — Treat 'New + High Value' as the priority early-intervention segment and design loyalty programs that protect the 'Loyal + High Value' revenue base.

## Statistical Analysis Summary

All tests use alpha = 0.05. Statistical significance indicates an observed association in this dataset and does not imply causation.

- **Contract vs churn** (Chi-square test of independence): statistic = 1184.60, p-value = 5.86e-258, df = 2. Statistically significant at alpha=0.
- **InternetService vs churn** (Chi-square test of independence): statistic = 732.31, p-value = 9.57e-160, df = 2. Statistically significant at alpha=0.
- **PaymentMethod vs churn** (Chi-square test of independence): statistic = 648.14, p-value = 3.68e-140, df = 3. Statistically significant at alpha=0.
- **MonthlyCharges vs churn** (Mann-Whitney U test): statistic = 6003125.50, p-value = 3.31e-54. Statistically significant at alpha=0.
- **tenure vs churn** (Mann-Whitney U test): statistic = 2515538.00, p-value = 2.42e-208. Statistically significant at alpha=0.

---

## Priority Recommendations (observations separated from actions)

The recommendations below follow directly from the observed findings. They are business actions to test, not guaranteed outcomes.

1. **Target early-tenure attrition** — the 0-6 month group shows the highest churn; build an onboarding/engagement program and monitor cohort-level churn monthly.
2. **Shift month-to-month customers to longer commitments** — the largest churned segment; test retention offers at renewal and compare take-rates.
3. **Enroll electronic check payers in automatic payments** — automatic payment methods show materially lower observed churn.
4. **Investigate fiber optic service experience** — high churn on a high-value service points to a service-quality risk.
5. **Reduce support/security service gaps** — customers without tech support and online security churn at higher rates; test proactive offers.
6. **Prioritize high-value early customers** — the New + High Value segment combines elevated churn with elevated revenue.
7. **Protect the revenue base** — loyalty/engagement programming for Loyal + High Value customers, who contribute the largest monthly revenue.

## Limitations

- Observational data: associations, not causal effects.
- The dataset is a historical snapshot; no timing of events is available, so lead/lag effects cannot be established.
- 11 customers have zero recorded TotalCharges (tenure 0); they were retained with TotalCharges set to 0 after verification that their tenure was 0.
- Thresholds for tenure groups, charge groups and value segments are documented analytical choices; different thresholds may change segmentation results.
- Revenue figures represent monthly charges associated with churned customers, not forecast future losses.

---

## Generated Artifacts

- Data quality report: `reports/data_quality_report.md`
- Charts: `reports/figures/` (static PNG + interactive HTML)
- SQL database: `data/processed/customer_churn.db`
- SQL query results: `reports/analysis_results/sql_query_results.md`
- Statistical tests: `reports/analysis_results/statistical_tests.md`
