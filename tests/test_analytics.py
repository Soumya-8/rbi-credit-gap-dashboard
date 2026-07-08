"""Tests for core analytics functions."""

from __future__ import annotations

import pandas as pd

from src.analytics import aggregate_state, cagr, credit_gap, yoy_growth


def sample_state_data() -> pd.DataFrame:
    """Return a compact state-level fixture."""
    return pd.DataFrame(
        {
            "year": [2023, 2024, 2023, 2024],
            "state": ["A", "A", "B", "B"],
            "region": ["North", "North", "South", "South"],
            "state_code": ["IN-A", "IN-A", "IN-B", "IN-B"],
            "bank_type": ["Public", "Public", "Public", "Public"],
            "population_million": [10, 10, 20, 20],
            "deposits_crore": [1000, 1100, 1500, 1650],
            "credit_crore": [600, 720, 800, 760],
            "priority_sector_credit_crore": [250, 300, 320, 330],
            "gdp_proxy_crore": [5000, 5500, 7000, 7700],
            "expected_credit_crore": [650, 700, 900, 920],
        }
    )


def test_yoy_growth_calculates_percent_change() -> None:
    """YoY growth should be grouped by state."""
    result = yoy_growth(sample_state_data(), ["state"], "credit_crore")
    value = result[(result["state"] == "A") & (result["year"] == 2024)]["credit_crore_yoy_growth"].iloc[0]
    assert round(value, 2) == 20.0


def test_credit_gap_adds_rank_and_opportunity() -> None:
    """Credit gap should create positive opportunity metrics."""
    latest = aggregate_state(sample_state_data())
    latest = latest[latest["year"] == 2024]
    result = credit_gap(latest)
    assert {"credit_gap_crore", "gap_pct", "opportunity_index", "gap_rank"}.issubset(result.columns)
    assert result["gap_rank"].min() == 1


def test_cagr_handles_valid_and_invalid_inputs() -> None:
    """CAGR should be stable for normal and zero inputs."""
    assert round(cagr(100, 121, 2), 2) == 10.0
    assert cagr(0, 121, 2) == 0.0

