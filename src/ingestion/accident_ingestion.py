from datetime import datetime, timezone
from pathlib import Path

from ingestion_utils import (
    append_ingestion_log,
    calculate_file_hash,
    copy_to_raw_storage,
    count_rows,
    save_metadata,
    validate_source_file,
)


DATASET_NAME = "collisions"
SOURCE_URL = (
    "https://www.gov.uk/government/statistical-data-sets/road-safety-open-data"
)
SOURCE_FILE = (
    Path.home()
    / "Downloads"
    / "dft-road-casualty-statistics-collision-last-5-years.csv"
)

REQUIRED_COLUMNS = [
    "collision_index",
    "collision_year",
    "collision_severity",
]

def ingest_collision_data() -> None:
    extraction_time = datetime.now(timezone.utc).isoformat()

    log_record = {
        "extraction_time_utc": extraction_time,
        "dataset_name": DATASET_NAME,
        "source_file": str(SOURCE_FILE),
        "source_url": SOURCE_URL,
        "status": "failed",
        "row_count": 0,
        "raw_file": "",
        "error_message": "",
    }

    try:
        columns = validate_source_file(SOURCE_FILE, REQUIRED_COLUMNS)
        row_count = count_rows(SOURCE_FILE)
        raw_file = copy_to_raw_storage(SOURCE_FILE, DATASET_NAME)

        metadata = {
            "dataset_name": DATASET_NAME,
            "source_url": SOURCE_URL,
            "source_file": str(SOURCE_FILE),
            "raw_file": str(raw_file),
            "extraction_time_utc": extraction_time,
            "status": "success",
            "row_count": row_count,
            "column_count": len(columns),
            "columns": columns,
            "source_file_sha256": calculate_file_hash(SOURCE_FILE),
        }
        metadata_file = save_metadata(metadata, DATASET_NAME)

        log_record.update(
            {
                "status": "success",
                "row_count": row_count,
                "raw_file": str(raw_file),
            }
        )
        append_ingestion_log(log_record)

        print("Collision ingestion completed successfully.")
        print(f"Rows ingested: {row_count}")
        print(f"Raw copy: {raw_file}")
        print(f"Metadata: {metadata_file}")

    except Exception as error:
        log_record["error_message"] = str(error)
        append_ingestion_log(log_record)
        print(f"Collision ingestion failed: {error}")
        raise


if __name__ == "__main__":
    ingest_collision_data()