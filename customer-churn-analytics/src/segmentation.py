"""Analytical feature engineering and business segmentation.

This module creates derived, human-interpretable features from the cleaned
data. It is a deterministic business segmentation exercise -- NOT machine
learning. Thresholds below are documented analytical decisions chosen for
readability and stability across the dataset.

Documented thresholds
---------------------
tenure_group
    Bins (months): 0-6, 7-12, 13-24, 25-36, 37-48, 49-60, 61+

monthly_charge_group (USD / month)
    Low:    MonthlyCharges <  40
    Medium: 40 <= MonthlyCharges < 90
    High:   MonthlyCharges >= 90
    (rounded, interpretable breakpoints near the dataset's Q1 and Q3)

customer_value_segment
    Tenure tier (months):  New (<= 12) | Established (13-36) | Loyal (> 36)
    Charge tier (USD):     Low (< 60)  | High (>= 60)

total_services
    Count of subscribed services among the 9 binary service indicators.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

TENURE_BINS = [0, 7, 13, 25, 37, 49, 61, 73]
TENURE_LABELS = ["0-6", "7-12", "13-24", "25-36", "37-48", "49-60", "61+"]

CHARGE_LOW_EDGE = 40.0
CHARGE_HIGH_EDGE = 90.0

NEW_TENURE_EDGE = 12
LOYAL_TENURE_EDGE = 36
VALUE_CHARGE_EDGE = 60.0

SERVICE_COLUMNS = [
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
]


def add_tenure_group(df: pd.DataFrame) -> pd.DataFrame:
    """Add a categorical tenure_group column."""
    out = df.copy()
    out["tenure_group"] = pd.cut(
        out["tenure"],
        bins=TENURE_BINS,
        labels=TENURE_LABELS,
        right=False,
    ).astype("string")
    return out


def add_monthly_charge_group(df: pd.DataFrame) -> pd.DataFrame:
    """Add a Low / Medium / High monthly charge group column."""
    out = df.copy()
    charges = out["MonthlyCharges"]
    out["monthly_charge_group"] = np.select(
        [
            charges < CHARGE_LOW_EDGE,
            charges < CHARGE_HIGH_EDGE,
        ],
        ["Low", "Medium"],
        default="High",
    )
    return out


def add_total_services(df: pd.DataFrame) -> pd.DataFrame:
    """Count subscribed services per customer.

    Each service column contributes 1 when the customer is subscribed.
    'No phone service' for MultipleLines and 'No' for InternetService count
    as 0.
    """
    out = df.copy()
    counts = np.zeros(len(out), dtype=int)
    counts += out["PhoneService"].eq("Yes").to_numpy(dtype=int)
    counts += out["MultipleLines"].eq("Yes").to_numpy(dtype=int)
    counts += out["InternetService"].ne("No").to_numpy(dtype=int)
    for column in [
        "OnlineSecurity",
        "OnlineBackup",
        "DeviceProtection",
        "TechSupport",
        "StreamingTV",
        "StreamingMovies",
    ]:
        counts += out[column].eq("Yes").to_numpy(dtype=int)
    out["total_services"] = counts
    return out


def add_customer_value_segment(df: pd.DataFrame) -> pd.DataFrame:
    """Add a New/Established/Loyal x Low/High value segment column."""
    out = df.copy()
    tenure = out["tenure"]
    tenure_tier = np.select(
        [
            tenure <= NEW_TENURE_EDGE,
            tenure <= LOYAL_TENURE_EDGE,
        ],
        ["New", "Established"],
        default="Loyal",
    )
    charge_tier = np.where(
        out["MonthlyCharges"] < VALUE_CHARGE_EDGE, "Low Value", "High Value"
    )
    out["customer_value_segment"] = [
        f"{t} + {v}" for t, v in zip(tenure_tier, charge_tier)
    ]
    return out


def add_all_features(df: pd.DataFrame) -> pd.DataFrame:
    """Apply every analytical feature in one step."""
    out = add_tenure_group(df)
    out = add_monthly_charge_group(out)
    out = add_total_services(out)
    out = add_customer_value_segment(out)
    return out


SEGMENT_ORDER = [
    "New + Low Value",
    "New + High Value",
    "Established + Low Value",
    "Established + High Value",
    "Loyal + Low Value",
    "Loyal + High Value",
]
