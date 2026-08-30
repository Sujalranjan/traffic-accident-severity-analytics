from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR = PROJECT_ROOT / "docs" / "data_dictionary"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


DATASETS = {
    "collision": "dft-road-casualty-statistics-collision-last-5-years.csv",
    "vehicle": "dft-road-casualty-statistics-vehicle-last-5-years.csv",
    "casualty": "dft-road-casualty-statistics-casualty-last-5-years.csv",
}


def generate_dictionary(dataset_name, file_name):
    file_path = RAW_DIR / file_name

    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    df = pd.read_csv(file_path, low_memory=False)

    dictionary = pd.DataFrame({
        "dataset": dataset_name,
        "column_name": df.columns,
        "data_type": [str(df[col].dtype) for col in df.columns],
        "row_count": len(df),
        "missing_count": [
            int(df[col].isna().sum())
            for col in df.columns
        ],
        "unique_count": [
            int(df[col].nunique(dropna=True))
            for col in df.columns
        ],
    })

    return dictionary


def main():
    profiles = []

    for dataset_name, file_name in DATASETS.items():
        print(f"Processing: {dataset_name}")

        profile = generate_dictionary(
            dataset_name,
            file_name
        )

        profiles.append(profile)

    result = pd.concat(
        profiles,
        ignore_index=True
    )

    output_file = (
        OUTPUT_DIR / "column_inventory.csv"
    )

    result.to_csv(
        output_file,
        index=False
    )

    print("\n" + "=" * 70)
    print("COLUMN INVENTORY GENERATED")
    print("=" * 70)

    print(f"Total columns: {len(result)}")
    print(f"Output: {output_file}")

    print("\nColumns by dataset:")

    print(
        result.groupby("dataset")
        .size()
        .to_string()
    )


if __name__ == "__main__":
    main()