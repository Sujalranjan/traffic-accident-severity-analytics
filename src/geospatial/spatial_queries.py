"""
Reusable PostGIS spatial query helpers.

These functions assume the base ``collisions`` table and optional
``spatial_hotspot_grid`` table described in ``sql/geospatial/``.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from geospatial.db import get_engine

COLLISIONS_TABLE = "collisions"
HOTSPOT_TABLE = "spatial_hotspot_grid"


@dataclass(frozen=True)
class BoundingBox:
    """Geographic bounding box in WGS84 decimal degrees."""

    min_lon: float
    min_lat: float
    max_lon: float
    max_lat: float


def build_bbox_from_center(
    center_lon: float,
    center_lat: float,
    buffer_deg: float,
) -> BoundingBox:
    """Build a square bounding box around a center point."""
    return BoundingBox(
        min_lon=center_lon - buffer_deg,
        min_lat=center_lat - buffer_deg,
        max_lon=center_lon + buffer_deg,
        max_lat=center_lat + buffer_deg,
    )


def bounding_box_query_sql() -> str:
    """
    Return SQL for accidents inside a bounding box.

    Uses the ``&&`` operator so a GIST index on ``geom`` can be used.
    """
    return f"""
        SELECT
            c.collision_index,
            c.latitude,
            c.longitude,
            c.collision_severity,
            c.collision_year,
            c.road_type,
            c.weather_conditions,
            c.urban_or_rural_area,
            c.number_of_casualties,
            c.number_of_vehicles,
            ST_X(c.geom) AS geom_lon,
            ST_Y(c.geom) AS geom_lat
        FROM {COLLISIONS_TABLE} AS c
        WHERE c.geom IS NOT NULL
          AND c.geom && ST_MakeEnvelope(
                :min_lon, :min_lat, :max_lon, :max_lat, 4326
          )
        ORDER BY c.collision_index
        LIMIT :limit
    """


def radius_query_sql() -> str:
    """
    Return SQL for accidents within a radius in meters.

    Uses geography casts so distance is measured in meters on the spheroid.
    """
    return f"""
        SELECT
            c.collision_index,
            c.latitude,
            c.longitude,
            c.collision_severity,
            c.collision_year,
            c.road_type,
            c.weather_conditions,
            c.urban_or_rural_area,
            c.number_of_casualties,
            c.number_of_vehicles,
            ST_Distance(
                c.geom::geography,
                ST_SetSRID(ST_MakePoint(:center_lon, :center_lat), 4326)::geography
            ) AS distance_meters
        FROM {COLLISIONS_TABLE} AS c
        WHERE c.geom IS NOT NULL
          AND ST_DWithin(
                c.geom::geography,
                ST_SetSRID(ST_MakePoint(:center_lon, :center_lat), 4326)::geography,
                :radius_meters
          )
        ORDER BY distance_meters
        LIMIT :limit
    """


def hotspot_bbox_query_sql() -> str:
    """Return SQL for hotspot grid cells inside a bounding box."""
    return f"""
        SELECT
            h.grid_cell_id,
            h.grid_lat AS latitude,
            h.grid_lon AS longitude,
            h.accident_count,
            h.hotspot_score
        FROM {HOTSPOT_TABLE} AS h
        WHERE h.geom IS NOT NULL
          AND h.geom && ST_MakeEnvelope(
                :min_lon, :min_lat, :max_lon, :max_lat, 4326
          )
          AND h.accident_count >= :min_accident_count
        ORDER BY h.accident_count DESC
        LIMIT :limit
    """


def query_by_bounding_box(
    bbox: BoundingBox,
    *,
    engine: Engine | None = None,
    limit: int | None = None,
) -> pd.DataFrame:
    """Fetch collision records whose geometry intersects a bounding box."""
    active_engine = engine or get_engine()
    params = {
        "min_lon": bbox.min_lon,
        "min_lat": bbox.min_lat,
        "max_lon": bbox.max_lon,
        "max_lat": bbox.max_lat,
        "limit": limit if limit is not None else 10_000,
    }

    with active_engine.connect() as connection:
        return pd.read_sql(text(bounding_box_query_sql()), connection, params=params)


def query_within_radius(
    center_lon: float,
    center_lat: float,
    radius_meters: float,
    *,
    engine: Engine | None = None,
    limit: int | None = None,
) -> pd.DataFrame:
    """Fetch collision records within a radius of a center point."""
    active_engine = engine or get_engine()
    params = {
        "center_lon": center_lon,
        "center_lat": center_lat,
        "radius_meters": radius_meters,
        "limit": limit if limit is not None else 10_000,
    }

    with active_engine.connect() as connection:
        return pd.read_sql(text(radius_query_sql()), connection, params=params)


def query_hotspot_cells_in_bbox(
    bbox: BoundingBox,
    *,
    engine: Engine | None = None,
    min_accident_count: int = 1,
    limit: int | None = None,
) -> pd.DataFrame:
    """Fetch hotspot grid cells inside a bounding box."""
    active_engine = engine or get_engine()
    params = {
        "min_lon": bbox.min_lon,
        "min_lat": bbox.min_lat,
        "max_lon": bbox.max_lon,
        "max_lat": bbox.max_lat,
        "min_accident_count": min_accident_count,
        "limit": limit if limit is not None else 10_000,
    }

    with active_engine.connect() as connection:
        return pd.read_sql(text(hotspot_bbox_query_sql()), connection, params=params)
