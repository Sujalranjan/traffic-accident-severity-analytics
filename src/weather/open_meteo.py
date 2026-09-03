"""
open_meteo.py
--------------
Thin client around the Open-Meteo API (https://open-meteo.com/).

Two endpoints are used:
- Archive API  -> historical weather for past accident dates
- Forecast API -> only relevant if you ever need "current" conditions

No API key is required for Open-Meteo, which is why the assignment
suggests it as the weather source.
"""

import time
import logging
import requests
from datetime import datetime

logger = logging.getLogger("open_meteo")

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

# Variables we care about for accident-severity analysis
HOURLY_VARS = [
    "temperature_2m",
    "precipitation",
    "rain",
    "snowfall",
    "windspeed_10m",
    "weathercode",
]


class OpenMeteoError(Exception):
    pass


def fetch_historical_weather(latitude: float, longitude: float, date: str,
                              max_retries: int = 3, backoff: float = 2.0) -> dict:
    """
    Fetch hourly historical weather for a single lat/lon/date.

    Parameters
    ----------
    latitude, longitude : float
        Accident location.
    date : str
        'YYYY-MM-DD' — Open-Meteo archive API takes a start/end date range,
        we use the same day for both since we only need one day.
    max_retries : int
        Number of retry attempts on transient failures.
    backoff : float
        Seconds to wait between retries (multiplied by attempt number).

    Returns
    -------
    dict : raw JSON response from Open-Meteo, or raises OpenMeteoError.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": date,
        "end_date": date,
        "hourly": ",".join(HOURLY_VARS),
        "timezone": "auto",
    }

    last_exception = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(ARCHIVE_URL, params=params, timeout=15)
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 429:
                # rate limited — back off and retry
                logger.warning("Rate limited by Open-Meteo, attempt %s", attempt)
                time.sleep(backoff * attempt)
                continue
            else:
                raise OpenMeteoError(
                    f"Open-Meteo returned status {resp.status_code}: {resp.text[:200]}"
                )
        except requests.exceptions.RequestException as e:
            last_exception = e
            logger.warning("Request failed (attempt %s/%s): %s", attempt, max_retries, e)
            time.sleep(backoff * attempt)

    raise OpenMeteoError(
        f"Failed to fetch weather for ({latitude},{longitude}) on {date} "
        f"after {max_retries} attempts. Last error: {last_exception}"
    )


def extract_hour_slice(weather_json: dict, hour: int) -> dict:
    """
    Given a full-day hourly response from fetch_historical_weather,
    pull out the single hour that matches the accident time.

    Parameters
    ----------
    weather_json : dict
        Response from fetch_historical_weather.
    hour : int
        0-23, the hour of the accident.

    Returns
    -------
    dict of variable_name -> value for that hour, or all-None if missing.
    """
    hourly = weather_json.get("hourly", {})
    times = hourly.get("time", [])

    if not times or hour >= len(times):
        return {var: None for var in HOURLY_VARS}

    result = {}
    for var in HOURLY_VARS:
        values = hourly.get(var, [])
        result[var] = values[hour] if hour < len(values) else None
    return result