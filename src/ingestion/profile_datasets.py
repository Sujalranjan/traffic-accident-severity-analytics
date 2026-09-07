from pathlib import Path
import pandas as pd


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR = PROJECT_ROOT / "docs" / "dataset" / "generated"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# Dataset configuration
# ---------------------------------------------------------

DATASETS = {
    "collision": "dft-road-casualty-statistics-collision-last-5-years.csv",
    "vehicle": "dft-road-casualty-statistics-vehicle-last-5-years.csv",
    "casualty": "dft-road-casualty-statistics-casualty-last-5-years.csv",
}


# ---------------------------------------------------------
# Profile one dataset
# ---------------------------------------------------------

def profile_dataset(dataset_name: str, file_name: str) -> None:
    file_path = RAW_DIR / file_name

    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {file_path}\n"
            f"Place the CSV file inside: {RAW_DIR}"
        )

    print("\n" + "=" * 70)
    print(f"Profiling dataset: {dataset_name.upper()}")
    print("=" * 70)

    # Read dataset
    df = pd.read_csv(
        file_path,
        low_memory=False
    )

    row_count = len(df)
    column_count = len(df.columns)

    print(f"Rows    : {row_count:,}")
    print(f"Columns : {column_count}")

    # Build column profile
    profile = pd.DataFrame({
        "column_name": df.columns,
        "data_type": [
            str(df[column].dtype)
            for column in df.columns
        ],
        "row_count": row_count,
        "missing_count": [
            int(df[column].isna().sum())
            for column in df.columns
        ],
        "missing_percentage": [
            round(
                df[column].isna().mean() * 100,
                4
            )
            for column in df.columns
        ],
        "unique_count": [
            int(df[column].nunique(dropna=True))
            for column in df.columns
        ],
    })

    # Save profile
    output_file = OUTPUT_DIR / f"{dataset_name}_profile.csv"

    profile.to_csv(
        output_file,
        index=False
    )

    print(f"Profile saved: {output_file}")

    # Display missing-value summary
    missing = profile[
        profile["missing_count"] > 0
    ].sort_values(
        "missing_count",
        ascending=False
    )

    if not missing.empty:
        print("\nColumns containing missing values:")
        print(
            missing[
                [
                    "column_name",
                    "missing_count",
                    "missing_percentage"
                ]
            ].to_string(index=False)
        )
    else:
        print("\nNo missing values found.")


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main() -> None:
    print("Traffic Accident Dataset Profiler")
    print("---------------------------------")
    print(f"Raw data directory: {RAW_DIR}")
    print(f"Output directory   : {OUTPUT_DIR}")

    for dataset_name, file_name in DATASETS.items():
        profile_dataset(
            dataset_name,
            file_name
        )

    print("\n" + "=" * 70)
    print("DATASET PROFILING COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()