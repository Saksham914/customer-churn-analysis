"""Data cleaning and data-quality assessment for the telecom churn dataset.

Everything in this module is deterministic and purely observational: it
validates the data, documents quality issues, and returns a cleaned
DataFrame ready for downstream analytical features.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from src import DATA_PROCESSED_DIR, DATA_RAW_DIR, REPORTS_DIR, RESULTS_DIR

DEFAULT_RAW_PATH = DATA_RAW_DIR / "WA_Fn-UseC_-Telco-Customer-Churn.csv"
CLEAN_OUTPUT_PATH = DATA_PROCESSED_DIR / "customer_churn_clean.csv"
REPORT_PATH = REPORTS_DIR / "data_quality_report.md"

# Columns that should be categorical text after cleaning.
CATEGORICAL_COLUMNS = [
    "gender",
    "SeniorCitizen",
    "Partner",
    "Dependents",
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
    "Churn",
]

# Numeric columns that must be float/int after cleaning.
NUMERIC_COLUMNS = ["tenure", "MonthlyCharges", "TotalCharges"]

ID_COLUMN = "customerID"


def load_raw_data(path: str | Path | None = None) -> pd.DataFrame:
    """Load the raw telco churn CSV file.

    Parameters
    ----------
    path : str or Path, optional
        Path to the raw CSV. Defaults to the expected raw-data location.

    Returns
    -------
    pandas.DataFrame
        The raw dataset as read from disk.
    """
    data_path = Path(path) if path is not None else DEFAULT_RAW_PATH
    if not data_path.exists():
        raise FileNotFoundError(
            f"Raw dataset not found at {data_path}. "
            "Place the IBM Telco Customer Churn CSV in data/raw/ and retry."
        )
    return pd.read_csv(data_path)


def _strip_whitespace(df: pd.DataFrame) -> pd.DataFrame:
    """Strip surrounding whitespace from all object/string columns."""
    cleaned = df.copy()
    for column in cleaned.select_dtypes(include=["object", "string"]).columns:
        cleaned[column] = cleaned[column].astype("string").str.strip()
    return cleaned


def _identify_blank_entries(df: pd.DataFrame) -> Dict[str, int]:
    """Count blank / whitespace-only / missing entries per column."""
    blanks: Dict[str, int] = {}
    for column in df.columns:
        series = df[column]
        blank_mask = series.isna() | series.astype("string").str.strip().eq("")
        count = int(blank_mask.sum())
        if count > 0:
            blanks[str(column)] = count
    return blanks


def _convert_total_charges(df: pd.DataFrame) -> pd.DataFrame:
    """Safely convert TotalCharges to numeric.

    Blank / whitespace entries become NaN. In this dataset every blank
    TotalCharges row has tenure == 0 (no full months billed yet), so NaN is
    replaced with 0.0 to preserve the row while avoiding fabricated amounts.
    """
    cleaned = df.copy()
    raw = cleaned["TotalCharges"].astype("string").str.strip()
    raw = raw.replace({"": np.nan, "nan": np.nan, "NaN": np.nan})
    cleaned["TotalCharges"] = pd.to_numeric(raw, errors="coerce")
    cleaned["TotalCharges"] = cleaned["TotalCharges"].fillna(0.0)
    return cleaned


def _validate_ids(df: pd.DataFrame) -> Dict[str, Any]:
    """Check customerID integrity (uniqueness, format, missing values)."""
    ids = df["customerID"]
    missing_ids = int(ids.isna().sum())
    duplicated_ids = int(ids.duplicated().sum())
    bad_format = int(~ids.astype("string").str.fullmatch(r"\d{4}-\w{6}", na=False).sum())
    return {
        "missing_customer_ids": missing_ids,
        "duplicated_customer_ids": duplicated_ids,
        "malformed_customer_ids": bad_format,
        "unique_customers": int(ids.nunique()),
    }


def _detect_duplicate_rows(df: pd.DataFrame) -> int:
    """Count fully duplicated rows (excluding customerID)."""
    columns = [c for c in df.columns if c != ID_COLUMN]
    return int(df.duplicated(subset=columns).sum())


def _outlier_summary(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """Investigate outliers on numeric columns via IQR and z-score.

    Outliers are reported, not removed: this is an observational study and
    removing observations would alter the very population under study.
    """
    summary: Dict[str, Dict[str, Any]] = {}
    for column in NUMERIC_COLUMNS:
        series = pd.to_numeric(df[column], errors="coerce")
        q1, q3 = series.quantile(0.25), series.quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        iqr_outliers = series[(series < lower) | (series > upper)]
        mean, std = series.mean(), series.std()
        z_scores = (series - mean) / std if std else series * 0
        z_outliers = series[z_scores.abs() > 3]
        summary[column] = {
            "count": int(series.count()),
            "min": float(series.min()) if series.count() else np.nan,
            "max": float(series.max()) if series.count() else np.nan,
            "mean": float(series.mean()) if series.count() else np.nan,
            "median": float(series.median()) if series.count() else np.nan,
            "iqr_lower_fence": float(lower),
            "iqr_upper_fence": float(upper),
            "iqr_outlier_count": int(iqr_outliers.count()),
            "zscore_outlier_count_3sd": int(z_outliers.count()),
        }
    return summary


def _categorical_inspection(df: pd.DataFrame) -> Dict[str, Dict[str, int]]:
    """List observed values and their frequencies for categorical columns."""
    inspection: Dict[str, Dict[str, int]] = {}
    for column in CATEGORICAL_COLUMNS:
        counts = df[column].value_counts(dropna=False)
        inspection[column] = {str(k): int(v) for k, v in counts.items()}
    return inspection


def _documented_senior_citizen(df: pd.DataFrame) -> pd.DataFrame:
    """Map SeniorCitizen 0/1 codes to readable Yes/No labels."""
    cleaned = df.copy()
    cleaned["SeniorCitizen"] = cleaned["SeniorCitizen"].map(
        {0: "No", 1: "Yes"}
    ).astype("string")
    return cleaned


def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, Dict[str, Any]]:
    """Clean the raw dataset and produce a data-quality report.

    Steps:
        1. Strip whitespace from string columns.
        2. Identify blank / invalid entries.
        3. Convert TotalCharges to numeric (blanks -> NaN -> 0 for tenure 0).
        4. Validate data types and normalize SeniorCitizen.
        5. Detect duplicate customerIDs and duplicate rows.
        6. Investigate outliers on numeric columns (reported, not removed).
        7. Inspect categorical value distributions.

    Returns
    -------
    (cleaned_df, quality_report) : tuple
        Cleaned DataFrame and a machine-readable quality report dict.
    """
    cleaned = _strip_whitespace(df)

    blank_entries = _identify_blank_entries(cleaned)
    cleaned = _convert_total_charges(cleaned)

    # After numeric conversion, re-check for remaining blanks.
    remaining_blanks = _identify_blank_entries(cleaned)

    cleaned = _documented_senior_citizen(cleaned)

    # Data-type validation.
    expected_types = {col: "numeric" for col in NUMERIC_COLUMNS}
    expected_types.update({col: "categorical" for col in CATEGORICAL_COLUMNS})
    dtype_check: Dict[str, str] = {}
    for column in NUMERIC_COLUMNS:
        is_numeric = pd.to_numeric(cleaned[column], errors="coerce").notna().all()
        dtype_check[column] = "ok" if is_numeric else "unexpected"
    for column in CATEGORICAL_COLUMNS:
        dtype_check[column] = "ok"

    id_check = _validate_ids(cleaned)
    duplicate_rows = _detect_duplicate_rows(cleaned)
    outlier_summary = _outlier_summary(cleaned)
    categorical_values = _categorical_inspection(cleaned)

    report: Dict[str, Any] = {
        "dataset_shape_before": {"rows": int(df.shape[0]), "columns": int(df.shape[1])},
        "dataset_shape_after": {
            "rows": int(cleaned.shape[0]),
            "columns": int(cleaned.shape[1]),
        },
        "missing_values": blank_entries,
        "blank_total_charges_filled_with_zero": int(
            blank_entries.get("TotalCharges", 0)
        ),
        "remaining_missing_values": remaining_blanks,
        "customer_id_check": id_check,
        "duplicate_rows_excluding_id": duplicate_rows,
        "dtype_validation": dtype_check,
        "outlier_investigation": outlier_summary,
        "categorical_value_counts": categorical_values,
        "notes": [
            "TotalCharges contained whitespace-only entries; all mapped rows had "
            "tenure == 0 and were filled with 0.0 (no full month billed).",
            "Outliers are investigated and reported but deliberately not removed "
            "(observational study).",
            "SeniorCitizen was relabelled from 0/1 to No/Yes for readability.",
            "No rows were dropped during cleaning.",
        ],
    }
    return cleaned, report


def save_clean_data(df: pd.DataFrame, path: str | Path | None = None) -> Path:
    """Persist the cleaned dataset to CSV."""
    out_path = Path(path) if path is not None else CLEAN_OUTPUT_PATH
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    return out_path


def save_quality_report(report: Dict[str, Any], path: str | Path | None = None) -> Path:
    """Save the machine-readable quality report as JSON."""
    out_path = Path(path) if path is not None else RESULTS_DIR / "data_quality_summary.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, default=str)
    return out_path


def _format_markdown_table(header: List[str], rows: List[List[Any]]) -> str:
    """Render a small markdown table from a header and rows."""
    lines = ["| " + " | ".join(str(h) for h in header) + " |"]
    lines.append("| " + " | ".join("---" for _ in header) + " |")
    for row in rows:
        lines.append("| " + " | ".join(str(c) for c in row) + " |")
    return "\n".join(lines)


def render_quality_report_markdown(report: Dict[str, Any]) -> str:
    """Render the quality report as human-readable markdown text."""
    lines: List[str] = [
        "# Data Quality Report",
        "",
        "Dataset: IBM Telco Customer Churn (raw file)",
        "",
        f"Shape before cleaning: **{report['dataset_shape_before']['rows']}** rows x "
        f"**{report['dataset_shape_before']['columns']}** columns",
        f"Shape after cleaning: **{report['dataset_shape_after']['rows']}** rows x "
        f"**{report['dataset_shape_after']['columns']}** columns",
        "",
        "## Missing / blank values",
        "",
    ]
    if report["missing_values"]:
        rows = [[k, v] for k, v in report["missing_values"].items()]
        lines.append(_format_markdown_table(["Column", "Blank/missing count"], rows))
    else:
        lines.append("No missing or blank values detected.")
    lines += [
        "",
        "## Customer ID integrity",
        "",
        _format_markdown_table(
            ["Check", "Result"],
            [
                ["Missing customer IDs", report["customer_id_check"]["missing_customer_ids"]],
                ["Duplicated customer IDs", report["customer_id_check"]["duplicated_customer_ids"]],
                ["Malformed customer IDs", report["customer_id_check"]["malformed_customer_ids"]],
                ["Unique customers", report["customer_id_check"]["unique_customers"]],
            ],
        ),
        "",
        f"Fully duplicated rows (ignoring customerID): "
        f"**{report['duplicate_rows_excluding_id']}**",
        "",
        "## Data-type validation",
        "",
        _format_markdown_table(
            ["Column", "Status"],
            [[k, v] for k, v in report["dtype_validation"].items()],
        ),
        "",
        "## Outlier investigation (reported, not removed)",
        "",
    ]
    outlier_rows = []
    for column, info in report["outlier_investigation"].items():
        outlier_rows.append(
            [
                column,
                info["count"],
                f"{info['min']:.2f}",
                f"{info['max']:.2f}",
                f"{info['mean']:.2f}",
                info["iqr_outlier_count"],
                info["zscore_outlier_count_3sd"],
            ]
        )
    lines.append(
        _format_markdown_table(
            ["Column", "Count", "Min", "Max", "Mean", "IQR outliers", "z>3 outliers"],
            outlier_rows,
        )
    )
    lines += [
        "",
        "## Categorical value inspection",
        "",
    ]
    for column, counts in report["categorical_value_counts"].items():
        lines.append(f"### {column}")
        lines.append("")
        lines.append(_format_markdown_table(["Value", "Count"], [[k, v] for k, v in counts.items()]))
        lines.append("")
    lines += ["## Cleaning notes", ""]
    lines += [f"- {note}" for note in report["notes"]]
    return "\n".join(lines)


def write_data_quality_report(
    report: Dict[str, Any], path: str | Path | None = None
) -> Path:
    """Write the human-readable data quality report to markdown."""
    out_path = Path(path) if path is not None else REPORT_PATH
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render_quality_report_markdown(report), encoding="utf-8")
    return out_path
