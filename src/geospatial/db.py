"""
Database connection helpers for the geospatial module.

Connection details are read from environment variables defined in
``.env.example`` and must never be hard-coded.
"""

from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def get_database_url() -> str:
    """Build a PostgreSQL URL from environment variables."""
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    database = os.getenv("POSTGRES_DB", "traffic_analytics")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "")

    if password:
        return (
            f"postgresql+psycopg2://{user}:{password}"
            f"@{host}:{port}/{database}"
        )

    return f"postgresql+psycopg2://{user}@{host}:{port}/{database}"


def get_engine() -> Engine:
    """Create a SQLAlchemy engine for PostGIS queries."""
    return create_engine(get_database_url())
