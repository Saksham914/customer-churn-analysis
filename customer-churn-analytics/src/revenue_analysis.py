"""Revenue analysis associated with observed churn.

IMPORTANT framing: these figures describe revenue associated with customers
who were observed to churn in the historical window. They are NOT forecasts
of guaranteed future losses. All values are computed from the dataset.
"""

from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd

CHURN_COLUMN = "Churn"


def revenue_overview(df: pd.DataFrame) -> Dict[str, Any]:
    """Total monthly revenue, split by churn status.

    Monthly revenue is the sum of MonthlyCharges (what the company bills per
    month). We report the share of recurring monthly revenue associated with
    customers who churned.
    """
    total = float(df["MonthlyCharges"].sum())
    churned_mask = df[CHURN_COLUMN].eq("Yes")
    churned_revenue = float(df.loc[churned_mask, "MonthlyCharges"].sum())
    retained_revenue = float(df.loc[~churned_mask, "MonthlyCharges"].sum())
    return {
        "total_monthly_revenue": total,
        "monthly_revenue_churned": churned_revenue,
        "monthly_revenue_retained": retained_revenue,
        "churned_share_of_monthly_revenue": churned_revenue / total if total else 0.0,
        "churned_customers": int(churned_mask.sum()),
        "total_customers": int(len(df)),
    }


def average_charges_by_churn(df: pd.DataFrame) -> pd.DataFrame:
    """Mean and median monthly charges by churn status."""
    table = (
        df.groupby(CHURN_COLUMN, observed=True)["MonthlyCharges"]
        .agg(["count", "mean", "median", "std"])
        .reset_index()
    )
    return table


def total_charges_by_churn(df: pd.DataFrame) -> pd.DataFrame:
    """Sum of lifetime TotalCharges by churn status."""
    table = (
        df.groupby(CHURN_COLUMN, observed=True)["TotalCharges"]
        .agg(["count", "sum", "mean", "median"])
        .reset_index()
    )
    return table


def revenue_by_group(df: pd.DataFrame, group_column: str) -> pd.DataFrame:
    """Monthly revenue split by churn status for each category of a group.

    Columns returned:
        group, customers, total_monthly_revenue, churned_revenue,
        retained_revenue, churned_revenue_share, churn_rate
    """
    records: List[Dict[str, Any]] = []
    for group_value, subset in df.groupby(group_column, observed=True):
        churned_mask = subset[CHURN_COLUMN].eq("Yes")
        total = float(subset["MonthlyCharges"].sum())
        churned_rev = float(subset.loc[churned_mask, "MonthlyCharges"].sum())
        records.append(
            {
                group_column: group_value,
                "customers": len(subset),
                "churned_customers": int(churned_mask.sum()),
                "total_monthly_revenue": total,
                "churned_revenue": churned_rev,
                "retained_revenue": total - churned_rev,
                "churned_revenue_share": churned_rev / total if total else 0.0,
                "churn_rate": churned_mask.mean(),
            }
        )
    table = pd.DataFrame(records).sort_values(
        "churned_revenue", ascending=False
    ).reset_index(drop=True)
    return table


def revenue_analysis_dimensions(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Run revenue-by-group for the documented analysis dimensions."""
    dimensions = [
        "Contract",
        "InternetService",
        "tenure_group",
        "PaymentMethod",
        "customer_value_segment",
    ]
    results: Dict[str, pd.DataFrame] = {}
    for dimension in dimensions:
        if dimension in df.columns:
            results[dimension] = revenue_by_group(df, dimension)
    return results
