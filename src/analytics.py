"""Reusable financial analytics functions."""

from __future__ import annotations

import numpy as np
import pandas as pd


def aggregate_state(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate bank-level records to state-year level."""
    group_cols = ["year", "state", "region", "state_code"]
    agg = (
        df.groupby(group_cols, as_index=False)
        .agg(
            population_million=("population_million", "max"),
            deposits_crore=("deposits_crore", "sum"),
            credit_crore=("credit_crore", "sum"),
            priority_sector_credit_crore=("priority_sector_credit_crore", "sum"),
            gdp_proxy_crore=("gdp_proxy_crore", "max"),
            expected_credit_crore=("expected_credit_crore", "sum"),
        )
    )
    agg["deposit_credit_ratio"] = agg["credit_crore"] / agg["deposits_crore"] * 100
    agg["credit_per_capita"] = agg["credit_crore"] / agg["population_million"]
    agg["priority_sector_share"] = agg["priority_sector_credit_crore"] / agg["credit_crore"] * 100
    return agg.replace([np.inf, -np.inf], 0).fillna(0)


def aggregate_sector(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate sector data to sector-year level."""
    return (
        df.groupby(["year", "sector", "priority_classification"], as_index=False)
        .agg(credit_crore=("credit_crore", "sum"))
        .sort_values(["year", "credit_crore"], ascending=[True, False])
    )


def yoy_growth(df: pd.DataFrame, group_cols: list[str], value_col: str) -> pd.DataFrame:
    """Calculate year-over-year growth percentage."""
    out = df.sort_values(group_cols + ["year"]).copy()
    out[f"{value_col}_yoy_growth"] = out.groupby(group_cols)[value_col].pct_change() * 100
    return out


def cagr(start_value: float, end_value: float, periods: int) -> float:
    """Calculate compound annual growth rate."""
    if start_value <= 0 or periods <= 0:
        return 0.0
    return ((end_value / start_value) ** (1 / periods) - 1) * 100


def add_moving_average(
    df: pd.DataFrame,
    group_cols: list[str],
    value_col: str,
    window: int = 3,
) -> pd.DataFrame:
    """Add a rolling moving average column."""
    out = df.sort_values(group_cols + ["year"]).copy()
    out[f"{value_col}_{window}y_ma"] = (
        out.groupby(group_cols)[value_col]
        .transform(lambda series: series.rolling(window=window, min_periods=1).mean())
    )
    return out


def credit_gap(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate expected credit, actual credit, gap, gap percentage, and ranking."""
    out = df.copy()
    if "expected_credit_crore" not in out:
        benchmark = out.groupby("region")["deposit_credit_ratio"].transform("median") / 100
        out["expected_credit_crore"] = out["deposits_crore"] * benchmark
    out["credit_gap_crore"] = out["expected_credit_crore"] - out["credit_crore"]
    out["gap_pct"] = out["credit_gap_crore"] / out["expected_credit_crore"] * 100
    out["opportunity_index"] = (
        out["gap_pct"].clip(lower=0) * 0.45
        + (100 - out["deposit_credit_ratio"]).clip(lower=0) * 0.35
        + out["priority_sector_share"].rsub(45).clip(lower=0) * 0.20
    )
    out["gap_rank"] = out["credit_gap_crore"].rank(ascending=False, method="dense").astype(int)
    return out.replace([np.inf, -np.inf], 0).fillna(0)


def top_performers(df: pd.DataFrame, metric: str, n: int = 10) -> pd.DataFrame:
    """Return the top n records by metric."""
    return df.nlargest(n, metric)


def bottom_performers(df: pd.DataFrame, metric: str, n: int = 10) -> pd.DataFrame:
    """Return the bottom n records by metric."""
    return df.nsmallest(n, metric)


def national_kpis(state_df: pd.DataFrame, sector_df: pd.DataFrame) -> dict[str, float | str]:
    """Calculate headline dashboard KPIs for the latest filtered year."""
    latest_year = int(state_df["year"].max())
    latest_state = aggregate_state(state_df[state_df["year"] == latest_year])
    sector_latest = aggregate_sector(sector_df[sector_df["year"] == latest_year])
    state_growth = yoy_growth(aggregate_state(state_df), ["state"], "credit_crore")
    latest_growth = state_growth[state_growth["year"] == latest_year]["credit_crore_yoy_growth"].mean()
    return {
        "year": latest_year,
        "total_credit": latest_state["credit_crore"].sum(),
        "total_deposits": latest_state["deposits_crore"].sum(),
        "avg_credit_growth": latest_growth,
        "top_sector": sector_latest.iloc[0]["sector"] if not sector_latest.empty else "NA",
        "highest_credit_state": latest_state.nlargest(1, "credit_crore").iloc[0]["state"],
    }

