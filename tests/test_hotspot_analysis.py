"""Tests for hotspot grid analysis."""

from __future__ import annotations

import pytest

from geospatial.hotspot_analysis import compute_hotspot_grid, snap_to_grid


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
