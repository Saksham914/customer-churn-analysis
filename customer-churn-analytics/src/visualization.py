"""Chart generation for the churn analysis.

Produces publication-quality matplotlib/seaborn figures and interactive
Plotly HTML charts into reports/figures/. Every chart is computed from the
data at runtime.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Sequence

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import seaborn as sns

from src import FIGURES_DIR

CHURN_PALETTE = {"No": "#2e7d32", "Yes": "#c62828"}
ACCENT = "#1565c0"
SECOND = "#6a1b9a"

sns.set_theme(style="whitegrid", font_scale=1.05, rc={"figure.dpi": 130})
plt.rcParams["axes.titlesize"] = 13
plt.rcParams["axes.titleweight"] = "bold"
plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.right"] = False


def _save_fig(fig, name: str, fig_dir: Path) -> Path:
    path = fig_dir / f"{name}.png"
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    return path


def _churn_rate_series(df: pd.DataFrame, group_col: str) -> pd.Series:
    return df.groupby(group_col, observed=True)[
        "Churn"
    ].apply(lambda s: s.eq("Yes").mean())


def _count_series(df: pd.DataFrame, group_col: str) -> pd.Series:
    return df.groupby(group_col, observed=True).size()


# --------------------------------------------------------------------------
# Static matplotlib charts
# --------------------------------------------------------------------------

def plot_overall_churn(df: pd.DataFrame, fig_dir: Path = FIGURES_DIR) -> Path:
    counts = df["Churn"].value_counts()
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.pie(
        counts.values,
        labels=counts.index,
        autopct=lambda p: f"{p:.1f}%\n({int(round(p*counts.sum()/100)):,})",
        colors=[CHURN_PALETTE["No"], CHURN_PALETTE["Yes"]],
        startangle=90,
        explode=(0, 0.06),
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
        textprops={"fontsize": 11},
    )
    ax.set_title("Overall Churn vs Retention\nTelecom Customer Churn Dataset")
    return _save_fig(fig, "01_overall_churn", fig_dir)


def plot_churn_by_contract(df: pd.DataFrame, fig_dir: Path = FIGURES_DIR) -> Path:
    fig, ax = plt.subplots(figsize=(8, 5))
    order = ["Month-to-month", "One year", "Two year"]
    rates = _churn_rate_series(df, "Contract").reindex(order)
    counts = _count_series(df, "Contract").reindex(order)
    bars = ax.bar(
        rates.index, rates.values * 100, color=[ACCENT, SECOND, "#00838f"]
    )
    for bar, rate, count in zip(bars, rates.values, counts.values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            f"{rate*100:.1f}%  (n={count:,})",
            ha="center", fontsize=9,
        )
    ax.set_ylabel("Churn rate (%)")
    ax.set_title("Observed Churn Rate by Contract Type")
    ax.set_ylim(0, max(rates.values * 100) * 1.2)
    return _save_fig(fig, "02_churn_by_contract", fig_dir)


def plot_churn_by_tenure(df: pd.DataFrame, fig_dir: Path = FIGURES_DIR) -> Path:
    tenure_order = ["0-6", "7-12", "13-24", "25-36", "37-48", "49-60", "61+"]
    rates = _churn_rate_series(df, "tenure_group").reindex(tenure_order)
    counts = _count_series(df, "tenure_group").reindex(tenure_order)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(rates.index, rates.values * 100, marker="o", linewidth=2.5,
            color=ACCENT, markersize=7)
    for x, rate, count in zip(range(len(rates)), rates.values, counts.values):
        ax.annotate(
            f"{rate*100:.1f}%\n(n={count:,})",
            (x, rate * 100), textcoords="offset points",
            xytext=(0, 10), ha="center", fontsize=8.5,
        )
    ax.set_xlabel("Tenure group (months)")
    ax.set_ylabel("Churn rate (%)")
    ax.set_title("Observed Churn Rate by Customer Tenure")
    ax.set_ylim(0, max(rates.values * 100) * 1.25)
    return _save_fig(fig, "03_churn_by_tenure", fig_dir)


def plot_churn_by_internet(df: pd.DataFrame, fig_dir: Path = FIGURES_DIR) -> Path:
    order = ["No", "DSL", "Fiber optic"]
    rates = _churn_rate_series(df, "InternetService").reindex(order)
    counts = _count_series(df, "InternetService").reindex(order)
    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(rates.index, rates.values * 100, color=["#8e24aa", "#3949ab", "#ef6c00"])
    for bar, rate, count in zip(bars, rates.values, counts.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f"{rate*100:.1f}%  (n={count:,})", ha="center", fontsize=9)
    ax.set_ylabel("Churn rate (%)")
    ax.set_title("Observed Churn Rate by Internet Service")
    ax.set_ylim(0, max(rates.values * 100) * 1.2)
    return _save_fig(fig, "04_churn_by_internet", fig_dir)


def plot_churn_by_payment(df: pd.DataFrame, fig_dir: Path = FIGURES_DIR) -> Path:
    rates = _churn_rate_series(df, "PaymentMethod").sort_values()
    counts = _count_series(df, "PaymentMethod").loc[rates.index]
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.barh(rates.index, rates.values * 100, color="#0277bd")
    for bar, rate, count in zip(bars, rates.values, counts.values):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                f"{rate*100:.1f}%  (n={count:,})", va="center", fontsize=9)
    ax.set_xlabel("Churn rate (%)")
    ax.set_title("Observed Churn Rate by Payment Method")
    ax.set_xlim(0, max(rates.values * 100) * 1.25)
    return _save_fig(fig, "05_churn_by_payment", fig_dir)


def plot_churn_by_support_services(df: pd.DataFrame, fig_dir: Path = FIGURES_DIR) -> Path:
    service_cols = ["OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport"]
    fig, axes = plt.subplots(1, 4, figsize=(16, 4.5), sharey=True)
    for ax, col in zip(axes, service_cols):
        rates = _churn_rate_series(df, col)
        counts = _count_series(df, col)
        order = [v for v in ["Yes", "No", "No phone service"] if v in rates.index]
        rates = rates.reindex(order)
        counts = counts.reindex(order)
        colors = ["#2e7d32" if v == "Yes" else "#c62828" if v == "No" else "#78909c"
                  for v in order]
        bars = ax.bar(rates.index, rates.values * 100, color=colors)
        for bar, rate in zip(bars, rates.values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f"{rate*100:.0f}%", ha="center", fontsize=8)
        ax.set_title(col, fontsize=11)
        ax.tick_params(axis="x", rotation=25)
        ax.set_ylim(0, 60)
    axes[0].set_ylabel("Churn rate (%)")
    fig.suptitle("Observed Churn Rate by Support / Security Service", fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    path = fig_dir / "06_churn_by_support_services.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    return path


def plot_monthly_charges_by_churn(df: pd.DataFrame, fig_dir: Path = FIGURES_DIR) -> Path:
    fig, ax = plt.subplots(figsize=(7, 5))
    order = ["No", "Yes"]
    sns.boxplot(
        data=df, x="Churn", y="MonthlyCharges", order=order, ax=ax,
        palette=[CHURN_PALETTE["No"], CHURN_PALETTE["Yes"]],
        showfliers=True,
    )
    means = df.groupby("Churn")["MonthlyCharges"].mean().reindex(order)
    for i, status in enumerate(order):
        ax.plot(i, means[status], marker="D", color="black", markersize=6, zorder=5)
        ax.annotate(f"mean={means[status]:.2f}", (i, means[status]),
                    textcoords="offset points", xytext=(8, -14), fontsize=8.5)
    ax.set_title("Monthly Charges Distribution by Churn Status")
    ax.set_ylabel("Monthly charges (USD)")
    return _save_fig(fig, "07_monthly_charges_vs_churn", fig_dir)


def plot_tenure_by_churn(df: pd.DataFrame, fig_dir: Path = FIGURES_DIR) -> Path:
    fig, ax = plt.subplots(figsize=(7, 5))
    order = ["No", "Yes"]
    sns.boxplot(
        data=df, x="Churn", y="tenure", order=order, ax=ax,
        palette=[CHURN_PALETTE["No"], CHURN_PALETTE["Yes"]],
        showfliers=True,
    )
    medians = df.groupby("Churn")["tenure"].median().reindex(order)
    for i, status in enumerate(order):
        ax.plot(i, medians[status], marker="D", color="black", markersize=6, zorder=5)
        ax.annotate(f"median={medians[status]:.0f}", (i, medians[status]),
                    textcoords="offset points", xytext=(8, -14), fontsize=8.5)
    ax.set_title("Customer Tenure Distribution by Churn Status")
    ax.set_ylabel("Tenure (months)")
    return _save_fig(fig, "08_tenure_vs_churn", fig_dir)


def plot_revenue_by_contract(df: pd.DataFrame, fig_dir: Path = FIGURES_DIR) -> Path:
    revenue = (
        df.groupby("Contract")["MonthlyCharges"]
        .sum().sort_values(ascending=False)
    )
    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(revenue.index, revenue.values, color=[ACCENT, SECOND, "#00838f"])
    for bar, value in zip(bars, revenue.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2_000,
                f"${value:,.0f}", ha="center", fontsize=9)
    ax.set_ylabel("Total monthly revenue (USD)")
    ax.set_title("Total Monthly Revenue by Contract Type")
    ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"${v:,.0f}"))
    return _save_fig(fig, "09_revenue_by_contract", fig_dir)


def plot_revenue_associated_with_churn(df: pd.DataFrame, fig_dir: Path = FIGURES_DIR) -> Path:
    pivot = df.groupby("Contract")["MonthlyCharges"].apply(
        lambda s: s.loc[df.loc[s.index, "Churn"].eq("Yes")].sum()
    ).sort_values(ascending=False)
    total = df.groupby("Contract")["MonthlyCharges"].sum().loc[pivot.index]
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(pivot.index, pivot.values, color="#c62828", label="Churned")
    ax.bar(pivot.index, (total - pivot).values, bottom=pivot.values,
           color="#8bc34a", label="Retained")
    for bar, value in zip(bars, pivot.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1_500,
                f"${value:,.0f}", ha="center", fontsize=9)
    ax.set_ylabel("Total monthly revenue (USD)")
    ax.set_title("Monthly Revenue Associated with Churned Customers by Contract")
    ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"${v:,.0f}"))
    ax.legend()
    return _save_fig(fig, "10_revenue_associated_with_churn", fig_dir)


def plot_customer_segmentation(df: pd.DataFrame, fig_dir: Path = FIGURES_DIR) -> Path:
    from src.segmentation import SEGMENT_ORDER
    rates = _churn_rate_series(df, "customer_value_segment").reindex(SEGMENT_ORDER)
    counts = _count_series(df, "customer_value_segment").reindex(SEGMENT_ORDER)
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = ["#5c6bc0", "#ef5350", "#5c6bc0", "#ef5350", "#5c6bc0", "#ef5350"]
    bars = ax.bar(rates.index, rates.values * 100, color=colors)
    for bar, rate, count in zip(bars, rates.values, counts.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.7,
                f"{rate*100:.1f}% (n={count:,})", ha="center", fontsize=8,
                rotation=0)
    ax.set_ylabel("Churn rate (%)")
    ax.set_title("Observed Churn Rate by Customer Value Segment")
    ax.tick_params(axis="x", rotation=20)
    ax.set_ylim(0, max(rates.values * 100) * 1.2)
    return _save_fig(fig, "11_customer_segmentation_churn", fig_dir)


def plot_churn_heatmap(df: pd.DataFrame, fig_dir: Path = FIGURES_DIR) -> Path:
    tenure_order = ["0-6", "7-12", "13-24", "25-36", "37-48", "49-60", "61+"]
    contract_order = ["Month-to-month", "One year", "Two year"]
    pivot = df.pivot_table(
        index="tenure_group", columns="Contract",
        values="Churn", aggfunc=lambda s: s.eq("Yes").mean(),
        observed=True,
    ).reindex(index=tenure_order, columns=contract_order)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(
        pivot * 100, annot=True, fmt=".1f", cmap="RdYlGn_r", ax=ax,
        cbar_kws={"label": "Churn rate (%)"}, vmin=0, vmax=100,
    )
    ax.set_title("Churn Rate Heatmap: Contract x Tenure Group")
    return _save_fig(fig, "12_churn_heatmap", fig_dir)


def plot_retention_by_tenure(df: pd.DataFrame, fig_dir: Path = FIGURES_DIR) -> Path:
    tenure_order = ["0-6", "7-12", "13-24", "25-36", "37-48", "49-60", "61+"]
    rates = (
        df.groupby("tenure_group", observed=True)["Churn"]
        .apply(lambda s: s.eq("No").mean())
        .reindex(tenure_order)
    )
    counts = _count_series(df, "tenure_group").reindex(tenure_order)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(rates.index, rates.values * 100, color="#2e7d32", alpha=0.85)
    ax.plot(rates.index, rates.values * 100, color="#1b5e20", marker="o",
            linewidth=2, markersize=6)
    for x, rate, count in zip(range(len(rates)), rates.values, counts.values):
        ax.annotate(f"{rate*100:.1f}%\n(n={count:,})", (x, rate * 100),
                    textcoords="offset points", xytext=(0, 7), ha="center",
                    fontsize=8.5)
    ax.set_xlabel("Tenure group (months)")
    ax.set_ylabel("Retention rate (%)")
    ax.set_title("Observed Retention Rate by Customer Tenure")
    ax.set_ylim(0, 100)
    return _save_fig(fig, "13_retention_by_tenure", fig_dir)


def plot_revenue_by_segment(df: pd.DataFrame, fig_dir: Path = FIGURES_DIR) -> Path:
    from src.segmentation import SEGMENT_ORDER
    revenue = (
        df.groupby("customer_value_segment")["MonthlyCharges"]
        .sum().reindex(SEGMENT_ORDER)
    )
    churned_rev = (
        df.loc[df["Churn"].eq("Yes")]
        .groupby("customer_value_segment")["MonthlyCharges"]
        .sum().reindex(SEGMENT_ORDER)
    )
    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(SEGMENT_ORDER))
    ax.bar(x - 0.2, revenue.values, width=0.4, color="#42a5f5", label="Total monthly revenue")
    ax.bar(x + 0.2, churned_rev.values, width=0.4, color="#ef5350",
           label="Revenue of churned customers")
    for xi, value in zip(x, churned_rev.values):
        if value > 0:
            ax.text(xi + 0.2, value + 400, f"${value:,.0f}", ha="center", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(SEGMENT_ORDER, rotation=20)
    ax.set_ylabel("Total monthly revenue (USD)")
    ax.set_title("Monthly Revenue by Customer Value Segment")
    ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"${v:,.0f}"))
    ax.legend()
    return _save_fig(fig, "14_revenue_by_segment", fig_dir)


def plot_tenure_histogram(df: pd.DataFrame, fig_dir: Path = FIGURES_DIR) -> Path:
    fig, ax = plt.subplots(figsize=(8, 5))
    for status, color in CHURN_PALETTE.items():
        subset = df.loc[df["Churn"].eq(status), "tenure"]
        ax.hist(subset, bins=30, alpha=0.55, label=f"{status} (churn)"
                if status == "Yes" else f"{status} (retained)", color=color)
    ax.set_xlabel("Tenure (months)")
    ax.set_ylabel("Number of customers")
    ax.set_title("Tenure Distribution by Churn Status")
    ax.legend()
    return _save_fig(fig, "15_tenure_histogram", fig_dir)


def plot_total_services_vs_churn(df: pd.DataFrame, fig_dir: Path = FIGURES_DIR) -> Path:
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(
        data=df, x="total_services", y="Churn", errorbar=None, ax=ax,
        estimator=lambda s: s.eq("Yes").mean(), color=ACCENT,
    )
    ax.set_ylabel("Observed churn rate (%)")
    ax.set_xlabel("Number of subscribed services")
    ax.set_title("Observed Churn Rate by Number of Subscribed Services")
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v*100:.0f}%"))
    return _save_fig(fig, "16_churn_by_total_services", fig_dir)


# --------------------------------------------------------------------------
# Interactive Plotly charts (saved as self-contained HTML)
# --------------------------------------------------------------------------

def plotly_churn_donut(df: pd.DataFrame, fig_dir: Path = FIGURES_DIR) -> Path:
    counts = df["Churn"].value_counts().reset_index()
    counts.columns = ["Churn", "customers"]
    fig = px.pie(
        counts, names="Churn", values="customers", hole=0.45,
        title="Overall Churn vs Retention (interactive)",
        color_discrete_map={"No": "#2e7d32", "Yes": "#c62828"},
    )
    path = fig_dir / "plotly_overall_churn.html"
    fig.write_html(str(path), include_plotlyjs=True, full_html=True)
    return path


def plotly_churn_by_contract(df: pd.DataFrame, fig_dir: Path = FIGURES_DIR) -> Path:
    table = (
        df.groupby("Contract", observed=True)["Churn"]
        .apply(lambda s: s.eq("Yes").mean() * 100)
        .reset_index()
    )
    table.columns = ["Contract", "churn_rate"]
    fig = px.bar(
        table, x="Contract", y="churn_rate", color="Contract",
        title="Observed Churn Rate by Contract (interactive)",
        labels={"churn_rate": "Churn rate (%)"},
        text=table["churn_rate"].round(1),
    )
    path = fig_dir / "plotly_churn_by_contract.html"
    fig.write_html(str(path), include_plotlyjs=True, full_html=True)
    return path


def plotly_monthly_charges_by_churn(df: pd.DataFrame, fig_dir: Path = FIGURES_DIR) -> Path:
    fig = px.box(
        df, x="Churn", y="MonthlyCharges", color="Churn",
        title="Monthly Charges by Churn Status (interactive)",
        labels={"MonthlyCharges": "Monthly charges (USD)"},
        color_discrete_map=CHURN_PALETTE,
    )
    path = fig_dir / "plotly_monthly_charges.html"
    fig.write_html(str(path), include_plotlyjs=True, full_html=True)
    return path


def plotly_churn_heatmap(df: pd.DataFrame, fig_dir: Path = FIGURES_DIR) -> Path:
    tenure_order = ["0-6", "7-12", "13-24", "25-36", "37-48", "49-60", "61+"]
    contract_order = ["Month-to-month", "One year", "Two year"]
    pivot = df.pivot_table(
        index="tenure_group", columns="Contract",
        values="Churn", aggfunc=lambda s: s.eq("Yes").mean() * 100,
        observed=True,
    ).reindex(index=tenure_order, columns=contract_order)
    fig = px.imshow(
        pivot, text_auto=".1f", aspect="auto",
        color_continuous_scale="RdYlGn_r",
        labels={"color": "Churn rate (%)"},
        title="Churn Rate Heatmap: Contract x Tenure (interactive)",
    )
    path = fig_dir / "plotly_churn_heatmap.html"
    fig.write_html(str(path), include_plotlyjs=True, full_html=True)
    return path


def generate_all_static_charts(df: pd.DataFrame, fig_dir: Path = FIGURES_DIR) -> List[Path]:
    """Generate every static chart and return the saved file paths."""
    fig_dir.mkdir(parents=True, exist_ok=True)
    paths = [
        plot_overall_churn(df, fig_dir),
        plot_churn_by_contract(df, fig_dir),
        plot_churn_by_tenure(df, fig_dir),
        plot_churn_by_internet(df, fig_dir),
        plot_churn_by_payment(df, fig_dir),
        plot_churn_by_support_services(df, fig_dir),
        plot_monthly_charges_by_churn(df, fig_dir),
        plot_tenure_by_churn(df, fig_dir),
        plot_revenue_by_contract(df, fig_dir),
        plot_revenue_associated_with_churn(df, fig_dir),
        plot_customer_segmentation(df, fig_dir),
        plot_churn_heatmap(df, fig_dir),
        plot_retention_by_tenure(df, fig_dir),
        plot_revenue_by_segment(df, fig_dir),
        plot_tenure_histogram(df, fig_dir),
        plot_total_services_vs_churn(df, fig_dir),
    ]
    plt.close("all")
    return paths


def generate_all_interactive_charts(df: pd.DataFrame, fig_dir: Path = FIGURES_DIR) -> List[Path]:
    """Generate every interactive Plotly chart and return the saved paths."""
    fig_dir.mkdir(parents=True, exist_ok=True)
    return [
        plotly_churn_donut(df, fig_dir),
        plotly_churn_by_contract(df, fig_dir),
        plotly_monthly_charges_by_churn(df, fig_dir),
        plotly_churn_heatmap(df, fig_dir),
    ]
