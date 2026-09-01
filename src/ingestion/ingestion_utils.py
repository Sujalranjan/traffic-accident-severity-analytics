from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
METADATA_DIR = RAW_DATA_DIR / "metadata"
LOGS_DIR = PROJECT_ROOT / "logs"
INGESTION_LOG_FILE = LOGS_DIR / "ingestion_log.csv"


def validate_source_file(source_path: str | Path, required_columns: list[str]) -> list[str]:
    """Check that a CSV exists, is non-empty, and has the required columns."""
    path = Path(source_path)

    if not path.exists():
        raise FileNotFoundError(f"Source file not found: {path}")

    if path.suffix.lower() != ".csv":
        raise ValueError(f"Expected a CSV file, received: {path.name}")

    if path.stat().st_size == 0:
        raise ValueError(f"Source file is empty: {path.name}")

    columns = pd.read_csv(path, nrows=0).columns.tolist()
    missing_columns = [column for column in required_columns if column not in columns]

    if missing_columns:
        raise ValueError(
            f"Missing required columns in {path.name}: {', '.join(missing_columns)}"
        )

    return columns


def count_rows(source_path: str | Path) -> int:
    """Count CSV rows in chunks to avoid loading the whole file into memory."""
    return sum(
        len(chunk)
        for chunk in pd.read_csv(source_path, chunksize=100_000, low_memory=False)
    )


def calculate_file_hash(file_path: str | Path) -> str:
    """Create a SHA-256 checksum to show that the raw copy is unchanged."""
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(block)

    return sha256.hexdigest()


def copy_to_raw_storage(source_path: str | Path, dataset_name: str) -> Path:
    """Copy the original file unchanged into its raw-data folder."""
    source = Path(source_path)
    destination_dir = RAW_DATA_DIR / dataset_name
    destination_dir.mkdir(parents=True, exist_ok=True)

    destination = destination_dir / source.name
    shutil.copy2(source, destination)

    return destination


def save_metadata(metadata: dict, dataset_name: str) -> Path:
    """Save metadata for one ingestion run as JSON."""
    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    metadata_file = METADATA_DIR / f"{dataset_name}_{timestamp}.json"

    with open(metadata_file, "w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=2)

    return metadata_file


def append_ingestion_log(log_record: dict) -> None:
    """Append a single ingestion result to the project log."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    log_frame = pd.DataFrame([log_record])
    log_frame.to_csv(
        INGESTION_LOG_FILE,
        mode="a",
        header=not INGESTION_LOG_FILE.exists(),
        index=False,
    )