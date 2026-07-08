"""Project configuration for the RBI Credit Gap Dashboard."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
ASSETS_DIR = PROJECT_ROOT / "assets"
DATABASE_URL = f"sqlite:///{PROCESSED_DATA_DIR / 'rbi_credit_gap.db'}"

APP_TITLE = "RBI Credit Gap Dashboard"
APP_SUBTITLE = "Banking credit, deposits, sector exposure, and opportunity analytics"

DEFAULT_YEAR_RANGE = (2017, 2024)
DEFAULT_FORECAST_HORIZON = 8

THEME_TEMPLATE = "plotly_white"

