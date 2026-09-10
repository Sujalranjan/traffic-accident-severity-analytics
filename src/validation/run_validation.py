"""
Main validation pipeline for traffic accident datasets.

Loads cleaned staging datasets, applies data-quality checks,
generates quality reports, and stores rejected records.
"""

from pathlib import Path

import pandas as pd

from src.validation.quality_checks import (
    validate_collisions,
    validate_vehicles,
    validate_casualties,
    generate_quality_summary,
)

from src.validation.rejected_records import (
    create_rejected_records,
    save_rejected_records,
)


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

STAGING_DIR = PROJECT_ROOT / "data" / "staging"

REPORT_DIR = PROJECT_ROOT / "reports"


# ---------------------------------------------------------
# Dataset configuration
# ---------------------------------------------------------

DATASETS = {
    "collisions": {
        "file": "collisions_cleaned.csv",
        "validator": validate_collisions,
    },
    "vehicles": {
        "file": "vehicles_cleaned.csv",
        "validator": validate_vehicles,
    },
    "casualties": {
        "file": "casualties_cleaned.csv",
        "validator": validate_casualties,
    },
}


# ---------------------------------------------------------
# Validate one dataset
# ---------------------------------------------------------

def validate_dataset(dataset_name, config):

    input_file = STAGING_DIR / config["file"]

    print("\n" + "=" * 60)
    print(f"VALIDATING: {dataset_name.upper()}")
    print("=" * 60)

    if not input_file.exists():
        print(f"ERROR: Input file not found:")
        print(input_file)
        return None, None

    print(f"Loading: {input_file}")

    df = pd.read_csv(
        input_file,
        low_memory=False,
    )

    print(f"Records loaded: {len(df):,}")

    # Apply validation rules
    validation_results = config["validator"](df)

    # Generate rule-level quality summary
    quality_summary = generate_quality_summary(
        validation_results
    )

    # Determine valid/rejected records
    valid_mask = validation_results.all(axis=1)

    valid_count = int(valid_mask.sum())
    rejected_count = int((~valid_mask).sum())

    print(f"Valid records    : {valid_count:,}")
    print(f"Rejected records : {rejected_count:,}")

    # Create rejected records
    rejected_df = create_rejected_records(
        df,
        validation_results,
        dataset_name,
    )

    # Save rejected records only when failures exist
    if not rejected_df.empty:

        output_file = save_rejected_records(
            rejected_df,
            dataset_name,
        )

        print(f"Rejected records saved to:")
        print(output_file)

    else:
        print("No rejected records found.")

    return quality_summary, rejected_df


# ---------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------

def main():

    print("\n")
    print("=" * 60)
    print("TRAFFIC ACCIDENT DATA QUALITY VALIDATION")
    print("=" * 60)

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    all_quality_reports = []

    for dataset_name, config in DATASETS.items():

        quality_summary, _ = validate_dataset(
            dataset_name,
            config,
        )

        if quality_summary is not None:

            quality_summary.insert(
                0,
                "dataset",
                dataset_name,
            )

            all_quality_reports.append(
                quality_summary
            )

    # -----------------------------------------------------
    # Combined quality report
    # -----------------------------------------------------

    if all_quality_reports:

        final_report = pd.concat(
            all_quality_reports,
            ignore_index=True,
        )

        report_file = (
            REPORT_DIR
            / "validation_quality_report.csv"
        )

        final_report.to_csv(
            report_file,
            index=False,
        )

        print("\n" + "=" * 60)
        print("VALIDATION COMPLETED")
        print("=" * 60)

        print(f"Quality report:")
        print(report_file)

        print("\nQuality summary:")
        print(final_report.to_string(index=False))

    else:

        print("\nNo datasets were available for validation.")


# ---------------------------------------------------------
# Script entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    main()