# Dataset Sources

## 1. Primary Accident Data Source

### Source Organization

Department for Transport (DfT), UK Government

### Dataset Name

UK Road Safety Open Data

### Selected Dataset

Road Safety Data – Latest 5 Years

### Geographic Coverage

Great Britain, covering England, Scotland and Wales.

The dataset does not cover Northern Ireland.

### Selected Time Period

2021–2025

### Files Used

The following three datasets are used in this project:

1. `dft-road-casualty-statistics-collision-last-5-years.csv`
2. `dft-road-casualty-statistics-vehicle-last-5-years.csv`
3. `dft-road-casualty-statistics-casualty-last-5-years.csv`

### Dataset Purpose

The DfT Road Safety Open Data provides record-level road collision,
vehicle and casualty information.

In this project, the Collision dataset is used as the primary
accident-level dataset. Vehicle and Casualty datasets provide
additional information about vehicles involved in collisions and
people involved as casualties.

The datasets are used as the foundation for traffic accident
analytics, including accident severity, temporal patterns, road
conditions, weather conditions, vehicle characteristics, casualty
characteristics and geographical patterns.

### Data Collection System

The datasets are based on the STATS19 road accident reporting system.

### Access Instructions

1. Visit the official UK Government Department for Transport Road
   Safety Open Data page.
2. Locate the section containing the latest five years of data.
3. Download the Collision, Vehicle and Casualty datasets.
4. Store the downloaded files in the project's local
   `data/raw/` directory.
5. Do not manually modify the raw source files.
6. Use the project's ingestion and transformation pipeline for
   subsequent processing.

### Official Source

Department for Transport — Road Safety Open Data:

https://www.gov.uk/government/statistical-data-sets/road-safety-open-data

### Dataset Format

The datasets are provided as CSV files.

### Data Characteristics

The selected datasets contain:

| Dataset | Records | Columns |
|---|---:|---:|
| Collision | 513,801 | 44 |
| Vehicle | 937,265 | 32 |
| Casualty | 652,821 | 23 |

These values were obtained through the project's automated dataset
profiling process.

---

## 2. Weather Data Source

### Source Organization

Open-Meteo

### Dataset/API

Open-Meteo Historical Weather API

### Purpose

Weather data will be used to enrich accident records with
time- and location-specific weather information.

The weather enrichment will be performed using accident location
(latitude and longitude) and accident date/time.

### Planned Weather Information

The weather integration stage may use variables such as:

- Temperature
- Precipitation
- Rain
- Snowfall
- Weather condition/code
- Wind speed
- Wind direction

The final set of weather variables will be determined during the
weather-integration stage.

### Official Documentation

https://open-meteo.com/en/docs/historical-weather-api

---

## 3. Important Dataset Notes and Limitations

### Geographic Scope

The selected DfT road safety data covers Great Britain rather than
the entire United Kingdom.

Northern Ireland is not included.

### Coded Variables

Several DfT variables are represented using numeric codes rather than
descriptive text.

Examples include:

- Collision severity
- Road type
- Weather conditions
- Road surface conditions
- Light conditions
- Junction information
- Vehicle characteristics
- Casualty characteristics

The official DfT Open Dataset Data Guide should be used to interpret
these coded variables.

The project should not manually modify coded values in the raw data.

### Missing Geographic Information

Initial profiling identified 53 Collision records with missing:

- Latitude
- Longitude
- Location Easting
- Location Northing

These records are retained in the raw dataset.

Their treatment will be determined during the project's subsequent
data-quality and geospatial-processing stages.

### Raw Data Preservation

The original downloaded datasets are treated as raw source data.

Raw files should not be manually edited. Any cleaning,
standardization or transformation should be performed through the
automated/reproducible data pipeline.

---

## 4. Dataset Acquisition Date

**Accessed:** 31 August 2026

The project team should record the acquisition/extraction date when
the datasets are ingested into the pipeline so that future refreshes
can be traced.

---

## 5. Dataset Provenance

The data flow for the selected sources is:

```text
UK Department for Transport
        │
        ├── Collision Data
        ├── Vehicle Data
        └── Casualty Data
                │
                ▼
          Project Raw Layer
                │
                ▼
          ETL / Transformation
                │
                ▼
       PostgreSQL / PostGIS

Weather enrichment:

Accident Date + Time
        +
Latitude + Longitude
        │
        ▼
Open-Meteo Historical Weather API
        │
        ▼
Weather Enrichment
        │
        ▼
Analytical Dataset