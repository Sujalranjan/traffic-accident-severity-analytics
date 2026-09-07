"""Tests for spatial query SQL helpers."""

from __future__ import annotations

import pytest

from geospatial.spatial_queries import (
    BoundingBox,
    bounding_box_query_sql,
    build_bbox_from_center,
    hotspot_bbox_query_sql,
    radius_query_sql,
)


def test_build_bbox_from_center():
    bbox = build_bbox_from_center(-2.0, 53.0, buffer_deg=0.5)

    assert bbox.min_lon == pytest.approx(-2.5)
    assert bbox.max_lon == pytest.approx(-1.5)
    assert bbox.min_lat == pytest.approx(52.5)
    assert bbox.max_lat == pytest.approx(53.5)


def test_bounding_box_query_sql_uses_postgis_operators():
    sql = bounding_box_query_sql()

    assert "ST_MakeEnvelope" in sql
    assert "&&" in sql
    assert "collisions" in sql


def test_radius_query_sql_uses_st_dwithin():
    sql = radius_query_sql()

    assert "ST_DWithin" in sql
    assert "::geography" in sql
    assert "distance_meters" in sql


def test_hotspot_bbox_query_sql_reads_spatial_hotspot_grid():
    sql = hotspot_bbox_query_sql()

    assert "spatial_hotspot_grid" in sql
    assert "accident_count" in sql
    assert "hotspot_score" in sql


def test_bounding_box_dataclass():
    bbox = BoundingBox(min_lon=-3.0, min_lat=50.0, max_lon=-1.0, max_lat=55.0)

    assert bbox.min_lon == -3.0
    assert bbox.max_lat == 55.0
