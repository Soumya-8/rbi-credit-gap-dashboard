"""Data preprocessing and feature engineering."""

from __future__ import annotations

import pandas as pd


def clean_numeric_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Convert columns to numeric and fill missing values with zero."""
    cleaned = df.copy()
    for column in columns:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce").fillna(0)
    return cleaned


def prepare_state_data(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare state-level data for analytics."""
    numeric = [
        "population_million",
        "deposits_crore",
        "credit_crore",
        "priority_sector_credit_crore",
        "gdp_proxy_crore",
        "expected_credit_crore",
    ]
    prepared = clean_numeric_columns(df, numeric)
    prepared["deposit_credit_ratio"] = (prepared["credit_crore"] / prepared["deposits_crore"]) * 100
    prepared["credit_per_capita"] = prepared["credit_crore"] / prepared["population_million"]
    prepared["priority_sector_share"] = (
        prepared["priority_sector_credit_crore"] / prepared["credit_crore"]
    ) * 100
    return prepared.replace([float("inf"), -float("inf")], 0).fillna(0)


def prepare_sector_data(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare sector-level data for analytics."""
    return clean_numeric_columns(df, ["credit_crore"]).fillna({"priority_classification": "Unknown"})


def merge_state_sector(state_df: pd.DataFrame, sector_df: pd.DataFrame) -> pd.DataFrame:
    """Merge sector exposure with state-level indicators."""
    keys = ["year", "state", "region", "state_code", "bank_type"]
    columns = keys + ["deposits_crore", "population_million", "gdp_proxy_crore"]
    return sector_df.merge(state_df[columns], on=keys, how="left")

