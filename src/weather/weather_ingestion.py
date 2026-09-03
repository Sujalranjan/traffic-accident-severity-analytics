"""
weather_ingestion.py
----------------------
Main entry point for weather data integration (USN 1CR23AI123).

Pipeline:
    accident raw data (date, time, lat, lon)
        -> for each unique (lat, lon, date)
        -> Open-Meteo archive API (cached)
        -> extract the hour matching the accident time
        -> write raw_weather layer with extraction metadata

Run:
    python weather_ingestion.py --input data/raw/accidents_raw.csv \
                                 --output data/raw/raw_weather.csv
"""

import argparse
import logging
import sys
from datetime import datetime

import pandas as pd

from open_meteo import fetch_historical_weather, extract_hour_slice, OpenMeteoError
from weather_cache import get_cached, set_cached

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("weather_ingestion")


def load_accidents(path: str) -> pd.DataFrame:
    """
    Load the raw collision dataset produced by 121's accident_ingestion.py.

    UK DfT road-safety data uses these column names (confirmed against
    121's raw collision file):
        collision_index, date, time, latitude, longitude

    'date' is typically DD/MM/YYYY in the DfT export, 'time' is 'HH:MM'.
    """
    df = pd.read_csv(path, low_memory=False)
    required = {"collision_index", "latitude", "longitude", "date", "time"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Collision file is missing required columns: {missing}")

    # Normalize date to ISO (YYYY-MM-DD) since Open-Meteo requires that format.
    df["accident_date_iso"] = pd.to_datetime(
        df["date"], dayfirst=True, errors="coerce"
    ).dt.strftime("%Y-%m-%d")

    bad_dates = df["accident_date_iso"].isna().sum()
    if bad_dates:
        logger.warning("%s rows have unparseable dates and will be skipped", bad_dates)

    return df


def build_unique_requests(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reduce the collision table down to unique (lat, lon, date) combos
    so we call the API the minimum number of times needed.
    """
    subset = df[["latitude", "longitude", "accident_date_iso"]].dropna()
    subset = subset.rename(columns={"accident_date_iso": "accident_date"})
    unique = subset.drop_duplicates().reset_index(drop=True)
    logger.info("Found %s unique (lat, lon, date) combinations to fetch", len(unique))
    return unique


def fetch_all_weather(unique_requests: pd.DataFrame) -> dict:
    """
    Fetch (or load from cache) weather for every unique request.
    Returns a dict keyed by (lat, lon, date) -> full-day weather_json.
    Failures are logged and skipped, not fatal.
    """
    results = {}
    failed = []

    for i, row in unique_requests.iterrows():
        lat, lon, date = row["latitude"], row["longitude"], row["accident_date"]
        key = (lat, lon, date)

        cached = get_cached(lat, lon, date)
        if cached is not None:
            results[key] = cached
            continue

        try:
            data = fetch_historical_weather(lat, lon, date)
            set_cached(lat, lon, date, data)
            results[key] = data
        except OpenMeteoError as e:
            logger.error("Failed to fetch weather for %s: %s", key, e)
            failed.append({"latitude": lat, "longitude": lon, "date": date, "error": str(e)})

        if i % 50 == 0:
            logger.info("Fetched %s / %s", i, len(unique_requests))

    if failed:
        pd.DataFrame(failed).to_csv("data/raw/weather_fetch_failures.csv", index=False)
        logger.warning("%s requests failed — see data/raw/weather_fetch_failures.csv", len(failed))

    return results


def join_weather_to_accidents(df: pd.DataFrame, weather_by_key: dict) -> pd.DataFrame:
    """
    For every accident, pull the specific hour of weather matching its
    accident_time from the full-day weather data already fetched.
    """
    rows = []
    skipped = 0
    for _, r in df.iterrows():
        if pd.isna(r["accident_date_iso"]) or pd.isna(r["latitude"]) or pd.isna(r["longitude"]):
            skipped += 1
            continue

        key = (r["latitude"], r["longitude"], r["accident_date_iso"])
        weather_json = weather_by_key.get(key)

        hour = 0
        try:
            hour = int(str(r["time"]).split(":")[0])
        except (ValueError, IndexError):
            pass

        if weather_json is None:
            weather_vals = {
                "temperature_2m": None, "precipitation": None, "rain": None,
                "snowfall": None, "windspeed_10m": None, "weathercode": None,
            }
        else:
            weather_vals = extract_hour_slice(weather_json, hour)

        row = {
            "collision_index": r["collision_index"],
            "latitude": r["latitude"],
            "longitude": r["longitude"],
            "accident_date": r["accident_date_iso"],
            "accident_time": r["time"],
            **weather_vals,
        }
        rows.append(row)

    if skipped:
        logger.warning("Skipped %s rows with missing date/lat/lon", skipped)

    return pd.DataFrame(rows)


def add_extraction_metadata(df: pd.DataFrame, source_file: str) -> pd.DataFrame:
    """
    The assignment requires recording extraction date, source, status
    and row count for every ingestion step.
    """
    df = df.copy()
    df["extraction_source"] = "open-meteo-archive-api"
    df["extraction_date"] = datetime.utcnow().isoformat()
    df["source_accident_file"] = source_file
    df["status"] = "loaded"
    return df


def main():
    parser = argparse.ArgumentParser(description="Weather data ingestion (Open-Meteo)")
    parser.add_argument("--input", required=True, help="Path to raw accident CSV")
    parser.add_argument("--output", required=True, help="Path to write raw_weather CSV")
    args = parser.parse_args()

    logger.info("Starting weather ingestion")
    accidents = load_accidents(args.input)
    logger.info("Loaded %s accident records", len(accidents))

    unique_requests = build_unique_requests(accidents)
    weather_by_key = fetch_all_weather(unique_requests)

    result = join_weather_to_accidents(accidents, weather_by_key)
    result = add_extraction_metadata(result, args.input)

    result.to_csv(args.output, index=False)
    logger.info("Wrote %s weather-enriched rows to %s", len(result), args.output)
    logger.info("Row count: %s | Source: %s | Status: loaded", len(result), args.input)


if __name__ == "__main__":
    sys.exit(main())