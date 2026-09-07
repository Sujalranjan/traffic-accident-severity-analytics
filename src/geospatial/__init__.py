"""PostGIS and geospatial processing for traffic accident analytics."""

from geospatial.coordinates import (
    CoordinateValidationResult,
    prepare_coordinate_columns,
    summarize_coordinate_validation,
    validate_coordinates,
    validate_coordinates_batch,
)
from geospatial.geometry_builder import (
    build_geometries_batch,
    build_geometry_from_row,
    build_point_wgs84,
    geometries_to_geodataframe,
    point_to_ewkt,
)
from geospatial.hotspot_analysis import (
    compute_hotspot_grid,
    compute_hotspot_grid_from_csv,
    create_hotspot_table_sql,
    refresh_hotspot_grid,
    snap_to_grid,
)
from geospatial.spatial_queries import (
    BoundingBox,
    build_bbox_from_center,
    query_by_bounding_box,
    query_hotspot_cells_in_bbox,
    query_within_radius,
)

__all__ = [
    "BoundingBox",
    "CoordinateValidationResult",
    "build_bbox_from_center",
    "build_geometries_batch",
    "build_geometry_from_row",
    "build_point_wgs84",
    "compute_hotspot_grid",
    "compute_hotspot_grid_from_csv",
    "create_hotspot_table_sql",
    "geometries_to_geodataframe",
    "point_to_ewkt",
    "prepare_coordinate_columns",
    "query_by_bounding_box",
    "query_hotspot_cells_in_bbox",
    "query_within_radius",
    "refresh_hotspot_grid",
    "snap_to_grid",
    "summarize_coordinate_validation",
    "validate_coordinates",
    "validate_coordinates_batch",
]
