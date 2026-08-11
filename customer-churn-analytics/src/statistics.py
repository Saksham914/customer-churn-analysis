"""Statistical hypothesis testing with SciPy / Statsmodels.

Alpha = 0.05. Statistical significance is reported as evidence of an
ASSOCIATION, never as causation. All tests are run on the actual data.
"""

from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd
from scipy import stats

ALPHA = 0.05
CHURN_COLUMN = "Churn"


def _make_conclusion(p_value: float) -> str:
    if p_value < ALPHA:
        return (
            f"Statistically significant at alpha={ALPHA} "
            "(reject the null hypothesis of no association)."
        )
    return (
        f"Not statistically significant at alpha={ALPHA} "
        "(fail to reject the null hypothesis)."
    )


def chi2_association_test(
    df: pd.DataFrame, group_column: str, churn_column: str = CHURN_COLUMN
) -> Dict[str, Any]:
    """Chi-square test of independence between a categorical variable and churn."""
    contingency = pd.crosstab(df[group_column], df[churn_column])
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
    return {
        "test": "Chi-square test of independence",
        "variable": group_column,
        "vs": churn_column,
        "hypothesis": (
            f"H0: {group_column} and {churn_column} are independent. "
            f"H1: {group_column} and {churn_column} are associated."
        ),
        "contingency_table": contingency,
        "statistic": float(chi2),
        "p_value": float(p_value),
        "degrees_of_freedom": int(dof),
        "expected_min": float(expected.min()),
        "conclusion": _make_conclusion(float(p_value)),
    }


def _normality_test(series: pd.Series) -> Dict[str, Any]:
    """Shapiro-Wilk test of normality (sample capped for stability)."""
    sample = series.dropna()
    if len(sample) > 5000:
        sample = sample.sample(n=5000, random_state=42)
    statistic, p_value = stats.shapiro(sample)
    return {
        "statistic": float(statistic),
        "p_value": float(p_value),
        "normal": p_value >= ALPHA,
    }


def charge_comparison_test(
    df: pd.DataFrame, churn_column: str = CHURN_COLUMN
) -> Dict[str, Any]:
    """Compare MonthlyCharges between churned and retained customers.

    Uses a two-sample t-test when both groups are approximately normal,
    otherwise Mann-Whitney U.
    """
    churned = df.loc[df[churn_column].eq("Yes"), "MonthlyCharges"].dropna()
    retained = df.loc[df[churn_column].eq("No"), "MonthlyCharges"].dropna()
    churned_norm = _normality_test(churned)
    retained_norm = _normality_test(retained)
    use_parametric = churned_norm["normal"] and retained_norm["normal"]

    if use_parametric:
        statistic, p_value = stats.ttest_ind(churned, retained, equal_var=False)
        test_name = "Welch two-sample t-test"
    else:
        statistic, p_value = stats.mannwhitneyu(
            churned, retained, alternative="two-sided"
        )
        test_name = "Mann-Whitney U test"

    return {
        "test": test_name,
        "variable": "MonthlyCharges",
        "vs": churn_column,
        "hypothesis": (
            f"H0: monthly charges distributions do not differ by {churn_column}. "
            f"H1: monthly charges distributions differ by {churn_column}."
        ),
        "churned_normality": churned_norm,
        "retained_normality": retained_norm,
        "churned_mean": float(churned.mean()),
        "retained_mean": float(retained.mean()),
        "churned_median": float(churned.median()),
        "retained_median": float(retained.median()),
        "statistic": float(statistic),
        "p_value": float(p_value),
        "degrees_of_freedom": None,
        "conclusion": _make_conclusion(float(p_value)),
    }


def tenure_comparison_test(
    df: pd.DataFrame, churn_column: str = CHURN_COLUMN
) -> Dict[str, Any]:
    """Compare Tenure between churned and retained customers.

    Tenure is right-skewed and bounded (0-72 months), so the non-parametric
    Mann-Whitney U test is the primary choice; normality is still checked and
    reported for transparency.
    """
    churned = df.loc[df[churn_column].eq("Yes"), "tenure"].dropna()
    retained = df.loc[df[churn_column].eq("No"), "tenure"].dropna()
    churned_norm = _normality_test(churned)
    statistic, p_value = stats.mannwhitneyu(
        churned, retained, alternative="two-sided"
    )
    return {
        "test": "Mann-Whitney U test",
        "variable": "tenure",
        "vs": churn_column,
        "hypothesis": (
            f"H0: tenure distributions do not differ by {churn_column}. "
            f"H1: tenure distributions differ by {churn_column}."
        ),
        "churned_normality": churned_norm,
        "churned_median": float(churned.median()),
        "retained_median": float(retained.median()),
        "churned_mean": float(churned.mean()),
        "retained_mean": float(retained.mean()),
        "statistic": float(statistic),
        "p_value": float(p_value),
        "degrees_of_freedom": None,
        "conclusion": _make_conclusion(float(p_value)),
    }


def run_all_tests(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Run the full battery of hypothesis tests on the dataset."""
    tests: List[Dict[str, Any]] = []
    for column in ["Contract", "InternetService", "PaymentMethod"]:
        if column in df.columns:
            tests.append(chi2_association_test(df, column))
    if "MonthlyCharges" in df.columns:
        tests.append(charge_comparison_test(df))
    if "tenure" in df.columns:
        tests.append(tenure_comparison_test(df))
    return tests


def _dataframe_to_markdown(table: pd.DataFrame) -> str:
    headers = [str(col) for col in table.columns]
    rows = [[str(value) for value in row] for row in table.itertuples(index=False)]
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def tests_to_markdown(tests: List[Dict[str, Any]]) -> str:
    """Render the statistical test results as markdown."""
    lines: List[str] = [
        "# Statistical Analysis",
        "",
        f"Significance level (alpha) = **{ALPHA}**",
        "",
        "Interpretation note: statistical significance indicates an observed "
        "association in this dataset. It does not establish causation.",
        "",
    ]
    for test in tests:
        lines.append(f"## {test['variable']} vs {test['vs']}")
        lines.append("")
        lines.append(f"**Test used:** {test['test']}")
        lines.append("")
        lines.append(f"**Hypothesis:** {test['hypothesis']}")
        lines.append("")
        if "contingency_table" in test:
            lines.append("### Contingency table")
            lines.append("")
            contingency = test["contingency_table"].reset_index()
            lines.append(_dataframe_to_markdown(contingency))
            lines.append("")
            lines.append(
                f"**Chi-square statistic:** {test['statistic']:.4f}  "
                f"**p-value:** {test['p_value']:.4e}  "
                f"**degrees of freedom:** {test['degrees_of_freedom']}"
            )
        else:
            if "churned_normality" in test:
                lines.append(
                    "Normality (Shapiro-Wilk): "
                    f"churned p={test['churned_normality']['p_value']:.4e} "
                    f"(normal={test['churned_normality']['normal']})"
                )
                if "retained_normality" in test:
                    lines[-1] += (
                        f", retained p={test['retained_normality']['p_value']:.4e} "
                        f"(normal={test['retained_normality']['normal']})."
                    )
                lines.append("")
            lines.append(
                f"Churned group: mean={test['churned_mean']:.2f}, "
                f"median={test['churned_median']:.2f}."
            )
            lines.append("")
            lines.append(
                f"Retained group: mean={test['retained_mean']:.2f}, "
                f"median={test['retained_median']:.2f}."
            )
            lines.append("")
            lines.append(
                f"**Statistic:** {test['statistic']:.4f}  "
                f"**p-value:** {test['p_value']:.4e}"
            )
        lines.append("")
        lines.append(f"**Conclusion:** {test['conclusion']}")
        lines.append("")
    return "\n".join(lines)
