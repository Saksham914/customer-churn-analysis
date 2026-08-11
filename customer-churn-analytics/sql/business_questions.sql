-- ============================================================
-- Business Questions
-- Target: SQLite database generated from data/processed/customer_churn_clean.csv
-- Table name: customers
--
-- These queries answer the retention questions posed by the business,
-- in priority order.
-- ============================================================

-- Highest-churn segments (by customer value segment)
SELECT
    customer_value_segment,
    COUNT(*) AS customers,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned,
    ROUND(
        100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2
    ) AS churn_rate_pct
FROM customers
GROUP BY customer_value_segment
ORDER BY churn_rate_pct DESC;

-- Highest-revenue segments (total monthly revenue)
SELECT
    customer_value_segment,
    COUNT(*) AS customers,
    ROUND(SUM(MonthlyCharges), 2) AS total_monthly_revenue,
    ROUND(SUM(MonthlyCharges) / COUNT(*), 2) AS avg_monthly_revenue_per_customer
FROM customers
GROUP BY customer_value_segment
ORDER BY total_monthly_revenue DESC;

-- High-charge customers who churned (MonthlyCharges >= 90)
SELECT
    COUNT(*) AS high_charge_churned_customers,
    ROUND(SUM(MonthlyCharges), 2) AS churned_monthly_revenue,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges
FROM customers
WHERE Churn = 'Yes' AND MonthlyCharges >= 90;

-- Month-to-month customers who churned
SELECT
    COUNT(*) AS mtm_churned_customers,
    ROUND(SUM(MonthlyCharges), 2) AS churned_monthly_revenue,
    ROUND(
        100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END)
        / (SELECT COUNT(*) FROM customers WHERE Contract = 'Month-to-month'), 2
    ) AS mtm_churn_rate_pct
FROM customers
WHERE Contract = 'Month-to-month' AND Churn = 'Yes';

-- Month-to-month contract: full churn summary
SELECT
    Contract,
    COUNT(*) AS customers,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned,
    ROUND(
        100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2
    ) AS churn_rate_pct
FROM customers
WHERE Contract = 'Month-to-month'
GROUP BY Contract;

-- High-risk profile: month-to-month + fiber optic + electronic check
SELECT
    COUNT(*) AS customers,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned,
    ROUND(
        100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2
    ) AS churn_rate_pct,
    ROUND(SUM(MonthlyCharges), 2) AS total_monthly_revenue
FROM customers
WHERE Contract = 'Month-to-month'
  AND InternetService = 'Fiber optic'
  AND PaymentMethod = 'Electronic check';

-- Churned customers with no tech support (potential service-gap signal)
SELECT
    COUNT(*) AS customers,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned,
    ROUND(
        100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2
    ) AS churn_rate_pct
FROM customers
WHERE TechSupport = 'No' OR TechSupport = 'No phone service';

-- Average tenure of churned vs retained customers
SELECT
    Churn,
    COUNT(*) AS customers,
    ROUND(AVG(tenure), 2) AS avg_tenure,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges
FROM customers
GROUP BY Churn;
