"""Tests for data loading utilities."""

from __future__ import annotations

import pandas as pd
import pytest

from src.load_data import STATE_SCHEMA, filter_dataframe, validate_schema


def test_validate_schema_reports_missing_columns() -> None:
    """Schema validation should fail clearly."""
    with pytest.raises(ValueError):
        validate_schema(pd.DataFrame({"year": [2024]}), STATE_SCHEMA, "state")


def test_filter_dataframe_applies_year_and_state_filters() -> None:
    """Filters should narrow rows without mutating the source dataframe."""
    df = pd.DataFrame(
        {
            "year": [2023, 2024],
            "state": ["A", "B"],
            "region": ["North", "South"],
            "bank_type": ["Public", "Private"],
        }
    )
    result = filter_dataframe(df, years=(2024, 2024), states=["B"])
    assert len(result) == 1
    assert result.iloc[0]["state"] == "B"

