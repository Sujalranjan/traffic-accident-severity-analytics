"""
Simple grid-based hotspot analysis for collision points.

Groups nearby accidents into fixed-size grid cells and computes
``accident_count`` and a normalized ``hotspot_score`` suitable for
downstream data-mart and dashboard consumption.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
from shapely.geometry import Point
from sqlalchemy import text
from sqlalchemy.engine import Engine

from geospatial.coordinates import prepare_coordinate_columns, validate_coordinates_batch
from geospatial.db import get_engine
from geospatial.geometry_builder import point_to_ewkt

DEFAULT_GRID_SIZE_DEG = 0.01
HOTSPOT_TABLE = "spatial_hotspot_grid"


def snap_to_grid(value: float, grid_size_deg: float) -> float:
    """Snap one coordinate to the nearest grid line."""
    return round(value / grid_size_deg) * grid_size_deg


def make_grid_cell_id(grid_lon: float, grid_lat: float) -> str:
    """Create a stable identifier for a grid cell centroid."""
    return f"{grid_lon:.6f}_{grid_lat:.6f}"


def compute_hotspot_grid(
    df: pd.DataFrame,
    *,
    grid_size_deg: float = DEFAULT_GRID_SIZE_DEG,
) -> pd.DataFrame:
    """
    Compute hotspot cells from validated collision coordinates.

    This function works on a DataFrame and does not require PostgreSQL,
    which makes it easy to test and reuse in batch jobs.
    """
    valid_df, _ = validate_coordinates_batch(df)
    if valid_df.empty:
        return pd.DataFrame(
            columns=[
                "grid_cell_id",
                "grid_lon",
                "grid_lat",
                "latitude",
                "longitude",
                "accident_count",
                "hotspot_score",
                "ewkt",
            ]
        )

    working = valid_df.copy()
    working["grid_lon"] = working["longitude"].map(
        lambda value: snap_to_grid(float(value), grid_size_deg)
    )
    working["grid_lat"] = working["latitude"].map(
        lambda value: snap_to_grid(float(value), grid_size_deg)
    )
    working["grid_cell_id"] = working.apply(
        lambda row: make_grid_cell_id(row["grid_lon"], row["grid_lat"]),
        axis=1,
    )

    grouped = (
        working.groupby(["grid_cell_id", "grid_lon", "grid_lat"], as_index=False)
        .size()
        .rename(columns={"size": "accident_count"})
    )

    max_count = grouped["accident_count"].max()
    if max_count and max_count > 0:
        grouped["hotspot_score"] = grouped["accident_count"] / max_count
    else:
        grouped["hotspot_score"] = 0.0

    grouped["latitude"] = grouped["grid_lat"]
    grouped["longitude"] = grouped["grid_lon"]
    grouped["ewkt"] = grouped.apply(
        lambda row: point_to_ewkt(Point(row["grid_lon"], row["grid_lat"])),
        axis=1,
    )
    grouped["computed_at"] = datetime.now(timezone.utc).isoformat()
    return grouped.sort_values("accident_count", ascending=False).reset_index(drop=True)


def build_hotspot_grid_sql(grid_size_deg: float = DEFAULT_GRID_SIZE_DEG) -> str:
    """
    Return SQL that aggregates collision geometries into hotspot grid cells.

    Intended for execution after 1CR23AI129 loads ``collisions.geom``.
    """
    return f"""
        WITH snapped AS (
            SELECT
                c.collision_index,
                ST_SnapToGrid(c.geom, :grid_size_deg) AS cell_geom
            FROM collisions AS c
            WHERE c.geom IS NOT NULL
        ),
        aggregated AS (
            SELECT
                cell_geom,
                COUNT(*) AS accident_count,
                ST_X(cell_geom) AS grid_lon,
                ST_Y(cell_geom) AS grid_lat
            FROM snapped
            GROUP BY cell_geom
        )
        SELECT
            CONCAT(
                ROUND(grid_lon::numeric, 6),
                '_',
                ROUND(grid_lat::numeric, 6)
            ) AS grid_cell_id,
            grid_lon,
            grid_lat,
            grid_lat AS latitude,
            grid_lon AS longitude,
            cell_geom AS geom,
            accident_count,
            CASE
                WHEN MAX(accident_count) OVER () = 0 THEN 0
                ELSE accident_count::float / MAX(accident_count) OVER ()
            END AS hotspot_score,
            NOW() AS computed_at
        FROM aggregated
        ORDER BY accident_count DESC
    """


def create_hotspot_table_sql() -> str:
    """
    SQL contract for 1CR23AI129: optional hotspot table owned by the
    geospatial layer and separate from the base relational schema.
    """
    return f"""
        CREATE TABLE IF NOT EXISTS {HOTSPOT_TABLE} (
            grid_cell_id   TEXT PRIMARY KEY,
            grid_lon       DOUBLE PRECISION NOT NULL,
            grid_lat       DOUBLE PRECISION NOT NULL,
            geom           geometry(Point, 4326),
            accident_count INTEGER NOT NULL,
            hotspot_score  DOUBLE PRECISION NOT NULL,
            computed_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
    """


def refresh_hotspot_grid_sql() -> str:
    """Replace hotspot grid contents with a fresh aggregation.

    ``build_hotspot_grid_sql()`` also exposes ``latitude`` / ``longitude``
    aliases for analysis consumers. Those aliases are not table columns, so
    the INSERT projects only the ``spatial_hotspot_grid`` contract.
    """
    return f"""
        TRUNCATE TABLE {HOTSPOT_TABLE};

        INSERT INTO {HOTSPOT_TABLE} (
            grid_cell_id,
            grid_lon,
            grid_lat,
            geom,
            accident_count,
            hotspot_score,
            computed_at
        )
        SELECT
            grid_cell_id,
            grid_lon,
            grid_lat,
            geom,
            accident_count,
            hotspot_score,
            computed_at
        FROM (
            {build_hotspot_grid_sql()}
        ) AS hotspot_source
    """


def refresh_hotspot_grid(
    *,
    engine: Engine | None = None,
    grid_size_deg: float = DEFAULT_GRID_SIZE_DEG,
) -> dict[str, int | float]:
    """
    Refresh the ``spatial_hotspot_grid`` table in PostgreSQL.

    Requires the hotspot table and populated ``collisions.geom`` column
    described in ``sql/geospatial/schema_contract.sql``.
    """
    active_engine = engine or get_engine()
    refresh_sql = refresh_hotspot_grid_sql()

    with active_engine.begin() as connection:
        connection.execute(text(refresh_sql), {"grid_size_deg": grid_size_deg})
        summary = connection.execute(
            text(
                f"""
                SELECT
                    COUNT(*) AS grid_cells,
                    COALESCE(SUM(accident_count), 0) AS total_accidents_mapped,
                    COALESCE(MAX(accident_count), 0) AS max_accident_count
                FROM {HOTSPOT_TABLE}
                """
            )
        ).mappings().one()

    return {
        "grid_cells": int(summary["grid_cells"]),
        "total_accidents_mapped": int(summary["total_accidents_mapped"]),
        "max_accident_count": int(summary["max_accident_count"]),
    }


def compute_hotspot_grid_from_csv(
    csv_path: str,
    *,
    grid_size_deg: float = DEFAULT_GRID_SIZE_DEG,
) -> pd.DataFrame:
    """
    Convenience wrapper for offline hotspot analysis from a collision CSV.
    """
    df = pd.read_csv(csv_path, low_memory=False)
    prepared = prepare_coordinate_columns(df)
    return compute_hotspot_grid(prepared, grid_size_deg=grid_size_deg)
