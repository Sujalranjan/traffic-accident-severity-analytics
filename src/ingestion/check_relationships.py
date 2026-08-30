from pathlib import Path
import pandas as pd


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw"


# ---------------------------------------------------------
# Dataset paths
# ---------------------------------------------------------

COLLISION_FILE = (
    RAW_DIR
    / "dft-road-casualty-statistics-collision-last-5-years.csv"
)

VEHICLE_FILE = (
    RAW_DIR
    / "dft-road-casualty-statistics-vehicle-last-5-years.csv"
)

CASUALTY_FILE = (
    RAW_DIR
    / "dft-road-casualty-statistics-casualty-last-5-years.csv"
)


# ---------------------------------------------------------
# Load datasets
# ---------------------------------------------------------

def load_datasets():
    print("Loading datasets...")

    collision = pd.read_csv(
        COLLISION_FILE,
        low_memory=False
    )

    vehicle = pd.read_csv(
        VEHICLE_FILE,
        low_memory=False
    )

    casualty = pd.read_csv(
        CASUALTY_FILE,
        low_memory=False
    )

    print(f"Collision records : {len(collision):,}")
    print(f"Vehicle records   : {len(vehicle):,}")
    print(f"Casualty records  : {len(casualty):,}")

    return collision, vehicle, casualty


# ---------------------------------------------------------
# Check primary-key uniqueness
# ---------------------------------------------------------

def check_key_uniqueness(collision, vehicle, casualty):

    print("\n" + "=" * 70)
    print("KEY UNIQUENESS CHECKS")
    print("=" * 70)

    collision_duplicates = collision["collision_index"].duplicated().sum()

    vehicle_duplicates = vehicle[
        ["collision_index", "vehicle_reference"]
    ].duplicated().sum()

    casualty_duplicates = casualty[
        [
            "collision_index",
            "vehicle_reference",
            "casualty_reference",
        ]
    ].duplicated().sum()

    print(
        f"Duplicate collision_index: "
        f"{collision_duplicates:,}"
    )

    print(
        f"Duplicate vehicle keys: "
        f"{vehicle_duplicates:,}"
    )

    print(
        f"Duplicate casualty keys: "
        f"{casualty_duplicates:,}"
    )


# ---------------------------------------------------------
# Check Vehicle → Collision relationship
# ---------------------------------------------------------

def check_vehicle_collision_relationship(collision, vehicle):

    print("\n" + "=" * 70)
    print("VEHICLE → COLLISION RELATIONSHIP")
    print("=" * 70)

    collision_ids = set(
        collision["collision_index"]
    )

    invalid_vehicle_collisions = (
        ~vehicle["collision_index"].isin(collision_ids)
    ).sum()

    print(
        "Vehicle records with invalid collision_index: "
        f"{invalid_vehicle_collisions:,}"
    )


# ---------------------------------------------------------
# Check Casualty → Collision relationship
# ---------------------------------------------------------

def check_casualty_collision_relationship(
    collision,
    casualty
):

    print("\n" + "=" * 70)
    print("CASUALTY → COLLISION RELATIONSHIP")
    print("=" * 70)

    collision_ids = set(
        collision["collision_index"]
    )

    invalid_casualty_collisions = (
        ~casualty["collision_index"].isin(collision_ids)
    ).sum()

    print(
        "Casualty records with invalid collision_index: "
        f"{invalid_casualty_collisions:,}"
    )


# ---------------------------------------------------------
# Check Casualty → Vehicle relationship
# ---------------------------------------------------------

def check_casualty_vehicle_relationship(
    vehicle,
    casualty
):

    print("\n" + "=" * 70)
    print("CASUALTY → VEHICLE RELATIONSHIP")
    print("=" * 70)

    vehicle_keys = set(
        zip(
            vehicle["collision_index"],
            vehicle["vehicle_reference"],
        )
    )

    casualty_vehicle_keys = list(
        zip(
            casualty["collision_index"],
            casualty["vehicle_reference"],
        )
    )

    invalid_casualty_vehicles = sum(
        key not in vehicle_keys
        for key in casualty_vehicle_keys
    )

    print(
        "Casualty records with invalid vehicle reference: "
        f"{invalid_casualty_vehicles:,}"
    )


# ---------------------------------------------------------
# Check collision-level counts
# ---------------------------------------------------------

def check_collision_counts(
    collision,
    vehicle,
    casualty
):

    print("\n" + "=" * 70)
    print("COLLISION COUNT CONSISTENCY CHECKS")
    print("=" * 70)

    vehicle_counts = (
        vehicle
        .groupby("collision_index")
        .size()
        .rename("actual_vehicle_count")
    )

    casualty_counts = (
        casualty
        .groupby("collision_index")
        .size()
        .rename("actual_casualty_count")
    )

    collision_counts = collision[
        [
            "collision_index",
            "number_of_vehicles",
            "number_of_casualties",
        ]
    ].copy()

    collision_counts = collision_counts.merge(
        vehicle_counts,
        on="collision_index",
        how="left"
    )

    collision_counts = collision_counts.merge(
        casualty_counts,
        on="collision_index",
        how="left"
    )

    collision_counts[
        "actual_vehicle_count"
    ] = collision_counts[
        "actual_vehicle_count"
    ].fillna(0)

    collision_counts[
        "actual_casualty_count"
    ] = collision_counts[
        "actual_casualty_count"
    ].fillna(0)

    vehicle_mismatch = (
        collision_counts["number_of_vehicles"]
        != collision_counts["actual_vehicle_count"]
    ).sum()

    casualty_mismatch = (
        collision_counts["number_of_casualties"]
        != collision_counts["actual_casualty_count"]
    ).sum()

    print(
        "Collisions with vehicle-count mismatch: "
        f"{vehicle_mismatch:,}"
    )

    print(
        "Collisions with casualty-count mismatch: "
        f"{casualty_mismatch:,}"
    )


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    collision, vehicle, casualty = load_datasets()

    check_key_uniqueness(
        collision,
        vehicle,
        casualty
    )

    check_vehicle_collision_relationship(
        collision,
        vehicle
    )

    check_casualty_collision_relationship(
        collision,
        casualty
    )

    check_casualty_vehicle_relationship(
        vehicle,
        casualty
    )

    check_collision_counts(
        collision,
        vehicle,
        casualty
    )

    print("\n" + "=" * 70)
    print("RELATIONSHIP CHECKS COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()