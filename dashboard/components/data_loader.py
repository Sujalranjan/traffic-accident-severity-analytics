import os

import pandas as pd
from sqlalchemy import create_engine, text


def get_database_url():
    """
    Build the PostgreSQL connection URL from the project's
    environment variables.
    """

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

    return (
        f"postgresql+psycopg2://{user}"
        f"@{host}:{port}/{database}"
    )


def load_accident_data(query: str) -> pd.DataFrame:
    """
    Load dashboard data from the PostgreSQL analytical layer.

    Parameters:
        query: SQL query used to retrieve dashboard data.

    Returns:
        Pandas DataFrame containing the requested data.
    """

    if not query or not query.strip():
        raise ValueError(
            "A SQL query is required to load dashboard data."
        )

    database_url = get_database_url()

    try:
        engine = create_engine(database_url)

        with engine.connect() as connection:
            df = pd.read_sql(
                text(query),
                connection
            )

        return df

    except Exception as exc:
        raise RuntimeError(
            f"Unable to load dashboard data from PostgreSQL: {exc}"
        ) from exc


def validate_map_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare accident data for the dashboard map.

    Rows without valid latitude or longitude values
    are removed.
    """

    required_columns = {
        "latitude",
        "longitude",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            "Map data is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    map_df = df.copy()

    map_df["latitude"] = pd.to_numeric(
        map_df["latitude"],
        errors="coerce"
    )

    map_df["longitude"] = pd.to_numeric(
        map_df["longitude"],
        errors="coerce"
    )

    map_df = map_df.dropna(
        subset=[
            "latitude",
            "longitude",
        ]
    )

    map_df = map_df[
        map_df["latitude"].between(-90, 90)
        & map_df["longitude"].between(-180, 180)
    ]

    return map_df