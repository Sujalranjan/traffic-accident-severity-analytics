"""
weather_cache.py
------------------
Many accidents share the same (rounded lat/lon, date) — e.g. multiple
accidents in the same city on the same day. Calling Open-Meteo once per
accident would be wasteful and slow (and risks hitting rate limits).

This module caches API responses on disk, keyed by a rounded
(lat, lon, date) tuple, so re-running the pipeline doesn't re-fetch
data that's already been retrieved.
"""

import os
import json
import hashlib

CACHE_DIR = os.path.join("data", "raw", "weather_cache")


def _cache_key(latitude: float, longitude: float, date: str, precision: int = 2) -> str:
    """
    Build a stable cache key. Coordinates are rounded to `precision`
    decimal places (~1km at precision=2) so nearby accidents on the
    same day reuse the same cached weather call.
    """
    lat_r = round(latitude, precision)
    lon_r = round(longitude, precision)
    raw_key = f"{lat_r}_{lon_r}_{date}"
    return hashlib.md5(raw_key.encode()).hexdigest()


def get_cached(latitude: float, longitude: float, date: str) -> dict | None:
    os.makedirs(CACHE_DIR, exist_ok=True)
    key = _cache_key(latitude, longitude, date)
    path = os.path.join(CACHE_DIR, f"{key}.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None


def set_cached(latitude: float, longitude: float, date: str, data: dict) -> None:
    os.makedirs(CACHE_DIR, exist_ok=True)
    key = _cache_key(latitude, longitude, date)
    path = os.path.join(CACHE_DIR, f"{key}.json")
    with open(path, "w") as f:
        json.dump(data, f)