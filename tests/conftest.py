"""Shared pytest fixtures for geospatial tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


@pytest.fixture
def sample_collisions_df() -> pd.DataFrame:
    """Small collision dataset using real UK DfT column names."""
    return pd.DataFrame(
        {
            "collision_index": ["C1", "C2", "C3", "C4", "C5"],
            "latitude": [51.5074, 52.4862, None, 95.0, 53.4808],
            "longitude": [-0.1278, -1.8904, -2.2426, -1.0, -2.2426],
            "collision_severity": [3, 2, 3, 1, 3],
        }
    )


@pytest.fixture
def hotspot_cluster_df() -> pd.DataFrame:
    """Three accidents in one grid cell and one accident elsewhere."""
    return pd.DataFrame(
        {
            "collision_index": ["H1", "H2", "H3", "H4"],
            "latitude": [53.4808, 53.4809, 53.4807, 51.5074],
            "longitude": [-2.2426, -2.2425, -2.2427, -0.1278],
        }
    )
