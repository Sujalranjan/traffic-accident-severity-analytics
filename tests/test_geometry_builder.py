"""Tests for geometry creation."""

from __future__ import annotations

import pandas as pd
import pytest

from geospatial.geometry_builder import (
    build_geometries_batch,
    build_geometry_from_row,
    build_point_wgs84,
    point_to_ewkt,
)


def test_build_point_wgs84_uses_longitude_first():
    point = build_point_wgs84(-0.1278, 51.5074)

    assert point.x == pytest.approx(-0.1278)
    assert point.y == pytest.approx(51.5074)


def test_point_to_ewkt_returns_srid_4326():
    point = build_point_wgs84(-1.8904, 52.4862)

    assert point_to_ewkt(point) == "SRID=4326;POINT(-1.8904 52.4862)"


def test_build_geometry_from_row_for_valid_coordinates():
    row = pd.Series(
        {
            "collision_index": "C1",
            "latitude": 51.5074,
            "longitude": -0.1278,
        }
    )

    built = build_geometry_from_row(row)

    assert built["is_valid_geometry"] is True
    assert built["ewkt"] == "SRID=4326;POINT(-0.1278 51.5074)"
    assert built["geometry"] is not None


def test_build_geometry_from_row_for_missing_coordinates():
    row = pd.Series(
        {
            "collision_index": "C3",
            "latitude": None,
            "longitude": -2.2426,
        }
    )

    built = build_geometry_from_row(row)

    assert built["is_valid_geometry"] is False
    assert built["geometry"] is None
    assert built["rejection_reason"] == "missing_coordinates"


def test_build_geometries_batch_splits_valid_and_invalid(sample_collisions_df):
    valid_df, rejected_df = build_geometries_batch(sample_collisions_df)

    assert len(valid_df) == 3
    assert len(rejected_df) == 2
    assert "ewkt" in valid_df.columns
    assert valid_df["ewkt"].str.startswith("SRID=4326;POINT(").all()
