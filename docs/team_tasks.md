# Team Task Allocation & Tracking (Part 1)

This document tracks task allocations, expected deliverables, module dependencies, and execution status for Part 1 (Data Engineering & Analytics).

> **Initial Status**: All tasks are currently marked **NOT STARTED**. Implementation will begin sequentially once repository initialization is completed and approved.

---

## Task Allocation Table

| USN | Member Responsibility | Main Deliverable | Dependencies | Status |
| :--- | :--- | :--- | :--- | :---: |
| **1CR23AI119** *(Lead)* | Dataset Acquisition & Research | Dataset research doc, source URL catalog, licensing, initial sample schema | None | `NOT STARTED` |
| **1CR23AI121** | Accident Data Ingestion | Python ingestion module (`src/ingestion/`), raw data loader, staging loader | 1CR23AI119 | `NOT STARTED` |
| **1CR23AI123** | Weather Data Integration | Open-Meteo API client (`src/weather/`), timestamp & coordinate weather joiner | 1CR23AI121 | `NOT STARTED` |
| **1CR23AI124** | Data Cleaning & Standardization | Cleansing scripts (`src/transformation/`), missing value handler, schema normalizer | 1CR23AI121, 1CR23AI123 | `NOT STARTED` |
| **1CR23AI126** | Data Quality & Validation | Quality assertion suite (`src/validation/`), rejected record logging, DQ reports | 1CR23AI124 | `NOT STARTED` |
| **1CR23AI127** | Apache Airflow Orchestration | Airflow DAGs (`airflow/dags/`), automated scheduled pipeline, retries & alerts | 1CR23AI124, 1CR23AI126 | `NOT STARTED` |
| **1CR23AI129** | PostgreSQL Database | Relational DDL schemas (`sql/schemas/`, `sql/tables/`), database connection module | 1CR23AI124 | `NOT STARTED` |
| **1CR23AI130** | PostGIS & Geospatial Processing | PostGIS extension setup, spatial indexing, distance/boundary queries (`src/geospatial/`) | 1CR23AI129 | `NOT STARTED` |
| **1CR23AI131** | Analytical Data Mart | Star schema DDL (`sql/marts/`, `sql/dimensions/`, `sql/facts/`), aggregated summary views | 1CR23AI129, 1CR23AI130 | `NOT STARTED` |
| **1CR23AI132** | Dashboard Analytics | Streamlit analytical KPI views, accident breakdown charts (hour, day, weather) | 1CR23AI131 | `NOT STARTED` |
| **1CR23AI133** | Dashboard Map & UI | Streamlit geospatial hotspot mapping, interactive UI filters, layout polish | 1CR23AI130, 1CR23AI131 | `NOT STARTED` |
| **1CR23AI135** | Integration, Testing & Documentation | Pytest test suite (`tests/`), end-to-end pipeline verification, final project report | All Modules | `NOT STARTED` |
