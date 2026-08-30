# GitHub Issues Plan (Part 1 Modules)

This document contains the ready-to-use titles, descriptions, and acceptance criteria for creating the 12 GitHub Issues corresponding to each team member's assignment scope.

---

### Issue 1: Dataset Acquisition & Research — 1CR23AI119
- **Assignee USN**: `1CR23AI119` (Team Lead)
- **Branch**: `feature/dataset-research-119`
- **Description**:
  - Identify, acquire, and document the official UK Department for Transport (DfT) Road Safety Open Data.
  - Document dataset metadata, licensing terms, column definitions, and coordinate reference formats in `docs/dataset/`.
  - Establish data provenance documentation and provide sample schema formats.
- **Acceptance Criteria**:
  - [ ] Research documentation complete in `docs/dataset/`.
  - [ ] Data dictionary drafted in `docs/data_dictionary/`.
  - [ ] License and source provenance documented.

---

### Issue 2: Accident Data Ingestion — 1CR23AI121
- **Assignee USN**: `1CR23AI121`
- **Branch**: `feature/accident-ingestion-121`
- **Description**:
  - Implement Python ingestion scripts in `src/ingestion/` to read and parse raw UK DfT accident data.
  - Support chunked or batch reading of large CSV files.
  - Save initial structured data into the raw/staging layer (`data/raw/`, `data/staging/`).
- **Acceptance Criteria**:
  - [ ] Robust ingestion script with error handling in `src/ingestion/`.
  - [ ] Support for parsing collision, vehicle, and casualty datasets.
  - [ ] Raw to staging load verification.

---

### Issue 3: Weather Data Integration — 1CR23AI123
- **Assignee USN**: `1CR23AI123`
- **Branch**: `feature/weather-123`
- **Description**:
  - Develop the client module in `src/weather/` for querying the Open-Meteo Historical Weather API.
  - Fetch hourly weather telemetry (precipitation, temperature, visibility, wind) matching accident timestamps and GPS coordinates.
  - Implement caching/rate-limit handling for efficient API usage.
- **Acceptance Criteria**:
  - [ ] Open-Meteo API wrapper in `src/weather/`.
  - [ ] Temporal and spatial alignment between accidents and weather data.
  - [ ] Handling of network retries and edge cases.

---

### Issue 4: Data Cleaning & Standardization — 1CR23AI124
- **Assignee USN**: `1CR23AI124`
- **Branch**: `feature/data-cleaning-124`
- **Description**:
  - Create data cleaning and normalization routines in `src/transformation/`.
  - Handle missing/null values, erroneous negative codes, standard categorical encodings, and datetime normalization.
  - Output standardized data ready for validation and database insertion.
- **Acceptance Criteria**:
  - [ ] Transformation modules in `src/transformation/`.
  - [ ] Standardized date/time formats, categorical labels, and numeric types.
  - [ ] Documented cleaning decisions and assumptions.

---

### Issue 5: Data Quality & Validation — 1CR23AI126
- **Assignee USN**: `1CR23AI126`
- **Branch**: `feature/data-validation-126`
- **Description**:
  - Implement data quality assertion rules and boundary checks in `src/validation/`.
  - Validate latitude/longitude bounds, severity levels (1: Fatal, 2: Serious, 3: Slight), date ranges, and non-negative counts.
  - Maintain an automated rejected/error record log for malformed rows.
- **Acceptance Criteria**:
  - [ ] Validation suite in `src/validation/`.
  - [ ] Error logging mechanism for rejected rows with failure reasons.
  - [ ] Summary report generation of data quality metrics.

---

### Issue 6: Airflow Orchestration — 1CR23AI127
- **Assignee USN**: `1CR23AI127`
- **Branch**: `feature/airflow-127`
- **Description**:
  - Build Apache Airflow DAGs in `airflow/dags/` to automate the end-to-end ETL workflow.
  - Configure task dependencies: ingestion -> weather enrichment -> cleaning -> validation -> database loading -> mart refresh.
  - Add task retry policies, failure alerting, and execution monitoring.
- **Acceptance Criteria**:
  - [ ] Complete Airflow DAG definition in `airflow/dags/`.
  - [ ] Proper task dependency graph and retry configurations.
  - [ ] Documented steps to run Airflow locally.

---

### Issue 7: PostgreSQL Database — 1CR23AI129
- **Assignee USN**: `1CR23AI129`
- **Branch**: `feature/postgresql-129`
- **Description**:
  - Design and implement relational database schemas and DDL scripts in `sql/schemas/` and `sql/tables/`.
  - Create normalized tables for accidents, vehicles, casualties, and weather observations.
  - Configure primary keys, foreign keys, constraints, and B-Tree indexes for fast query performance.
- **Acceptance Criteria**:
  - [ ] SQL DDL scripts in `sql/schemas/` and `sql/tables/`.
  - [ ] Database connection and table creation scripts in Python.
  - [ ] Verified relational integrity and index performance.

---

### Issue 8: PostGIS & Geospatial Processing — 1CR23AI130
- **Assignee USN**: `1CR23AI130`
- **Branch**: `feature/postgis-130`
- **Description**:
  - Enable and configure PostGIS spatial extension.
  - Add geometry columns (`POINT(longitude, latitude)`) in SRID 4326 (WGS 84).
  - Implement spatial indexing (GIST) and geospatial query functions in `src/geospatial/`.
- **Acceptance Criteria**:
  - [ ] Spatial schema scripts and PostGIS initialization.
  - [ ] Spatial queries for bounding boxes, proximity, and density.
  - [ ] Performance-optimized GIST indexing.

---

### Issue 9: Analytical Data Mart — 1CR23AI131
- **Assignee USN**: `1CR23AI131`
- **Branch**: `feature/data-mart-131`
- **Description**:
  - Design dimensional modeling (Star/Snowflake schema) in `sql/dimensions/`, `sql/facts/`, and `sql/marts/`.
  - Construct dimension tables (`dim_date`, `dim_weather`, `dim_road_type`, `dim_location`) and `fact_accidents`.
  - Build analytical aggregation marts by hour, day of week, weather condition, and road type.
- **Acceptance Criteria**:
  - [ ] Dimension and Fact DDL scripts in `sql/`.
  - [ ] Aggregated data mart views in `sql/marts/`.
  - [ ] Verification of query performance on aggregation views.

---

### Issue 10: Dashboard Analytics — 1CR23AI132
- **Assignee USN**: `1CR23AI132`
- **Branch**: `feature/dashboard-132`
- **Description**:
  - Build core analytical components and visual KPI cards in `dashboard/`.
  - Implement minimum 5 distinct analytical indicators (severity distribution, time-of-day trends, weather impact, casualty rates, road conditions).
  - Integrate interactive Plotly charts with dynamic filtering.
- **Acceptance Criteria**:
  - [ ] Analytical dashboard pages in `dashboard/pages/`.
  - [ ] At least 5 distinct, well-designed analytical views.
  - [ ] Interactive parameter filters and KPI summaries.

---

### Issue 11: Dashboard Map & UI — 1CR23AI133
- **Assignee USN**: `1CR23AI133`
- **Branch**: `feature/dashboard-ui-133`
- **Description**:
  - Develop geospatial mapping interface in `dashboard/` using Streamlit and geospatial visualization libraries.
  - Render accident density heatmaps, accident severity clusters, and location-based filters.
  - Polish the overall dashboard layout, sidebar navigation, and styling.
- **Acceptance Criteria**:
  - [ ] Geospatial map page in `dashboard/`.
  - [ ] Heatmap / cluster visualization of high-accident zones.
  - [ ] Cohesive, modern UI navigation and layout.

---

### Issue 12: Integration, Testing & Documentation — 1CR23AI135
- **Assignee USN**: `1CR23AI135`
- **Branch**: `feature/integration-135`
- **Description**:
  - Develop automated test suites using `pytest` in `tests/` for ingestion, transformation, and validation modules.
  - Verify end-to-end pipeline execution from raw data to dashboard.
  - Compile final execution evidence, test logs, screenshots, and complete architectural documentation.
- **Acceptance Criteria**:
  - [ ] Automated test suite in `tests/`.
  - [ ] Pipeline integration tests passing.
  - [ ] Architecture documentation in `docs/architecture/` and test evidence in `docs/screenshots/`.
