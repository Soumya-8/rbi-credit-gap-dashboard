"""Data loading, validation, and filtering."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import streamlit as st

from config import RAW_DATA_DIR


STATE_SCHEMA = {
    "year",
    "state",
    "region",
    "state_code",
    "bank_type",
    "population_million",
    "deposits_crore",
    "credit_crore",
    "priority_sector_credit_crore",
    "gdp_proxy_crore",
    "expected_credit_crore",
}
SECTOR_SCHEMA = {
    "year",
    "state",
    "region",
    "state_code",
    "bank_type",
    "sector",
    "priority_classification",
    "credit_crore",
}
DEPOSIT_SCHEMA = {
    "year",
    "state",
    "region",
    "state_code",
    "bank_type",
    "deposits_crore",
    "credit_crore",
    "deposit_credit_ratio",
}


@dataclass(frozen=True)
class DashboardData:
    """Container for all dashboard-ready datasets."""

    state: pd.DataFrame
    sector: pd.DataFrame
    deposit: pd.DataFrame


def validate_schema(df: pd.DataFrame, required_columns: set[str], name: str) -> None:
    """Raise a clear error when a CSV does not contain required columns."""
    missing = required_columns.difference(df.columns)
    if missing:
        raise ValueError(f"{name} is missing required columns: {sorted(missing)}")


def _read_csv(path: Path, schema: set[str], name: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Required dataset not found: {path}")
    df = pd.read_csv(path)
    validate_schema(df, schema, name)
    return df


@st.cache_data(show_spinner=False)
def load_dashboard_data(raw_dir: str | Path = RAW_DATA_DIR) -> DashboardData:
    """Load all raw datasets with Streamlit caching."""
    raw_path = Path(raw_dir)
    state = _read_csv(raw_path / "state_credit.csv", STATE_SCHEMA, "state_credit.csv")
    sector = _read_csv(raw_path / "sector_credit.csv", SECTOR_SCHEMA, "sector_credit.csv")
    deposit = _read_csv(raw_path / "deposit_credit.csv", DEPOSIT_SCHEMA, "deposit_credit.csv")
    return DashboardData(state=state, sector=sector, deposit=deposit)


def filter_dataframe(
    df: pd.DataFrame,
    years: tuple[int, int] | None = None,
    sectors: list[str] | None = None,
    states: list[str] | None = None,
    bank_types: list[str] | None = None,
    regions: list[str] | None = None,
    search: str | None = None,
) -> pd.DataFrame:
    """Apply dashboard filters to a dataframe."""
    filtered = df.copy()
    if years:
        filtered = filtered[filtered["year"].between(years[0], years[1])]
    if sectors and "sector" in filtered:
        filtered = filtered[filtered["sector"].isin(sectors)]
    if states:
        filtered = filtered[filtered["state"].isin(states)]
    if bank_types:
        filtered = filtered[filtered["bank_type"].isin(bank_types)]
    if regions:
        filtered = filtered[filtered["region"].isin(regions)]
    if search:
        mask = pd.Series(False, index=filtered.index)
        for column in ["state", "sector", "region", "bank_type"]:
            if column in filtered:
                mask = mask | filtered[column].str.contains(search, case=False, na=False)
        filtered = filtered[mask]
    return filtered

