"""Churn-rate analysis across categorical customer dimensions.

Every calculation is computed from the actual dataset at runtime; nothing is
hardcoded. The module reports observed churn/retention rates and explicitly
avoids any causal language: we describe associations only.
"""

from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd

CHURN_COLUMN = "Churn"

DIMENSIONS = [
    "gender",
    "SeniorCitizen",
    "Partner",
    "Dependents",
    "tenure_group",
    "Contract",
    "InternetService",
    "PaymentMethod",
    "PaperlessBilling",
    "TechSupport",
    "OnlineSecurity",
    "DeviceProtection",
    "monthly_charge_group",
    "customer_value_segment",
]


def overall_churn(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute overall churn and retention rates."""
    total = int(len(df))
    churned = int(df[CHURN_COLUMN].eq("Yes").sum())
    retained = int(df[CHURN_COLUMN].eq("No").sum())
    churn_rate = churned / total if total else 0.0
    retention_rate = retained / total if total else 0.0
    return {
        "total_customers": total,
        "churned_customers": churned,
        "retained_customers": retained,
        "churn_rate": churn_rate,
        "retention_rate": retention_rate,
    }


def churn_by_group(df: pd.DataFrame, group_column: str) -> pd.DataFrame:
    """Compute count / churned / retained / churn rate / retention rate
    for every category of `group_column`."""
    summary = (
        df.groupby(group_column, observed=True)
        .apply(
            lambda g: pd.Series(
                {
                    "customers": len(g),
                    "churned": int(g[CHURN_COLUMN].eq("Yes").sum()),
                    "retained": int(g[CHURN_COLUMN].eq("No").sum()),
                }
            ),
            include_groups=False,
        )
        .reset_index()
    )
    summary["churn_rate"] = summary["churned"] / summary["customers"]
    summary["retention_rate"] = summary["retained"] / summary["customers"]
    summary = summary.sort_values("customers", ascending=False).reset_index(drop=True)
    return summary


def analyze_all_dimensions(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Run churn-by-group for every documented analysis dimension."""
    results: Dict[str, pd.DataFrame] = {}
    for dimension in DIMENSIONS:
        if dimension in df.columns:
            results[dimension] = churn_by_group(df, dimension)
    return results


def _dataframe_to_markdown(table: pd.DataFrame) -> str:
    """Render a DataFrame as a markdown table without external deps."""
    headers = [str(col) for col in table.columns]
    rows = [[str(value) for value in row] for row in table.itertuples(index=False)]
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def dimension_summary_markdown(summaries: Dict[str, pd.DataFrame]) -> str:
    """Render all churn-by-group tables as markdown."""
    lines: List[str] = ["# Churn Analysis by Dimension", ""]
    for dimension, table in summaries.items():
        lines.append(f"## {dimension}")
        lines.append("")
        display = table.copy()
        display["churn_rate"] = (display["churn_rate"] * 100).round(2).astype(str) + "%"
        display["retention_rate"] = (
            display["retention_rate"] * 100
        ).round(2).astype(str) + "%"
        lines.append(_dataframe_to_markdown(display))
        lines.append("")
    return "\n".join(lines)
