"""Shared utility helpers."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable

import pandas as pd


def configure_logging() -> None:
    """Configure concise application logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def ensure_directories(paths: Iterable[Path]) -> None:
    """Create directories if they do not already exist."""
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def format_inr_crore(value: float) -> str:
    """Format a numeric value as Indian rupees in crore."""
    if pd.isna(value):
        return "NA"
    if abs(value) >= 100000:
        return f"Rs {value / 100000:.2f} lakh cr"
    if abs(value) >= 1000:
        return f"Rs {value / 1000:.2f}k cr"
    return f"Rs {value:,.0f} cr"


def to_csv_download(df: pd.DataFrame) -> bytes:
    """Return a dataframe as UTF-8 CSV bytes."""
    return df.to_csv(index=False).encode("utf-8")


def normalize_selection(selection: list[str], all_label: str = "All") -> list[str] | None:
    """Convert a UI multi-select into an optional filter list."""
    if not selection or all_label in selection:
        return None
    return selection

