# Dashboard Analytics Contract - 1CR23AI132

This document defines the minimum data contract for the Streamlit dashboard analytics contribution. It is intended for the analytical data mart owner (`1CR23AI131`) and dashboard analytics owner (`1CR23AI132`).

## Input Source

The dashboard can load from either:

- `data/processed/dashboard_analytics.csv`
- PostgreSQL table or view configured by `DATABASE_URL` and `DASHBOARD_ANALYTICS_TABLE`

The default PostgreSQL relation name is `analytics.dashboard_analytics`.

## Required Columns

| Column | Expected meaning |
|---|---|
| `accident_id` | Stable accident identifier used for distinct accident counts. |
| `accident_date` | Accident date parseable by pandas. |
| `hour` | Hour of day from 0 to 23. |
| `weekday` | Weekday name or number from 1 to 7. |
| `severity` | Accident severity as `Fatal`, `Serious`, `Slight`, or source code `1`, `2`, `3`. |

## Optional Columns

| Column | Dashboard usage |
|---|---|
| `weather_condition` | Weather impact filter and breakdown chart. |
| `road_type` | Road type filter, breakdown chart, and casualty-rate chart. |
| `road_surface_condition` | Future surface-condition breakdown. |
| `casualty_count` | Total casualties and average casualties per accident. |
| `vehicle_count` | Future vehicle involvement KPI. |
| `latitude` | Passed through for map/UI teammate integration. |
| `longitude` | Passed through for map/UI teammate integration. |

## Notes

- This contract is mart-ready, not a raw source schema.
- The dashboard does not transform raw accident data or claim generated metrics as real results.
- Missing optional columns produce empty-state messages rather than failures.
- Any changes to these field names should be coordinated with `1CR23AI131` and `1CR23AI133`.
