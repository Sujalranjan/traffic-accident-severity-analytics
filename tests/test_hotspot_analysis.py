"""Tests for hotspot grid analysis."""

from __future__ import annotations

import pytest

from geospatial.hotspot_analysis import (
    compute_hotspot_grid,
    create_hotspot_table_sql,
    refresh_hotspot_grid_sql,
    snap_to_grid,
)


def test_snap_to_grid_rounds_to_nearest_cell():
    assert snap_to_grid(53.4808, 0.01) == pytest.approx(53.48)
    assert snap_to_grid(-2.2426, 0.01) == pytest.approx(-2.24)


def test_compute_hotspot_grid_counts_clustered_accidents(hotspot_cluster_df):
    hotspots = compute_hotspot_grid(hotspot_cluster_df, grid_size_deg=0.01)

    assert len(hotspots) == 2
    top_cell = hotspots.iloc[0]
    assert top_cell["accident_count"] == 3
    assert top_cell["hotspot_score"] == pytest.approx(1.0)
    assert top_cell["latitude"] == top_cell["grid_lat"]
    assert top_cell["longitude"] == top_cell["grid_lon"]


def test_compute_hotspot_grid_returns_empty_for_invalid_input():
    import pandas as pd

    df = pd.DataFrame(
        {
            "collision_index": ["X1"],
            "latitude": [None],
            "longitude": [None],
        }
    )

    hotspots = compute_hotspot_grid(df)

    assert hotspots.empty


def test_hotspot_score_is_normalized_between_zero_and_one(hotspot_cluster_df):
    hotspots = compute_hotspot_grid(hotspot_cluster_df, grid_size_deg=0.01)

    assert hotspots["hotspot_score"].min() >= 0.0
    assert hotspots["hotspot_score"].max() == pytest.approx(1.0)
    assert hotspots.loc[hotspots["accident_count"] == 1, "hotspot_score"].iloc[0] == pytest.approx(1 / 3)


def test_refresh_hotspot_grid_sql_insert_matches_table_columns():
    """INSERT must not consume latitude/longitude aliases from the source query."""
    from geospatial.hotspot_analysis import build_hotspot_grid_sql

    source_sql = build_hotspot_grid_sql()
    refresh_sql = refresh_hotspot_grid_sql()
    table_sql = create_hotspot_table_sql()

    assert "grid_lat AS latitude" in source_sql
    assert "grid_lon AS longitude" in source_sql
    assert "latitude" not in table_sql
    assert "longitude" not in table_sql

    insert_section = refresh_sql[refresh_sql.index("INSERT INTO") :]
    projected = insert_section.split("SELECT", 1)[1].split("FROM", 1)[0]
    assert "latitude" not in projected
    assert "longitude" not in projected
    for column in (
        "grid_cell_id",
        "grid_lon",
        "grid_lat",
        "geom",
        "accident_count",
        "hotspot_score",
        "computed_at",
    ):
        assert column in projected
