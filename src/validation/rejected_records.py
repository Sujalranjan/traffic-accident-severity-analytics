"""
Rejected record handling for traffic accident data validation.

Invalid records are preserved with the validation failures that
caused them to be rejected.
"""

from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

REJECTED_DIR = PROJECT_ROOT / "data" / "rejected"


# ---------------------------------------------------------
# Generate rejection reasons
# ---------------------------------------------------------

def get_rejection_reasons(validation_results):
    """
    Generate a readable list of failed validation rules
    for every record.
    """

    reasons = []

    for _, row in validation_results.iterrows():

        failed_rules = [
            rule
            for rule, passed in row.items()
            if not passed
        ]

        reasons.append(
            "; ".join(failed_rules)
            if failed_rules
            else ""
        )

    return reasons


# ---------------------------------------------------------
# Create rejected records
# ---------------------------------------------------------

def create_rejected_records(
    df,
    validation_results,
    dataset_name,
):
    """
    Create a DataFrame containing records that failed
    one or more validation rules.

    The original record is preserved and additional
    validation information is attached.
    """

    rejected_mask = ~validation_results.all(axis=1)

    rejected = df.loc[rejected_mask].copy()

    if rejected.empty:
        return rejected

    failed_rules = get_rejection_reasons(
        validation_results.loc[rejected_mask]
    )

    rejected["dataset"] = dataset_name
    rejected["rejection_reason"] = failed_rules

    return rejected


# ---------------------------------------------------------
# Save rejected records
# ---------------------------------------------------------

def save_rejected_records(
    rejected_df,
    dataset_name,
):
    """
    Save rejected records to the data/rejected directory.
    """

    REJECTED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = (
        REJECTED_DIR
        / f"{dataset_name}_rejected.csv"
    )

    rejected_df.to_csv(
        output_file,
        index=False,
    )

    return output_file