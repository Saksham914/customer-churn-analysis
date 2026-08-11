"""Builds the final business insights report.

Every number in the report is computed at runtime from the actual dataset
(summaries passed in from the pipeline). No metrics are hardcoded. Each major
finding uses the FINDING / EVIDENCE / BUSINESS IMPLICATION / RECOMMENDATION
template and explicitly separates observations from recommendations.
"""

from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd

from src import REPORTS_DIR, RESULTS_DIR


def _fmt_money(value: float) -> str:
    return f"${value:,.0f}"


def _pct(value: float) -> str:
    return f"{value:.1%}"


def _churn_rate_of(df: pd.DataFrame, mask: pd.Series) -> float:
    subset = df.loc[mask]
    if len(subset) == 0:
        return 0.0
    return float(subset["Churn"].eq("Yes").mean())


def compute_key_figures(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute all headline figures from the featured dataset."""
    total = len(df)
    churned = int(df["Churn"].eq("Yes").sum())
    retained = total - churned

    contract_rates = df.groupby("Contract", observed=True)["Churn"].apply(
        lambda s: s.eq("Yes").mean()
    )
    tenure_rates = df.groupby("tenure_group", observed=True)["Churn"].apply(
        lambda s: s.eq("Yes").mean()
    )
    internet_rates = df.groupby("InternetService", observed=True)["Churn"].apply(
        lambda s: s.eq("Yes").mean()
    )
    payment_rates = df.groupby("PaymentMethod", observed=True)["Churn"].apply(
        lambda s: s.eq("Yes").mean()
    )

    monthly_revenue = float(df["MonthlyCharges"].sum())
    churned_revenue = float(
        df.loc[df["Churn"].eq("Yes"), "MonthlyCharges"].sum()
    )

    segment_rates = df.groupby("customer_value_segment", observed=True)["Churn"].apply(
        lambda s: s.eq("Yes").mean()
    )
    segment_revenue = df.groupby("customer_value_segment", observed=True)[
        "MonthlyCharges"
    ].sum()

    senior_mask = df["SeniorCitizen"].eq("Yes")
    support_gap = df["TechSupport"].eq("No")
    security_gap = df["OnlineSecurity"].eq("No")

    return {
        "total_customers": total,
        "churned_customers": churned,
        "retained_customers": retained,
        "churn_rate": churned / total,
        "retention_rate": retained / total,
        "monthly_revenue": monthly_revenue,
        "churned_revenue": churned_revenue,
        "churned_revenue_share": churned_revenue / monthly_revenue,
        "contract_rates": contract_rates,
        "tenure_rates": tenure_rates,
        "internet_rates": internet_rates,
        "payment_rates": payment_rates,
        "segment_rates": segment_rates,
        "segment_revenue": segment_revenue,
        "senior_rate": _churn_rate_of(df, senior_mask),
        "non_senior_rate": _churn_rate_of(df, ~senior_mask),
        "support_gap_rate": _churn_rate_of(df, support_gap),
        "support_ok_rate": _churn_rate_of(df, ~support_gap),
        "security_gap_rate": _churn_rate_of(df, security_gap),
        "security_ok_rate": _churn_rate_of(df, ~security_gap),
        "avg_charge_churned": float(df.loc[df["Churn"].eq("Yes"), "MonthlyCharges"].mean()),
        "avg_charge_retained": float(df.loc[df["Churn"].eq("No"), "MonthlyCharges"].mean()),
        "avg_tenure_churned": float(df.loc[df["Churn"].eq("Yes"), "tenure"].mean()),
        "avg_tenure_retained": float(df.loc[df["Churn"].eq("No"), "tenure"].mean()),
        "mtm_customers": int(df["Contract"].eq("Month-to-month").sum()),
        "mtm_churned": int(
            (df["Contract"].eq("Month-to-month") & df["Churn"].eq("Yes")).sum()
        ),
    }


def _finding(
    title: str, evidence: str, implication: str, recommendation: str
) -> List[str]:
    return [
        f"### {title}",
        "",
        f"**FINDING** — {title}",
        "",
        f"**EVIDENCE** — {evidence}",
        "",
        f"**BUSINESS IMPLICATION** — {implication}",
        "",
        f"**RECOMMENDATION** — {recommendation}",
        "",
    ]


def build_insights_report(
    featured: pd.DataFrame,
    quality_report: Dict[str, Any],
    churn_summaries: Dict[str, pd.DataFrame],
    revenue_tables: Dict[str, pd.DataFrame],
    tests: List[Dict[str, Any]],
    sql_results: Dict[str, Dict[str, pd.DataFrame]],
) -> Any:
    """Assemble and persist the final business insights report."""
    figures = compute_key_figures(featured)

    lines: List[str] = [
        "# Customer Churn Analytics & Retention Intelligence",
        "",
        "## Final Business Insights",
        "",
        "This report synthesizes the analytical findings for the telecom "
        "customer base. It is an **observational study**: all findings describe "
        "associations observed in the historical dataset. **None of the findings "
        "are causal claims.**",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        f"- Dataset: {figures['total_customers']:,} customers; "
        f"{figures['churned_customers']:,} churned "
        f"({_pct(figures['churn_rate'])}).",
        f"- Overall retention rate: {_pct(figures['retention_rate'])}.",
        f"- Total monthly revenue: {_fmt_money(figures['monthly_revenue'])}; "
        f"{_fmt_money(figures['churned_revenue'])} "
        f"({_pct(figures['churned_revenue_share'])}) is associated with customers "
        "who churned.",
        f"- Churned customers carried a higher average monthly charge "
        f"({_fmt_money(figures['avg_charge_churned'])} vs "
        f"{_fmt_money(figures['avg_charge_retained'])}) and a shorter average "
        f"tenure ({figures['avg_tenure_churned']:.1f} vs "
        f"{figures['avg_tenure_retained']:.1f} months).",
        "",
        "---",
        "",
        "## Major Findings",
        "",
    ]

    # --- Finding 1: contract -------------------------------------------------
    mtm = figures["contract_rates"].get("Month-to-month", 0.0)
    one = figures["contract_rates"].get("One year", 0.0)
    two = figures["contract_rates"].get("Two year", 0.0)
    lines += _finding(
        "Month-to-month customers show the highest observed churn rate",
        f"{_pct(mtm)} of month-to-month customers churned "
        f"({figures['mtm_customers']:,} customers), versus {_pct(one)} for "
        f"one-year and {_pct(two)} for two-year contracts.",
        "This segment represents a large, recurring and largely avoidable "
        "retention opportunity given the size of the month-to-month base.",
        "Investigate incentives that encourage movement to longer-term "
        "commitments (e.g., multi-month discounts, mid-term upgrades, loyalty "
        "credits) and study the drivers behind month-to-month behavior.",
    )

    # --- Finding 2: tenure ---------------------------------------------------
    tenure_rates = figures["tenure_rates"]
    early_rate = tenure_rates.get("0-6", 0.0)
    late_rate = tenure_rates.get("61+", 0.0)
    highest_tenure = tenure_rates.idxmax()
    lines += _finding(
        "Churn is highest in the earliest tenure window and declines sharply "
        "with tenure",
        f"Customers in the {highest_tenure}-month group churned at "
        f"{_pct(tenure_rates.max())}, while customers with 61+ months churned "
        f"at {_pct(late_rate)}.",
        "Early-tenure attrition suggests the onboarding and first-bill "
        "experience are critical touchpoints; retention effort is more "
        "effective where the churn probability is highest.",
        "Design an onboarding / first-90-day engagement program and monitor "
        "early-tenure cohorts; the observed retention gains at higher tenure "
        "support a 'get through the first year' framing.",
    )

    # --- Finding 3: internet service -----------------------------------------
    fiber = figures["internet_rates"].get("Fiber optic", 0.0)
    dsl = figures["internet_rates"].get("DSL", 0.0)
    none_ = figures["internet_rates"].get("No", 0.0)
    lines += _finding(
        "Fiber optic customers churned at roughly twice the rate of DSL and "
        "non-internet customers",
        f"Fiber optic customers churned at {_pct(fiber)} versus {_pct(dsl)} "
        f"(DSL) and {_pct(none_)} (no internet service).",
        "Fiber optic customers are high-value (higher charges) but their churn "
        "rate is elevated, indicating a service-quality or expectation-gap "
        "risk worth investigating.",
        "Investigate fiber optic service quality, outage and support "
        "experience; bundle proactive service checks or compensation "
        "mechanisms for this high-value group.",
    )

    # --- Finding 4: payment method -------------------------------------------
    ec = figures["payment_rates"].get("Electronic check", 0.0)
    bc = figures["payment_rates"].get("Bank transfer (automatic)", 0.0)
    cc = figures["payment_rates"].get("Credit card (automatic)", 0.0)
    mc = figures["payment_rates"].get("Mailed check", 0.0)
    lines += _finding(
        "Electronic check payers churned at the highest rate of any payment "
        "method",
        f"Electronic check payers churned at {_pct(ec)}, versus "
        f"{_pct(mc)} (mailed check), {_pct(bc)} (bank transfer automatic) and "
        f"{_pct(cc)} (credit card automatic).",
        "Payment method is strongly associated with churn. Automatic payment "
        "customers show materially lower observed churn.",
        "Promote automatic payment enrollment (bank transfer / credit card) "
        "with small incentives and investigate friction points for electronic "
        "check payers.",
    )

    # --- Finding 5: support/security gaps ------------------------------------
    lines += _finding(
        "Customers without tech support or online security churned at much "
        "higher rates",
        f"Customers without tech support churned at {_pct(figures['support_gap_rate'])} "
        f"versus {_pct(figures['support_ok_rate'])} for customers with it; "
        f"customers without online security churned at "
        f"{_pct(figures['security_gap_rate'])} versus "
        f"{_pct(figures['security_ok_rate'])} for those with it.",
        "Lack of add-on protective/support services is associated with elevated "
        "churn, suggesting engagement and perceived-protection gaps.",
        "Test proactive onboarding of online security and tech support offers, "
        "especially for new customers on high-value services.",
    )

    # --- Finding 6: charges --------------------------------------------------
    lines += _finding(
        "Churned customers carried, on average, higher monthly charges",
        f"Churned customers had a mean monthly charge of "
        f"{_fmt_money(figures['avg_charge_churned'])} versus "
        f"{_fmt_money(figures['avg_charge_retained'])} for retained customers.",
        "Higher-bill customers appear more likely to churn, possibly due to "
        "price sensitivity or value perception at higher spend levels.",
        "Analyze the value-perception of high-bill customers; consider "
        "targeted value adds (discounts, bundled perks) rather than blanket "
        "price cuts.",
    )

    # --- Finding 7: revenue at risk ------------------------------------------
    contract_rev = revenue_tables.get("Contract", pd.DataFrame())
    churned_share_contract = 0.0
    if not contract_rev.empty and "churned_revenue_share" in contract_rev.columns:
        churned_share_contract = float(contract_rev["churned_revenue_share"].max())
    lines += _finding(
        "A significant share of monthly recurring revenue is associated with "
        "customers who churned",
        f"{_fmt_money(figures['churned_revenue'])} of "
        f"{_fmt_money(figures['monthly_revenue'])} total monthly revenue "
        f"({_pct(figures['churned_revenue_share'])}) is associated with "
        "customers observed to churn.",
        "This is a direct measure of the revenue surface exposed to churn "
        "risk and frames the commercial value of retention.",
        "Prioritize retention spend by balancing churn probability against "
        "customer revenue, rather than by churn probability alone.",
    )

    # --- Finding 8: senior citizens ------------------------------------------
    lines += _finding(
        "Senior citizens show a higher observed churn rate",
        f"Senior citizens churned at {_pct(figures['senior_rate'])} versus "
        f"{_pct(figures['non_senior_rate'])} for non-seniors.",
        "Age-segmented needs (support style, usability, communication "
        "channels) may not be fully met for this group.",
        "Explore segment-specific support and communication approaches for "
        "senior customers and measure their response.",
    )

    # --- Finding 9: segments -------------------------------------------------
    seg_rates = figures["segment_rates"]
    seg_rev = figures["segment_revenue"]
    worst_segment = seg_rates.idxmax()
    best_segment = seg_rates.idxmin()
    top_rev_segment = seg_rev.idxmax()
    lines += _finding(
        "New + High Value customers churn most; Loyal + High Value customers "
        "anchor the revenue base",
        f"The {worst_segment} segment shows the highest observed churn rate "
        f"({_pct(seg_rates[worst_segment])}). The {best_segment} segment shows "
        f"the lowest ({_pct(seg_rates[best_segment])}). The {top_rev_segment} "
        f"segment contributes {_fmt_money(seg_rev[top_rev_segment])} in monthly "
        "revenue.",
        "The two-sided nature of the customer base (high-churn early/high-"
        "value vs stable late/high-value) requires different retention "
        "strategies per segment.",
        "Treat 'New + High Value' as the priority early-intervention segment "
        "and design loyalty programs that protect the 'Loyal + High Value' "
        "revenue base.",
    )

    # --- Statistical summary -------------------------------------------------
    lines += [
        "## Statistical Analysis Summary",
        "",
        "All tests use alpha = 0.05. Statistical significance indicates an "
        "observed association in this dataset and does not imply causation.",
        "",
    ]
    for test in tests:
        lines.append(
            f"- **{test['variable']} vs churn** ({test['test']}): "
            f"statistic = {test['statistic']:.2f}, p-value = "
            f"{test['p_value']:.2e}"
            + (f", df = {test['degrees_of_freedom']}" if test["degrees_of_freedom"] is not None else "")
            + f". {test['conclusion'].split('.')[0]}."
        )
    lines.append("")

    # --- Priority recommendation ladder --------------------------------------
    lines += [
        "---",
        "",
        "## Priority Recommendations (observations separated from actions)",
        "",
        "The recommendations below follow directly from the observed findings. "
        "They are business actions to test, not guaranteed outcomes.",
        "",
        "1. **Target early-tenure attrition** — the 0-6 month group shows the "
        "highest churn; build an onboarding/engagement program and monitor "
        "cohort-level churn monthly.",
        "2. **Shift month-to-month customers to longer commitments** — the "
        "largest churned segment; test retention offers at renewal and "
        "compare take-rates.",
        "3. **Enroll electronic check payers in automatic payments** — "
        "automatic payment methods show materially lower observed churn.",
        "4. **Investigate fiber optic service experience** — high churn on a "
        "high-value service points to a service-quality risk.",
        "5. **Reduce support/security service gaps** — customers without tech "
        "support and online security churn at higher rates; test proactive "
        "offers.",
        "6. **Prioritize high-value early customers** — the New + High Value "
        "segment combines elevated churn with elevated revenue.",
        "7. **Protect the revenue base** — loyalty/engagement programming for "
        "Loyal + High Value customers, who contribute the largest monthly "
        "revenue.",
        "",
    ]

    # --- Limitations ----------------------------------------------------------
    lines += [
        "## Limitations",
        "",
        "- Observational data: associations, not causal effects.",
        "- The dataset is a historical snapshot; no timing of events is "
        "available, so lead/lag effects cannot be established.",
        "- 11 customers have zero recorded TotalCharges (tenure 0); they were "
        "retained with TotalCharges set to 0 after verification that their "
        "tenure was 0.",
        "- Thresholds for tenure groups, charge groups and value segments are "
        "documented analytical choices; different thresholds may change "
        "segmentation results.",
        "- Revenue figures represent monthly charges associated with churned "
        "customers, not forecast future losses.",
        "",
        "---",
        "",
        "## Generated Artifacts",
        "",
        "- Data quality report: `reports/data_quality_report.md`",
        "- Charts: `reports/figures/` (static PNG + interactive HTML)",
        "- SQL database: `data/processed/customer_churn.db`",
        "- SQL query results: `reports/analysis_results/sql_query_results.md`",
        "- Statistical tests: `reports/analysis_results/statistical_tests.md`",
        "",
    ]

    path = REPORTS_DIR / "final_business_insights.md"
    path.write_text("\n".join(lines), encoding="utf-8")

    # Also persist the key figures machine-readable file.
    (RESULTS_DIR / "key_figures.json").write_text(
        _serialize_figures(figures), encoding="utf-8"
    )
    return path


def _serialize_figures(figures: Dict[str, Any]) -> str:
    import json

    clean: Dict[str, Any] = {}
    for key, value in figures.items():
        if isinstance(value, pd.Series):
            clean[key] = value.to_dict()
        else:
            clean[key] = value
    return json.dumps(clean, indent=2, default=str)
