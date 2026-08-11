"""Customer Churn Analytics & Retention Intelligence - source package.

This package contains modular, reusable analysis components for a purely
observational telecom customer churn study. No machine learning models are
used anywhere in this project.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
RESULTS_DIR = REPORTS_DIR / "analysis_results"

for _directory in (DATA_RAW_DIR, DATA_PROCESSED_DIR, FIGURES_DIR, RESULTS_DIR):
    _directory.mkdir(parents=True, exist_ok=True)
