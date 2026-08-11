"""Pytest suite for the churn analytics pipeline.

Tests cover data loading, cleaning, feature engineering, churn
calculations, segmentation, and revenue calculations. They run against the
real raw dataset so results stay honest.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src import DATA_PROCESSED_DIR, DATA_RAW_DIR
from src.churn_analysis import churn_by_group, overall_churn
from src.data_cleaning import (
    _convert_total_charges,
    _identify_blank_entries,
    clean_data,
    load_raw_data,
)
from src.revenue_analysis import (
    average_charges_by_churn,
    revenue_by_group,
    revenue_overview,
)
from src.segmentation import (
    SEGMENT_ORDER,
    add_all_features,
    add_customer_value_segment,
    add_monthly_charge_group,
    add_tenure_group,
    add_total_services,
)

RAW_PATH = DATA_RAW_DIR / "WA_Fn-UseC_-Telco-Customer-Churn.csv"
CLEAN_PATH = DATA_PROCESSED_DIR / "customer_churn_clean.csv"


@pytest.fixture(scope="session")
def raw_df() -> pd.DataFrame:
    return load_raw_data(RAW_PATH)


@pytest.fixture(scope="session")
def clean_df(raw_df: pd.DataFrame) -> pd.DataFrame:
    cleaned, _ = clean_data(raw_df)
    return cleaned


@pytest.fixture(scope="session")
def featured_df(clean_df: pd.DataFrame) -> pd.DataFrame:
    return add_all_features(clean_df)


# --------------------------------------------------------------------------
# Data loading
# --------------------------------------------------------------------------

def test_raw_data_loading_shape(raw_df: pd.DataFrame) -> None:
    assert raw_df.shape == (7043, 21)


def test_raw_data_has_expected_columns(raw_df: pd.DataFrame) -> None:
    expected = {
        "customerID", "gender", "SeniorCitizen", "Partner", "Dependents",
        "tenure", "PhoneService", "MultipleLines", "InternetService",
        "OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport",
        "StreamingTV", "StreamingMovies", "Contract", "PaperlessBilling",
        "PaymentMethod", "MonthlyCharges", "TotalCharges", "Churn",
    }
    assert expected == set(raw_df.columns)


def test_raw_data_has_two_churn_classes(raw_df: pd.DataFrame) -> None:
    assert set(raw_df["Churn"].unique()) == {"Yes", "No"}


# --------------------------------------------------------------------------
# Cleaning
# --------------------------------------------------------------------------

def test_clean_data_preserves_row_count(raw_df: pd.DataFrame) -> None:
    cleaned, _ = clean_data(raw_df)
    assert len(cleaned) == len(raw_df) == 7043


def test_total_charges_conversion_is_numeric(raw_df: pd.DataFrame) -> None:
    cleaned, _ = clean_data(raw_df)
    assert pd.api.types.is_numeric_dtype(cleaned["TotalCharges"])


def test_total_charges_blanks_become_zero(raw_df: pd.DataFrame) -> None:
    cleaned, report = clean_data(raw_df)
    assert report["blank_total_charges_filled_with_zero"] == 11
    assert cleaned["TotalCharges"].isna().sum() == 0


def test_convert_total_charges_handles_whitespace() -> None:
    frame = pd.DataFrame({"TotalCharges": [" ", "  ", "100.5", "", "20"]})
    converted = _convert_total_charges(frame)
    assert converted["TotalCharges"].tolist() == [0.0, 0.0, 100.5, 0.0, 20.0]


def test_senior_citizen_relabelled(raw_df: pd.DataFrame) -> None:
    cleaned, _ = clean_data(raw_df)
    assert set(cleaned["SeniorCitizen"].unique()) == {"Yes", "No"}


def test_customer_ids_unique_and_complete(raw_df: pd.DataFrame) -> None:
    cleaned, report = clean_data(raw_df)
    check = report["customer_id_check"]
    assert check["duplicated_customer_ids"] == 0
    assert check["missing_customer_ids"] == 0


def test_quality_report_keys_present(raw_df: pd.DataFrame) -> None:
    _, report = clean_data(raw_df)
    for key in [
        "dataset_shape_before",
        "missing_values",
        "customer_id_check",
        "outlier_investigation",
        "categorical_value_counts",
    ]:
        assert key in report


# --------------------------------------------------------------------------
# Churn calculations
# --------------------------------------------------------------------------

def test_overall_churn_matches_dataset(clean_df: pd.DataFrame) -> None:
    result = overall_churn(clean_df)
    assert result["total_customers"] == 7043
    assert result["churned_customers"] == 1869
    assert result["retained_customers"] == 5174
    assert result["churn_rate"] == pytest.approx(1869 / 7043)
    assert result["retention_rate"] == pytest.approx(1 - 1869 / 7043)


def test_churn_by_group_rates_sum(clean_df: pd.DataFrame) -> None:
    table = churn_by_group(clean_df, "Contract")
    assert table["customers"].sum() == len(clean_df)
    assert table["churned"].sum() == 1869
    assert np.allclose(table["churn_rate"] + table["retention_rate"], 1.0)


def test_churn_by_group_monotonic_columns(clean_df: pd.DataFrame) -> None:
    table = churn_by_group(clean_df, "InternetService")
    assert (table["churned"] <= table["customers"]).all()
    assert (table["retained"] <= table["customers"]).all()


# --------------------------------------------------------------------------
# Feature engineering
# --------------------------------------------------------------------------

def test_tenure_group_bins(clean_df: pd.DataFrame) -> None:
    featured = add_tenure_group(clean_df)
    expected = {"0-6", "7-12", "13-24", "25-36", "37-48", "49-60", "61+"}
    assert set(featured["tenure_group"].unique()) == expected
    assert len(featured[featured["tenure_group"] == "0-6"]) == len(
        clean_df[clean_df["tenure"] <= 6]
    )
    assert len(featured[featured["tenure_group"] == "61+"]) == len(
        clean_df[clean_df["tenure"] >= 61]
    )


def test_monthly_charge_group_edges() -> None:
    frame = pd.DataFrame({"MonthlyCharges": [20.0, 39.99, 40.0, 89.99, 90.0, 118.75]})
    grouped = add_monthly_charge_group(frame)
    assert grouped["monthly_charge_group"].tolist() == [
        "Low", "Low", "Medium", "Medium", "High", "High",
    ]


def test_total_services_range(clean_df: pd.DataFrame) -> None:
    featured = add_total_services(clean_df)
    assert featured["total_services"].between(0, 9).all()
    assert featured["total_services"].dtype == int


def test_customer_value_segment_combinations(clean_df: pd.DataFrame) -> None:
    featured = add_customer_value_segment(clean_df)
    observed = set(featured["customer_value_segment"].unique())
    assert observed.issubset(set(SEGMENT_ORDER))
    assert len(observed) >= 4


def test_feature_pipeline_keeps_rows(clean_df: pd.DataFrame) -> None:
    featured = add_all_features(clean_df)
    assert len(featured) == len(clean_df)
    for column in [
        "tenure_group", "monthly_charge_group", "total_services",
        "customer_value_segment",
    ]:
        assert column in featured.columns


# --------------------------------------------------------------------------
# Revenue calculations
# --------------------------------------------------------------------------

def test_revenue_overview_totals(clean_df: pd.DataFrame) -> None:
    result = revenue_overview(clean_df)
    expected_total = clean_df["MonthlyCharges"].sum()
    assert result["total_monthly_revenue"] == pytest.approx(expected_total)
    assert result["monthly_revenue_churned"] + result["monthly_revenue_retained"] == \
        pytest.approx(expected_total)
    assert 0 <= result["churned_share_of_monthly_revenue"] <= 1


def test_revenue_overview_matches_direct_calculation(clean_df: pd.DataFrame) -> None:
    result = revenue_overview(clean_df)
    direct = clean_df.loc[clean_df["Churn"].eq("Yes"), "MonthlyCharges"].sum()
    assert result["monthly_revenue_churned"] == pytest.approx(float(direct))


def test_average_charges_by_churn(clean_df: pd.DataFrame) -> None:
    table = average_charges_by_churn(clean_df)
    assert set(table["Churn"]) == {"No", "Yes"}
    direct_mean = clean_df.groupby("Churn")["MonthlyCharges"].mean()
    assert table.set_index("Churn")["mean"].to_dict() == pytest.approx(
        direct_mean.to_dict()
    )


def test_revenue_by_group_revenue_consistency(clean_df: pd.DataFrame) -> None:
    table = revenue_by_group(clean_df, "Contract")
    expected_total = clean_df.groupby("Contract")["MonthlyCharges"].sum()
    assert table.set_index("Contract")["total_monthly_revenue"].to_dict() == pytest.approx(
        expected_total.to_dict()
    )
    for _, row in table.iterrows():
        assert row["churned_revenue"] + row["retained_revenue"] == pytest.approx(
            row["total_monthly_revenue"]
        )


def test_revenue_by_group_share_bounds(clean_df: pd.DataFrame) -> None:
    table = revenue_by_group(clean_df, "PaymentMethod")
    assert table["churned_revenue_share"].between(0, 1).all()


# --------------------------------------------------------------------------
# End-to-end saved artifacts
# --------------------------------------------------------------------------

def test_cleaned_csv_exists() -> None:
    assert CLEAN_PATH.exists(), "cleaned CSV has not been generated"


def test_cleaned_csv_round_trip() -> None:
    saved = pd.read_csv(CLEAN_PATH)
    assert saved.shape[0] == 7043
    assert pd.api.types.is_numeric_dtype(saved["TotalCharges"])
