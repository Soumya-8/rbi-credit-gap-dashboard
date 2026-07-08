"""SQLite database utilities with a migration-friendly boundary."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from config import DATABASE_URL, PROCESSED_DATA_DIR


def get_engine(database_url: str = DATABASE_URL) -> Engine:
    """Create a SQLAlchemy engine."""
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    return create_engine(database_url, future=True)


def initialize_database(
    state_df: pd.DataFrame,
    sector_df: pd.DataFrame,
    deposit_df: pd.DataFrame,
    database_url: str = DATABASE_URL,
) -> Path:
    """Persist dashboard dataframes into SQLite tables."""
    engine = get_engine(database_url)
    state_df.to_sql("state_data", engine, if_exists="replace", index=False)
    sector_df.to_sql("sector_data", engine, if_exists="replace", index=False)
    deposit_df.to_sql("deposit_data", engine, if_exists="replace", index=False)
    state_df.to_sql("credit_data", engine, if_exists="replace", index=False)
    return Path(database_url.replace("sqlite:///", ""))


def read_table(table_name: str, database_url: str = DATABASE_URL) -> pd.DataFrame:
    """Read a table from the configured database."""
    engine = get_engine(database_url)
    with engine.connect() as connection:
        return pd.read_sql(text(f"SELECT * FROM {table_name}"), connection)

