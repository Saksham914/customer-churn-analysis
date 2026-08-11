#!/usr/bin/env python3
"""End-to-end pipeline for Customer Churn Analytics & Retention Intelligence.

Run from the project root:

    python run_analysis.py

Pipeline steps:
    1.  Load raw data
    2.  Clean data + data-quality report
    3.  Create analytical features (tenure group, charge group, services, segment)
    4.  Run EDA summaries
    5.  Run churn analysis by dimension
    6.  Run revenue analysis
    7.  Run segmentation analysis
    8.  Run statistical tests
    9.  Load cleaned data into SQLite and execute SQL queries
    10. Generate static + interactive charts
    11. Generate markdown reports (data quality, churn, revenue, statistics,
        SQL results, final business insights)

Everything is computed from the actual dataset; no results are hardcoded.
"""

from __future__ import annotations

import json
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from src import (
    DATA_PROCESSED_DIR,
    FIGURES_DIR,
    PROJECT_ROOT,
    RESULTS_DIR,
    REPORTS_DIR,
)
from src import churn_analysis as ca
from src import data_cleaning as dc
from src import revenue_analysis as ra
from src import segmentation as seg
from src import statistics as st
from src import visualization as viz

SQL_DIR = PROJECT_ROOT / "sql"
DB_PATH = DATA_PROCESSED_DIR / "customer_churn.db"
TABLE_NAME = "customers"

SEPARATOR = "=" * 72


def step_banner(message: str) -> None:
    print("\n" + SEPARATOR)
    print(f"STEP: {message}")
    print(SEPARATOR)


def step_1_2_3_load_clean_features() -> tuple[pd.DataFrame, Dict[str, Any]]:
    """Load, clean, and add analytical features."""
    step_banner("Loading raw data")
    raw = dc.load_raw_data()
    print(f"Raw dataset: {raw.shape[0]} rows x {raw.shape[1]} columns")

    step_banner("Cleaning data")
    clean, quality_report = dc.clean_data(raw)
    print(f"Cleaned dataset: {clean.shape[0]} rows x {clean.shape[1]} columns")
    print(f"Blank TotalCharges entries filled: "
          f"{quality_report['blank_total_charges_filled_with_zero']}")

    step_banner("Creating analytical features")
    featured = seg.add_all_features(clean)
    print("Created: tenure_group, monthly_charge_group, total_services, "
          "customer_value_segment")

    dc.save_clean_data(clean)
    print(f"Saved cleaned data to {dc.CLEAN_OUTPUT_PATH}")
    dc.save_quality_report(quality_report)
    dc.write_data_quality_report(quality_report)
    print(f"Saved quality report to {dc.REPORT_PATH}")

    return featured, quality_report


def step_4_eda(featured: pd.DataFrame) -> Dict[str, Any]:
    """Descriptive statistics of the cleaned, featured dataset."""
    step_banner("Running EDA")
    numeric_summary = featured[
        ["tenure", "MonthlyCharges", "TotalCharges", "total_services"]
    ].describe()
    eda_path = RESULTS_DIR / "eda_summary.csv"
    numeric_summary.round(2).to_csv(eda_path)
    print(f"Saved EDA numeric summary to {eda_path}")
    print(numeric_summary.round(2).to_string())
    return {
        "numeric_summary": numeric_summary.round(2).to_dict(),
        "categorical_counts": {
            col: featured[col].value_counts().astype(int).to_dict()
            for col in ["gender", "Contract", "InternetService", "PaymentMethod",
                        "tenure_group", "customer_value_segment"]
        },
    }


def step_5_churn_analysis(featured: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Churn by every documented dimension."""
    step_banner("Running churn analysis by dimension")
    overall = ca.overall_churn(featured)
    print(f"Overall churn rate: {overall['churn_rate']:.2%} "
          f"({overall['churned_customers']:,} of {overall['total_customers']:,})")

    summaries = ca.analyze_all_dimensions(featured)
    for dimension, table in summaries.items():
        table.to_csv(RESULTS_DIR / f"churn_by_{dimension}.csv", index=False)
    (RESULTS_DIR / "churn_analysis_by_dimension.md").write_text(
        ca.dimension_summary_markdown(summaries), encoding="utf-8"
    )
    print(f"Saved churn-by-dimension tables and markdown to {RESULTS_DIR}")
    return summaries


def step_6_revenue_analysis(featured: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Revenue analysis associated with churn."""
    step_banner("Running revenue analysis")
    overview = ra.revenue_overview(featured)
    print(
        f"Total monthly revenue: ${overview['total_monthly_revenue']:,.2f} | "
        f"churned share: {overview['churned_share_of_monthly_revenue']:.2%}"
    )

    avg_table = ra.average_charges_by_churn(featured)
    total_table = ra.total_charges_by_churn(featured)
    avg_table.to_csv(RESULTS_DIR / "avg_charges_by_churn.csv", index=False)
    total_table.to_csv(RESULTS_DIR / "total_charges_by_churn.csv", index=False)

    dimensions = ra.revenue_analysis_dimensions(featured)
    for dimension, table in dimensions.items():
        table.to_csv(RESULTS_DIR / f"revenue_by_{dimension}.csv", index=False)
    return dimensions


def step_7_segmentation(featured: pd.DataFrame) -> None:
    """Value-segment breakdown of churn and revenue."""
    step_banner("Running segmentation analysis")
    segment_churn = ca.churn_by_group(featured, "customer_value_segment")
    segment_churn = segment_churn.set_index("customer_value_segment").reindex(
        seg.SEGMENT_ORDER
    ).reset_index()
    segment_churn.to_csv(RESULTS_DIR / "segment_churn_summary.csv", index=False)

    segment_revenue = ra.revenue_by_group(featured, "customer_value_segment")
    segment_revenue = segment_revenue.set_index("customer_value_segment").reindex(
        seg.SEGMENT_ORDER
    ).reset_index()
    segment_revenue.to_csv(RESULTS_DIR / "segment_revenue_summary.csv", index=False)

    print("Saved segment churn and revenue summaries.")
    print(segment_churn.to_string(index=False))


def step_8_statistics(featured: pd.DataFrame) -> List[Dict[str, Any]]:
    """Statistical hypothesis tests."""
    step_banner("Running statistical tests (alpha=0.05)")
    tests = st.run_all_tests(featured)
    (RESULTS_DIR / "statistical_tests.md").write_text(
        st.tests_to_markdown(tests), encoding="utf-8"
    )
    summary = []
    for test in tests:
        summary.append(
            {
                "test": test["test"],
                "variable": test["variable"],
                "statistic": round(test["statistic"], 4),
                "p_value": test["p_value"],
                "degrees_of_freedom": test["degrees_of_freedom"],
                "conclusion": test["conclusion"],
            }
        )
    (RESULTS_DIR / "statistical_tests_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    for row in summary:
        print(f"{row['variable']:<20} statistic={row['statistic']:<12} "
              f"p={row['p_value']:.4e}")
    return tests


def _extract_queries(sql_text: str) -> List[Dict[str, str]]:
    """Split an SQL file into named queries.

    Each query is introduced by a comment line `-- <name>`. Multiple
    statements separated by blank lines are also handled.
    """
    queries: List[Dict[str, str]] = []
    current_name: str = "query"
    current_lines: List[str] = []
    for line in sql_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("--"):
            if current_lines and any(
                l.strip() and not l.strip().startswith("--") for l in current_lines
            ):
                queries.append({"name": current_name, "sql": "\n".join(current_lines)})
                current_lines = []
            match = re.match(r"--\s*(.+)$", stripped)
            current_name = match.group(1).strip() if match else current_name
            continue
        current_lines.append(line)
    if current_lines and any(l.strip() and not l.strip().startswith("--") for l in current_lines):
        queries.append({"name": current_name, "sql": "\n".join(current_lines)})
    return queries


def step_9_sql(featured: pd.DataFrame) -> Dict[str, Dict[str, pd.DataFrame]]:
    """Load data into SQLite and execute every named SQL query."""
    step_banner("Building SQLite database and running SQL queries")
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    featured.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)
    print(f"Loaded {len(featured):,} rows into {DB_PATH}")

    all_results: Dict[str, Dict[str, pd.DataFrame]] = {}
    for sql_file in sorted(SQL_DIR.glob("*.sql")):
        queries = _extract_queries(sql_file.read_text(encoding="utf-8"))
        file_results: Dict[str, pd.DataFrame] = {}
        for query in queries:
            result = pd.read_sql_query(query["sql"], conn)
            file_results[query["name"]] = result
            print(f"  [{sql_file.stem}] {query['name']}: {result.shape[0]} rows")
        all_results[sql_file.stem] = file_results
    conn.close()

    combined = {**all_results.get("churn_analysis", {}),
                **all_results.get("revenue_analysis", {}),
                **all_results.get("business_questions", {})}
    json_ready = {name: table.to_dict(orient="records") for name, table in combined.items()}
    (RESULTS_DIR / "sql_query_results.json").write_text(
        json.dumps(json_ready, indent=2, default=str), encoding="utf-8"
    )
    write_sql_results_markdown(all_results)
    return all_results


def _dataframe_to_markdown(table: pd.DataFrame) -> str:
    headers = [str(col) for col in table.columns]
    rows = [[str(value) for value in row] for row in table.itertuples(index=False)]
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def write_sql_results_markdown(all_results: Dict[str, Dict[str, pd.DataFrame]]) -> Path:
    """Write every SQL query result to a single markdown report."""
    lines: List[str] = ["# SQL Query Results", ""]
    for file_name, queries in all_results.items():
        lines.append(f"## {file_name}.sql")
        lines.append("")
        for query_name, table in queries.items():
            lines.append(f"### {query_name}")
            lines.append("")
            lines.append(_dataframe_to_markdown(table))
            lines.append("")
    path = RESULTS_DIR / "sql_query_results.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved SQL query results to {path}")
    return path


def step_10_charts(featured: pd.DataFrame) -> None:
    """Generate all static and interactive charts."""
    step_banner("Generating charts")
    static = viz.generate_all_static_charts(featured)
    interactive = viz.generate_all_interactive_charts(featured)
    print(f"Static charts: {len(static)}")
    for path in static:
        print(f"  {path.name}")
    print(f"Interactive charts: {len(interactive)}")
    for path in interactive:
        print(f"  {path.name}")


def step_11_reports(
    featured: pd.DataFrame,
    quality_report: Dict[str, Any],
    churn_summaries: Dict[str, pd.DataFrame],
    revenue_tables: Dict[str, pd.DataFrame],
    tests: List[Dict[str, Any]],
    sql_results: Dict[str, Dict[str, pd.DataFrame]],
) -> Path:
    """Write the final business insights report."""
    step_banner("Writing final business insights report")
    from src.insights import build_insights_report

    path = build_insights_report(
        featured=featured,
        quality_report=quality_report,
        churn_summaries=churn_summaries,
        revenue_tables=revenue_tables,
        tests=tests,
        sql_results=sql_results,
    )
    print(f"Saved {path}")
    return path


def main() -> int:
    featured, quality_report = step_1_2_3_load_clean_features()
    step_4_eda(featured)
    churn_summaries = step_5_churn_analysis(featured)
    revenue_tables = step_6_revenue_analysis(featured)
    step_7_segmentation(featured)
    tests = step_8_statistics(featured)
    sql_results = step_9_sql(featured)
    step_10_charts(featured)
    step_11_reports(
        featured, quality_report, churn_summaries, revenue_tables, tests, sql_results
    )

    print("\n" + SEPARATOR)
    print("PIPELINE COMPLETE")
    print(SEPARATOR)
    print(f"Reports:      {REPORTS_DIR}")
    print(f"Charts:       {FIGURES_DIR}")
    print(f"SQL database: {DB_PATH}")
    print("Use `pytest tests/` to run the automated test suite.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
