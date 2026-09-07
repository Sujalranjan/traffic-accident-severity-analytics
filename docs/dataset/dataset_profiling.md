# Dataset Profiling Report

## 1. Overview

This document presents the initial profiling results of the traffic
accident datasets selected for the Traffic Accident Severity Analytics
and Prediction project.

The datasets were obtained from the UK Department for Transport (DfT)
Road Safety Open Data and cover the latest five-year period available
for the project.

The three datasets used are:

1. Collision dataset
2. Vehicle dataset
3. Casualty dataset

The profiling was performed programmatically using Python and Pandas
through the `src/ingestion/profile_datasets.py` script.

---

## 2. Dataset Summary

| Dataset | Rows | Columns |
|---|---:|---:|
| Collision | 513,801 | 44 |
| Vehicle | 937,265 | 32 |
| Casualty | 652,821 | 23 |

The Collision dataset represents the primary accident-level dataset.
The Vehicle dataset contains vehicle-level records associated with
collisions, while the Casualty dataset contains casualty-level records.

---

## 3. Collision Dataset

### Dataset dimensions

- Rows: 513,801
- Columns: 44

### Missing-value analysis

The profiling identified missing values in four geographic fields:

| Column | Missing Records | Missing Percentage |
|---|---:|---:|
| `location_easting_osgr` | 53 | 0.0103% |
| `location_northing_osgr` | 53 | 0.0103% |
| `longitude` | 53 | 0.0103% |
| `latitude` | 53 | 0.0103% |

All other Collision dataset columns contained no missing values
according to the initial profiling.

### Observation

The missing values are concentrated in the geographic attributes of
53 collision records. These records require further handling during
the data-quality and geospatial processing stages.

They should not be manually deleted at the dataset-acquisition stage.
The validation pipeline should determine how these records are handled.

---

## 4. Vehicle Dataset

### Dataset dimensions

- Rows: 937,265
- Columns: 32

### Missing-value analysis

The initial profiling found no missing values in the Vehicle dataset.

| Dataset | Missing Values |
|---|---:|
| Vehicle | None detected |

The Vehicle dataset will be used for vehicle-level analysis and will
later be joined to Collision records using the appropriate collision
and vehicle identifiers.

---

## 5. Casualty Dataset

### Dataset dimensions

- Rows: 652,821
- Columns: 23

### Missing-value analysis

The initial profiling found no missing values in the Casualty dataset.

| Dataset | Missing Values |
|---|---:|
| Casualty | None detected |

The Casualty dataset will be used for casualty-level analysis and will
later be joined to Collision and Vehicle records using the appropriate
identifiers.

---

## 6. Profiling Methodology

The profiling was performed using a reusable Python script:

`src/ingestion/profile_datasets.py`

For each dataset, the script calculates:

- Dataset row count
- Dataset column count
- Column names
- Data types
- Missing-value count
- Missing-value percentage
- Number of unique values

The generated profiling files are stored in:

`docs/dataset/generated/`

Generated files:

- `collision_profile.csv`
- `vehicle_profile.csv`
- `casualty_profile.csv`

---

## 7. Initial Data Quality Findings

The initial profiling produced the following findings:

### Collision

- 513,801 records were analyzed.
- 44 columns were identified.
- 53 records contain missing latitude values.
- 53 records contain missing longitude values.
- 53 records contain missing easting values.
- 53 records contain missing northing values.

### Vehicle

- 937,265 records were analyzed.
- 32 columns were identified.
- No missing values were detected.

### Casualty

- 652,821 records were analyzed.
- 23 columns were identified.
- No missing values were detected.

---

## 8. Implications for the Data Pipeline

The profiling results will be used by the subsequent pipeline stages.

### Data Cleaning

The cleaning stage should preserve the raw records while
standardizing data types and formats.

### Data Validation

The validation stage should specifically check the geographic
attributes of collision records.

### Geospatial Processing

Records without valid latitude and longitude cannot be directly used
for coordinate-based spatial analysis and hotspot mapping.

### Database Loading

The cleaned and validated datasets will later be loaded into the
PostgreSQL/PostGIS database.

### Analytical Data Mart

The analytical layer will use the validated collision, vehicle and
casualty records for accident, road, weather and location analysis.

---

## 9. Reproducibility

The profiling results should not be manually edited.

To regenerate the profiles, run:

```bash
python src/ingestion/profile_datasets.py