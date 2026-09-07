"""Tests for coordinate validation."""

from __future__ import annotations

import pandas as pd
import pytest

from geospatial.coordinates import (
    prepare_coordinate_columns,
    summarize_coordinate_validation,
    validate_coordinates,
    validate_coordinates_batch,
)


def test_prepare_coordinate_columns_converts_strings():
    df = pd.DataFrame(
        {
            "collision_index": ["A1"],
            "latitude": ["51.5"],
            "longitude": ["-0.12"],
        }
    )

    prepared = prepare_coordinate_columns(df)

    assert prepared.loc[0, "latitude"] == pytest.approx(51.5)
    assert prepared.loc[0, "longitude"] == pytest.approx(-0.12)


def test_validate_coordinates_accepts_valid_point():
    row = pd.Series(
        {
            "collision_index": "C1",
            "latitude": 51.5074,
            "longitude": -0.1278,
        }
    )

    result = validate_coordinates(row)

    assert result.is_valid is True
    assert result.rejection_reason is None


def test_validate_coordinates_rejects_missing_coordinates():
    row = pd.Series(
        {
            "collision_index": "C3",
            "latitude": None,
            "longitude": -2.2426,
        }
    )

    result = validate_coordinates(row)

    assert result.is_valid is False
    assert result.rejection_reason == "missing_coordinates"


def test_validate_coordinates_rejects_invalid_latitude():
    row = pd.Series(
        {
            "collision_index": "C4",
            "latitude": 95.0,
            "longitude": -1.0,
        }
    )

    result = validate_coordinates(row)

    assert result.is_valid is False
    assert result.rejection_reason == "latitude_out_of_range"


def test_validate_coordinates_rejects_invalid_longitude():
    row = pd.Series(
        {
            "collision_index": "C6",
            "latitude": 51.0,
            "longitude": 200.0,
        }
    )

    result = validate_coordinates(row)

    assert result.is_valid is False
    assert result.rejection_reason == "longitude_out_of_range"


def test_validate_coordinates_batch_preserves_rejected_rows(sample_collisions_df):
    valid_df, rejected_df = validate_coordinates_batch(sample_collisions_df)

    assert len(valid_df) == 3
    assert len(rejected_df) == 2
    assert set(rejected_df["rejection_reason"]) == {
        "missing_coordinates",
        "latitude_out_of_range",
    }


def test_summarize_coordinate_validation(sample_collisions_df):
    summary = summarize_coordinate_validation(sample_collisions_df)

    assert summary["rows_processed"] == 5
    assert summary["valid_rows"] == 3
    assert summary["rejected_rows"] == 2
