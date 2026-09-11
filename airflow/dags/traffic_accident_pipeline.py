"""
Main Airflow DAG for the Traffic Accident Severity Analytics pipeline
(USN 1CR23AI127 — Apache Airflow Orchestration).

Notes:
- Ingestion (121/126), weather (123), cleaning (124), and post-clean
  validation (126) call real code already in src/. validate_raw_data
  has no upstream equivalent — it's a lightweight sanity check over
  the ingestion log, since real validation only happens post-cleaning.
- load_postgres / load_postgis / analytical_mart are functional
  bridges (129/131 haven't pushed a loader or mart script yet). They
  reuse existing pieces (get_engine, the PostGIS SQL files,
  refresh_hotspot_grid) so the pipeline runs end-to-end today. Swap
  their bodies for 129/131's real code once pushed.
- The repo mixes three import styles: flat sibling imports
  (ingestion/transformation/weather — need that folder on sys.path),
  `geospatial.x` imports (need src/ on sys.path), and `src.x` imports
  (need the repo root on sys.path). _on_path handles this per task.
- The ingestion scripts hard-code each developer's own ~/Downloads
  path as the source CSV. _override_source_file lets an Airflow
  Variable override it without editing their files.
- PROJECT_ROOT is read from the PROJECT_ROOT env var first, falling
  back to the <repo_root>/airflow/dags/... layout for local runs. In
  Docker, only dags/ is normally mounted into the container, so the
  repo root has to be mounted separately with PROJECT_ROOT pointing
  at it — see docker-compose.yaml.

Required env vars: PROJECT_ROOT (Docker only), POSTGRES_HOST,
POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD (read by
src/geospatial/db.py). Optional Airflow Variables: COLLISION_SOURCE_FILE,
VEHICLE_SOURCE_FILE, CASUALTY_SOURCE_FILE, WEATHER_SAMPLE_SIZE (caps how
many accident rows get a weather lookup — see ingest_weather_task; unset
means the full, unsampled dataset).
"""

from __future__ import annotations

import contextlib
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from airflow import DAG
from airflow.exceptions import AirflowException
from airflow.models import Variable
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.utils.trigger_rule import TriggerRule

logger = logging.getLogger("airflow.task")

_env_project_root = os.environ.get("PROJECT_ROOT")
PROJECT_ROOT = Path(_env_project_root) if _env_project_root else Path(__file__).resolve().parents[2]

if not (PROJECT_ROOT / "src").exists():
    raise AirflowException(
        f"PROJECT_ROOT resolved to '{PROJECT_ROOT}' but '{PROJECT_ROOT / 'src'}' doesn't exist. "
        f"If running in Docker, mount the full repo into the container and set the "
        f"PROJECT_ROOT environment variable to that mount path."
    )

SRC_DIR = PROJECT_ROOT / "src"
DATA_DIR = PROJECT_ROOT / "data"
STAGING_DIR = DATA_DIR / "staging"
RAW_DIR = DATA_DIR / "raw"
LOGS_DIR = PROJECT_ROOT / "logs"
REPORT_DIR = PROJECT_ROOT / "reports"
SQL_GEOSPATIAL_DIR = PROJECT_ROOT / "sql" / "geospatial"

RAW_WEATHER_FILE = RAW_DIR / "raw_weather.csv"
RAW_COLLISION_FILE = (
    RAW_DIR / "collisions" / "dft-road-casualty-statistics-collision-last-5-years.csv"
)
INGESTION_LOG_FILE = LOGS_DIR / "ingestion_log.csv"

DASHBOARD_ANALYTICS_CSV = PROJECT_ROOT / os.getenv(
    "DASHBOARD_ANALYTICS_CSV", "data/processed/dashboard_analytics.csv"
)
_dashboard_table_raw = os.getenv("DASHBOARD_ANALYTICS_TABLE", "analytics.dashboard_analytics")
if "." in _dashboard_table_raw:
    DASHBOARD_ANALYTICS_SCHEMA, DASHBOARD_ANALYTICS_TABLE = _dashboard_table_raw.split(".", 1)
else:
    DASHBOARD_ANALYTICS_SCHEMA, DASHBOARD_ANALYTICS_TABLE = None, _dashboard_table_raw


@contextlib.contextmanager
def _on_path(*dirs: Path):
    """Temporarily prepend dirs to sys.path and un-import anything loaded
    from them afterwards, so the three import styles don't collide across
    tasks in the same worker process."""
    added = [str(d.resolve()) for d in dirs if str(d.resolve()) not in sys.path]
    for d in reversed(added):
        sys.path.insert(0, d)
    try:
        yield
    finally:
        for d in added:
            if d in sys.path:
                sys.path.remove(d)
        for mod_name in list(sys.modules):
            mod_file = getattr(sys.modules[mod_name], "__file__", None)
            if mod_file and any(mod_file.startswith(str(d)) for d in dirs):
                del sys.modules[mod_name]


def _override_source_file(module, variable_name: str) -> None:
    """Let an Airflow Variable override a hard-coded ~/Downloads SOURCE_FILE
    without editing the teammate's script."""
    defaults = {
        "COLLISION_SOURCE_FILE": DATA_DIR / "source" / "dft-road-casualty-statistics-collision-last-5-years.csv",
        "VEHICLE_SOURCE_FILE": DATA_DIR / "source" / "dft-road-casualty-statistics-vehicle-last-5-years.csv",
        "CASUALTY_SOURCE_FILE": DATA_DIR / "source" / "dft-road-casualty-statistics-casualty-last-5-years.csv",
    }
    override = Variable.get(variable_name, default_var=str(defaults[variable_name]))
    module.SOURCE_FILE = Path(override)

    if not module.SOURCE_FILE.exists():
        raise AirflowException(
            f"Source file not found: {module.SOURCE_FILE}\n"
            f"Set the Airflow Variable '{variable_name}' to the correct path on this machine."
        )


def ingest_accidents_task(**_):
    # Support both package imports and the flat sibling imports used by the
    # existing ingestion scripts (e.g. ingestion_utils).
    with _on_path(SRC_DIR, SRC_DIR / "ingestion"):
        from ingestion import accident_ingestion as mod
        _override_source_file(mod, "COLLISION_SOURCE_FILE")
        mod.ingest_collision_data()


def ingest_vehicles_task(**_):
    with _on_path(SRC_DIR, SRC_DIR / "ingestion"):
        from ingestion import vehicle_ingestion as mod
        _override_source_file(mod, "VEHICLE_SOURCE_FILE")
        mod.ingest_vehicle_data()


def ingest_casualties_task(**_):
    with _on_path(SRC_DIR, SRC_DIR / "ingestion"):
        from ingestion import casualty_ingestion as mod
        _override_source_file(mod, "CASUALTY_SOURCE_FILE")
        mod.ingest_casualty_data()


def ingest_weather_task(**_):
    # weather_ingestion.py is a CLI script; call its functions directly
    # instead of shelling out, so this task gets proper Airflow logging.
    # Support package imports and any flat imports used by weather_ingestion.py.
    with _on_path(SRC_DIR, SRC_DIR / "weather"):
        from weather import weather_ingestion as mod

        if not RAW_COLLISION_FILE.exists():
            raise AirflowException(
                f"Collision raw file not found for weather join: {RAW_COLLISION_FILE}"
            )

        accidents = mod.load_accidents(str(RAW_COLLISION_FILE))
        logger.info("Loaded %s accident records for weather join", len(accidents))

        # build_unique_requests dedups on exact (lat, lon, date), which barely
        # collapses anything for precise UK collision coordinates — one API
        # call per accident is impractical at full scale (500k+ rows would
        # take ~85 hours sequentially). Set WEATHER_SAMPLE_SIZE for fast
        # iteration; leave it unset for the real, full-scale run.
        sample_size = Variable.get("WEATHER_SAMPLE_SIZE", default_var=None)
        if sample_size:
            sample_size = min(int(sample_size), len(accidents))
            accidents = accidents.sample(n=sample_size, random_state=42)
            logger.info(
                "WEATHER_SAMPLE_SIZE=%s set — sampled down to %s accident records",
                sample_size, len(accidents),
            )

        unique_requests = mod.build_unique_requests(accidents)
        weather_by_key = mod.fetch_all_weather(unique_requests)
        result = mod.join_weather_to_accidents(accidents, weather_by_key)
        result = mod.add_extraction_metadata(result, str(RAW_COLLISION_FILE))

        RAW_WEATHER_FILE.parent.mkdir(parents=True, exist_ok=True)
        result.to_csv(RAW_WEATHER_FILE, index=False)
        logger.info("Wrote %s weather-enriched rows to %s", len(result), RAW_WEATHER_FILE)


def validate_raw_data_task(**_):
    if not INGESTION_LOG_FILE.exists():
        raise AirflowException(f"Ingestion log not found: {INGESTION_LOG_FILE}")

    log_df = pd.read_csv(INGESTION_LOG_FILE)
    latest = log_df.sort_values("extraction_time_utc").groupby("dataset_name").tail(1)

    problems = []
    for dataset in ("collisions", "vehicles", "casualties"):
        row = latest[latest["dataset_name"] == dataset]
        if row.empty:
            problems.append(f"{dataset}: no ingestion log entry found")
            continue
        row = row.iloc[0]
        if row["status"] != "success":
            problems.append(f"{dataset}: last ingestion status was '{row['status']}'")
        elif int(row["row_count"]) <= 0:
            problems.append(f"{dataset}: row_count was {row['row_count']}")

    if not RAW_WEATHER_FILE.exists():
        problems.append(f"weather: output file missing at {RAW_WEATHER_FILE}")
    else:
        weather_rows = sum(1 for _ in open(RAW_WEATHER_FILE)) - 1
        if weather_rows <= 0:
            problems.append("weather: output file has 0 rows")

    if problems:
        raise AirflowException("Raw data sanity check failed:\n" + "\n".join(problems))

    logger.info("Raw data sanity check passed for collisions, vehicles, casualties, weather")


def clean_collisions_task(**_):
    with _on_path(SRC_DIR, SRC_DIR / "transformation"):
        from transformation import clean_accidents as mod
        mod.clean_collision_data()


def clean_vehicles_task(**_):
    with _on_path(SRC_DIR, SRC_DIR / "transformation"):
        from transformation import clean_vehicles as mod
        mod.clean_vehicle_data()


def clean_casualties_task(**_):
    with _on_path(SRC_DIR, SRC_DIR / "transformation"):
        from transformation import clean_casualties as mod
        mod.clean_casualty_data()


def quality_checks_task(ti=None, **_):
    with _on_path(PROJECT_ROOT):
        from src.validation.run_validation import DATASETS, validate_dataset

        summaries = []
        valid_counts = {}
        for dataset_name, config in DATASETS.items():
            quality_summary, rejected_df = validate_dataset(dataset_name, config)
            if quality_summary is None:
                raise AirflowException(
                    f"Staged file missing for '{dataset_name}' — did clean_transform run?"
                )
            quality_summary.insert(0, "dataset", dataset_name)
            summaries.append(quality_summary)

            staged_file = STAGING_DIR / config["file"]
            total_rows = len(pd.read_csv(staged_file, low_memory=False))
            rejected_rows = 0 if rejected_df is None else len(rejected_df)
            valid_counts[dataset_name] = total_rows - rejected_rows

        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        final_report = pd.concat(summaries, ignore_index=True)
        final_report.to_csv(REPORT_DIR / "validation_quality_report.csv", index=False)

        logger.info("Valid record counts: %s", valid_counts)
        if ti:
            ti.xcom_push(key="valid_counts", value=valid_counts)


def branch_on_quality(ti=None, **_):
    # Gate on collisions (the backbone every other table joins against)
    # having valid rows — not on whether any rejects exist at all.
    valid_counts = ti.xcom_pull(task_ids="quality_checks", key="valid_counts") or {}
    if valid_counts.get("collisions", 0) <= 0:
        logger.error("No valid collision records after validation — halting load.")
        return "rejected_log"
    return "load_postgres"


def load_postgres_task(**_):
    with _on_path(PROJECT_ROOT, SRC_DIR):
        from src.validation.quality_checks import (
            validate_collisions, validate_vehicles, validate_casualties, get_valid_records,
        )
        from geospatial.db import get_engine

        engine = get_engine()
        validators = {
            "collisions": (STAGING_DIR / "collisions_cleaned.csv", validate_collisions),
            "vehicles": (STAGING_DIR / "vehicles_cleaned.csv", validate_vehicles),
            "casualties": (STAGING_DIR / "casualties_cleaned.csv", validate_casualties),
        }
        for table, (path, validator) in validators.items():
            df = pd.read_csv(path, low_memory=False)
            valid_mask = get_valid_records(validator(df))
            valid_df = df[valid_mask]
            valid_df.to_sql(table, engine, if_exists="replace", index=False)
            logger.info("Loaded %s valid rows into '%s'", len(valid_df), table)

        if RAW_WEATHER_FILE.exists():
            weather_df = pd.read_csv(RAW_WEATHER_FILE, low_memory=False)
            weather_df.to_sql("weather", engine, if_exists="replace", index=False)
            logger.info("Loaded %s rows into 'weather'", len(weather_df))


def load_postgis_task(**_):
    with _on_path(SRC_DIR, SRC_DIR / "geospatial"):
        from sqlalchemy import text
        from geospatial.db import get_engine
        from geospatial.hotspot_analysis import create_hotspot_table_sql, refresh_hotspot_grid

        engine = get_engine()
        enable_postgis_sql = (SQL_GEOSPATIAL_DIR / "enable_postgis.sql").read_text()

        with engine.begin() as conn:
            conn.execute(text(enable_postgis_sql))
            conn.execute(text(
                "ALTER TABLE collisions ADD COLUMN IF NOT EXISTS geom geometry(Point, 4326)"
            ))
            conn.execute(text(
                """
                UPDATE collisions
                SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
                WHERE latitude IS NOT NULL AND longitude IS NOT NULL
                """
            ))
            conn.execute(text(create_hotspot_table_sql()))

        summary = refresh_hotspot_grid(engine=engine)
        logger.info("Hotspot grid refreshed: %s", summary)


def build_analytical_mart_task(**_):
    with _on_path(SRC_DIR, SRC_DIR / "geospatial"):
        from sqlalchemy import text
        from geospatial.db import get_engine

        engine = get_engine()
        collisions = pd.read_sql_table("collisions", engine)

        if "time" in collisions.columns:
            collisions["hour"] = pd.to_datetime(
                collisions["time"], errors="coerce", format="%H:%M"
            ).dt.hour

        group_cols = [c for c in ("hour", "collision_severity", "road_type") if c in collisions.columns]
        if not group_cols:
            raise AirflowException(
                "None of hour/collision_severity/road_type present in 'collisions' — "
                "check cleaning output columns."
            )

        mart = (
            collisions.groupby(group_cols, dropna=False)
            .agg(accident_count=("collision_index", "count"))
            .reset_index()
            .sort_values("accident_count", ascending=False)
        )

        try:
            hotspots = pd.read_sql_table("spatial_hotspot_grid", engine)
            mart.attrs["hotspot_cells"] = len(hotspots)
        except Exception:
            logger.warning("spatial_hotspot_grid not available yet — mart built without it")

        DASHBOARD_ANALYTICS_CSV.parent.mkdir(parents=True, exist_ok=True)
        mart.to_csv(DASHBOARD_ANALYTICS_CSV, index=False)

        if DASHBOARD_ANALYTICS_SCHEMA:
            with engine.begin() as conn:
                conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {DASHBOARD_ANALYTICS_SCHEMA}"))
        mart.to_sql(
            DASHBOARD_ANALYTICS_TABLE,
            engine,
            schema=DASHBOARD_ANALYTICS_SCHEMA,
            if_exists="replace",
            index=False,
        )
        logger.info(
            "Analytical mart written: %s rows -> %s and table '%s.%s'",
            len(mart), DASHBOARD_ANALYTICS_CSV,
            DASHBOARD_ANALYTICS_SCHEMA or "public", DASHBOARD_ANALYTICS_TABLE,
        )


def dashboard_ready_task(**_):
    # Terminal signal task — the Streamlit dashboard reads
    # DASHBOARD_ANALYTICS_CSV / _TABLE independently; this just confirms
    # the data it needs actually exists.
    if not DASHBOARD_ANALYTICS_CSV.exists():
        raise AirflowException(f"Dashboard analytics file missing: {DASHBOARD_ANALYTICS_CSV}")
    rows = sum(1 for _ in open(DASHBOARD_ANALYTICS_CSV)) - 1
    if rows <= 0:
        raise AirflowException("Dashboard analytics file has 0 rows")
    logger.info("Dashboard data ready: %s rows in %s", rows, DASHBOARD_ANALYTICS_CSV)


def rejected_log_task(**_):
    rejected_dir = DATA_DIR / "rejected"
    if not rejected_dir.exists():
        logger.warning("No rejected/ directory found — nothing to summarize")
        return
    total = 0
    for f in rejected_dir.glob("*_rejected.csv"):
        n = sum(1 for _ in open(f)) - 1
        logger.info("%s: %s rejected rows", f.name, n)
        total += n
    logger.error("Pipeline halted at quality gate. Total rejected rows logged: %s", total)


default_args = {
    "owner": "1CR23AI127",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
    "execution_timeout": timedelta(hours=2),
}

with DAG(
    dag_id="traffic_accident_pipeline",
    description="End-to-end traffic accident severity analytics pipeline",
    default_args=default_args,
    schedule="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["traffic-accident-severity-analytics", "1CR23AI127"],
) as dag:

    start = EmptyOperator(task_id="start")

    ingest_accidents = PythonOperator(task_id="ingest_accidents", python_callable=ingest_accidents_task)
    ingest_vehicles = PythonOperator(task_id="ingest_vehicles", python_callable=ingest_vehicles_task)
    ingest_casualties = PythonOperator(task_id="ingest_casualties", python_callable=ingest_casualties_task)
    ingest_weather = PythonOperator(task_id="ingest_weather", python_callable=ingest_weather_task)

    validate_raw_data = PythonOperator(task_id="validate_raw_data", python_callable=validate_raw_data_task)

    clean_collisions = PythonOperator(task_id="clean_collisions", python_callable=clean_collisions_task)
    clean_vehicles = PythonOperator(task_id="clean_vehicles", python_callable=clean_vehicles_task)
    clean_casualties = PythonOperator(task_id="clean_casualties", python_callable=clean_casualties_task)

    quality_checks = PythonOperator(task_id="quality_checks", python_callable=quality_checks_task)

    branch = BranchPythonOperator(task_id="branch_on_quality", python_callable=branch_on_quality)

    load_postgres = PythonOperator(task_id="load_postgres", python_callable=load_postgres_task)
    load_postgis = PythonOperator(task_id="load_postgis", python_callable=load_postgis_task)
    analytical_mart = PythonOperator(task_id="analytical_mart", python_callable=build_analytical_mart_task)
    dashboard_ready = PythonOperator(task_id="dashboard_ready", python_callable=dashboard_ready_task)

    rejected_log = PythonOperator(
        task_id="rejected_log",
        python_callable=rejected_log_task,
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
    )

    start >> [ingest_accidents, ingest_vehicles, ingest_casualties]
    ingest_accidents >> ingest_weather

    [ingest_vehicles, ingest_casualties, ingest_weather] >> validate_raw_data

    validate_raw_data >> [clean_collisions, clean_vehicles, clean_casualties]
    [clean_collisions, clean_vehicles, clean_casualties] >> quality_checks

    quality_checks >> branch
    branch >> load_postgres >> load_postgis >> analytical_mart >> dashboard_ready
    branch >> rejected_log