-- ============================================================
-- Revenue Analysis Queries
-- Target: SQLite database generated from data/processed/customer_churn_clean.csv
-- Table name: customers
--
-- NOTE: "Revenue associated with churned customers" means monthly
-- charges billed to customers who were observed to churn in the
-- historical window. It is not a forecast of future losses.
-- ============================================================

-- Average and median monthly charges by churn status
SELECT
    Churn,
    COUNT(*) AS customers,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges,
    ROUND(AVG(TotalCharges), 2) AS avg_total_charges,
    ROUND(SUM(TotalCharges), 2) AS sum_total_charges
FROM customers
GROUP BY Churn;

-- Total monthly revenue split by churn status
SELECT
    Churn,
    COUNT(*) AS customers,
    ROUND(SUM(MonthlyCharges), 2) AS total_monthly_revenue,
    ROUND(
        100.0 * SUM(MonthlyCharges) / (SELECT SUM(MonthlyCharges) FROM customers), 2
    ) AS revenue_share_pct
FROM customers
GROUP BY Churn;

-- Revenue associated with churn, by contract
SELECT
    Contract,
    COUNT(*) AS customers,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(SUM(MonthlyCharges), 2) AS total_monthly_revenue,
    ROUND(
        SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0 END), 2
    ) AS churned_monthly_revenue,
    ROUND(
        100.0 * SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0 END)
        / SUM(MonthlyCharges), 2
    ) AS churned_revenue_share_pct
FROM customers
GROUP BY Contract
ORDER BY churned_monthly_revenue DESC;

-- Revenue associated with churn, by internet service
SELECT
    InternetService,
    COUNT(*) AS customers,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(SUM(MonthlyCharges), 2) AS total_monthly_revenue,
    ROUND(
        SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0 END), 2
    ) AS churned_monthly_revenue,
    ROUND(
        100.0 * SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0 END)
        / SUM(MonthlyCharges), 2
    ) AS churned_revenue_share_pct
FROM customers
GROUP BY InternetService
ORDER BY churned_monthly_revenue DESC;

-- Revenue by customer value segment
SELECT
    customer_value_segment,
    COUNT(*) AS customers,
    ROUND(SUM(MonthlyCharges), 2) AS total_monthly_revenue,
    ROUND(
        SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0 END), 2
    ) AS churned_monthly_revenue,
    ROUND(
        100.0 * SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0 END)
        / SUM(MonthlyCharges), 2
    ) AS churned_revenue_share_pct
FROM customers
GROUP BY customer_value_segment
ORDER BY total_monthly_revenue DESC;

-- Revenue by tenure group
SELECT
    tenure_group,
    COUNT(*) AS customers,
    ROUND(SUM(MonthlyCharges), 2) AS total_monthly_revenue,
    ROUND(
        SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0 END), 2
    ) AS churned_monthly_revenue,
    ROUND(
        100.0 * SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0 END)
        / SUM(MonthlyCharges), 2
    ) AS churned_revenue_share_pct
FROM customers
GROUP BY tenure_group
ORDER BY MIN(tenure);

-- Revenue by payment method
SELECT
    PaymentMethod,
    COUNT(*) AS customers,
    ROUND(SUM(MonthlyCharges), 2) AS total_monthly_revenue,
    ROUND(
        SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0 END), 2
    ) AS churned_monthly_revenue,
    ROUND(
        100.0 * SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0 END)
        / SUM(MonthlyCharges), 2
    ) AS churned_revenue_share_pct
FROM customers
GROUP BY PaymentMethod
ORDER BY churned_monthly_revenue DESC;
