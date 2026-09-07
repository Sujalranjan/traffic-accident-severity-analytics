"""
Build WGS84 point geometries from validated collision coordinates.

Uses Shapely and GeoPandas for reusable geometry creation that can be
called from batch jobs or later Airflow tasks.
"""

from __future__ import annotations

import pandas as pd
from shapely.geometry import Point

from geospatial.coordinates import validate_coordinates, validate_coordinates_batch

EPSG_WGS84 = "EPSG:4326"


def build_point_wgs84(longitude: float, latitude: float) -> Point:
    """
    Create a Shapely Point in WGS84 order: X=longitude, Y=latitude.
    """
    return Point(longitude, latitude)


def point_to_ewkt(point: Point, srid: int = 4326) -> str:
    """Convert a Shapely point to EWKT for PostGIS insertion."""
    if point.is_empty:
        raise ValueError("Cannot convert an empty point to EWKT.")
    return f"SRID={srid};POINT({point.x} {point.y})"


def build_geometry_from_row(row: pd.Series) -> dict:
    """
    Build geometry metadata for one collision row.

    Returns a dictionary safe for downstream loaders. Invalid rows keep
    their source data but receive ``geometry=None``.
    """
    validation = validate_coordinates(row)

    if not validation.is_valid:
        return {
            "collision_index": validation.collision_index,
            "latitude": validation.latitude,
            "longitude": validation.longitude,
            "geometry": None,
            "ewkt": None,
            "is_valid_geometry": False,
            "rejection_reason": validation.rejection_reason,
        }

    point = build_point_wgs84(validation.longitude, validation.latitude)
    return {
        "collision_index": validation.collision_index,
        "latitude": validation.latitude,
        "longitude": validation.longitude,
        "geometry": point,
        "ewkt": point_to_ewkt(point),
        "is_valid_geometry": True,
        "rejection_reason": None,
    }


def build_geometries_batch(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Attach geometry objects to valid rows and flag invalid rows separately.

    Returns:
        valid_geometries: rows with Shapely Point and EWKT values
        invalid_geometries: rows that could not produce a geometry
    """
    valid_df, rejected_df = validate_coordinates_batch(df)

    if valid_df.empty:
        empty = df.iloc[0:0].copy()
        return empty, rejected_df

    geometry_rows: list[dict] = []
    for _, row in valid_df.iterrows():
        built = build_geometry_from_row(row)
        geometry_rows.append(
            {
                **row.to_dict(),
                "geometry": built["geometry"],
                "ewkt": built["ewkt"],
                "is_valid_geometry": built["is_valid_geometry"],
            }
        )

    valid_geometries = pd.DataFrame(geometry_rows)

    if not valid_geometries.empty:
        try:
            import geopandas as gpd

            valid_geometries = gpd.GeoDataFrame(
                valid_geometries,
                geometry="geometry",
                crs=EPSG_WGS84,
            )
        except ImportError:
            pass

    return valid_geometries, rejected_df


def geometries_to_geodataframe(df: pd.DataFrame):
    """
    Convert a geometry batch result into a GeoDataFrame when GeoPandas
    is available. Raises ImportError if GeoPandas is not installed.
    """
    import geopandas as gpd

    if "geometry" not in df.columns:
        raise ValueError("DataFrame must contain a 'geometry' column.")

    return gpd.GeoDataFrame(df.copy(), geometry="geometry", crs=EPSG_WGS84)
