"""Data loading helpers for the Streamlit dashboard."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Literal

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV_PATH = PROJECT_ROOT / "data" / "processed" / "dashboard_analytics.csv"
DEFAULT_DB_TABLE = "analytics.dashboard_analytics"
Source = Literal["auto", "csv", "database"]


def configured_csv_path() -> Path:
    """Return the dashboard CSV path from env or the project default."""

    configured = Path(
        os.getenv("DASHBOARD_ANALYTICS_CSV", str(DEFAULT_CSV_PATH))
    ).expanduser()
    if configured.is_absolute():
        return configured
    return PROJECT_ROOT / configured


def load_dashboard_data(source: Source = "auto") -> tuple[pd.DataFrame, str]:
    """Load mart-ready dashboard data from CSV or PostgreSQL."""

    csv_path = configured_csv_path()
    database_url = os.getenv("DATABASE_URL")

    if source == "csv" or (source == "auto" and csv_path.exists()):
        if not csv_path.exists():
            raise FileNotFoundError(f"Dashboard analytics CSV not found: {csv_path}")
        return pd.read_csv(csv_path), f"CSV: {csv_path}"

    if source == "database" or (source == "auto" and database_url):
        if not database_url:
            raise ValueError("DATABASE_URL is required when dashboard source is database")
        table_name = os.getenv("DASHBOARD_ANALYTICS_TABLE", DEFAULT_DB_TABLE)
        return _load_database_table(database_url, table_name), f"Database table: {table_name}"

    raise FileNotFoundError(
        "No dashboard analytics data found. Expected "
        f"{csv_path} or DATABASE_URL with DASHBOARD_ANALYTICS_TABLE."
    )


def _load_database_table(database_url: str, table_name: str) -> pd.DataFrame:
    from sqlalchemy import create_engine, text

    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)?", table_name):
        raise ValueError("DASHBOARD_ANALYTICS_TABLE must be schema.table or table")

    identifier = ".".join(f'"{part}"' for part in table_name.split("."))
    engine = create_engine(database_url)
    with engine.connect() as connection:
        return pd.read_sql_query(text(f"SELECT * FROM {identifier}"), connection)
