# Team Workflow & Engineering Guidelines

This document outlines the collaborative engineering workflow, branching strategy, commit standards, Pull Request (PR) process, review protocols, and Definition of Done for the **Traffic Accident Severity Analytics** project (Part 1).

---

## 1. Team Responsibilities & Ownership

| USN | Role / Module | Core Responsibilities |
| :--- | :--- | :--- |
| **1CR23AI119** *(Lead)* | Dataset Acquisition & Research | Lead coordination, dataset acquisition strategy, provenance documentation, data licensing. |
| **1CR23AI121** | Accident Data Ingestion | Raw accident data extraction, chunked file parsing, staging loader scripts in `src/ingestion/`. |
| **1CR23AI123** | Weather Data Integration | Open-Meteo Historical API client, spatial/temporal weather mapping in `src/weather/`. |
| **1CR23AI124** | Data Cleaning & Standardization | Null imputation, schema standardization, categorical mapping in `src/transformation/`. |
| **1CR23AI126** | Data Quality & Validation | Boundary checks, integrity assertion rules, rejected record logging in `src/validation/`. |
| **1CR23AI127** | Apache Airflow Orchestration | Directed Acyclic Graph (DAG) construction, scheduling, backfilling, retries in `airflow/dags/`. |
| **1CR23AI129** | PostgreSQL Database | DDL scripts, table indexing, connection management, schema initialization in `sql/`. |
| **1CR23AI130** | PostGIS & Geospatial Processing | Spatial geometry columns, spatial indexing (GIST), distance calculations in `src/geospatial/`. |
| **1CR23AI131** | Analytical Data Mart | Star/snowflake schema data marts, dimensional aggregations, fact tables in `sql/marts/`. |
| **1CR23AI132** | Dashboard Analytics | Streamlit analytical KPIs, severity distribution charts, multi-dimension metrics in `dashboard/`. |
| **1CR23AI133** | Dashboard Map & UI | Streamlit geospatial hotspot rendering, interactive filters, UI layout in `dashboard/`. |
| **1CR23AI135** | Integration, Testing & Documentation | End-to-end integration tests, pytest test suite in `tests/`, execution evidence and docs. |

---

## 2. Branch Naming Conventions

All development must take place on dedicated feature branches branched off the latest `main`. Team members must use the standardized naming convention corresponding to their USN and module:

| Assigned Branch Name | Owner (USN) | Purpose |
| :--- | :--- | :--- |
| `feature/dataset-research-119` | 1CR23AI119 | Dataset research, metadata collection, documentation |
| `feature/accident-ingestion-121` | 1CR23AI121 | Accident data ingestion scripts & loaders |
| `feature/weather-123` | 1CR23AI123 | Weather API integration and feature merging |
| `feature/data-cleaning-124` | 1CR23AI124 | Data cleaning and transformation pipeline |
| `feature/data-validation-126` | 1CR23AI126 | Data quality assertions and error logging |
| `feature/airflow-127` | 1CR23AI127 | Airflow DAGs, tasks, and scheduling logic |
| `feature/postgresql-129` | 1CR23AI129 | PostgreSQL relational schema & SQL tables |
| `feature/postgis-130` | 1CR23AI130 | PostGIS spatial queries and spatial indices |
| `feature/data-mart-131` | 1CR23AI131 | Analytical data mart views and dimension tables |
| `feature/dashboard-132` | 1CR23AI132 | Streamlit analytics, KPI metrics, charts |
| `feature/dashboard-ui-133` | 1CR23AI133 | Streamlit UI components and geospatial mapping |
| `feature/integration-135` | 1CR23AI135 | Test suites, integration pipeline, final docs |

### Creating and Switching to your Branch:
```bash
# Ensure you are on the latest main branch
git checkout main
git pull origin main

# Create and switch to your feature branch
git checkout -b feature/<your-branch-name>
```

---

## 3. Commit Message Standards

Commits must follow the **Conventional Commits** standard with clear, concise descriptions:

### Structure:
```
<type>(<scope>): <short description>

[optional longer body explaining context/rationale]
```

### Allowed Types:
- `feat`: A new feature or module capability
- `fix`: A bug fix or pipeline correction
- `docs`: Documentation updates only
- `test`: Adding or modifying automated tests
- `refactor`: Code restructuring without changing behavior
- `chore`: Repository maintenance, configuration, dependency updates

### Examples:
- `feat(ingestion): add chunked reader for UK DfT accident CSVs`
- `feat(weather): implement Open-Meteo API hourly batch extraction`
- `fix(transformation): handle missing road condition codes`
- `docs(dictionary): add column descriptions for accident severity`
- `test(validation): add unit test for coordinate range assertion`

---

## 4. Pull Request (PR) & Review Process

1. **Keep PRs Focused**: A PR should encompass work relevant only to your assigned module.
2. **Sync with Main**: Before opening a PR, rebase or merge the latest `main` branch to resolve conflicts locally.
3. **PR Description**: Include:
   - Summary of changes implemented
   - Linked task / module
   - Verification steps performed locally
   - Any schema changes or new dependencies required
4. **Code Review**: At least one peer review or Team Lead approval is required before merging.
5. **No Direct Pushes to `main`**: All code must enter `main` through a merged Pull Request.

---

## 5. Integration Rules & Safety

1. **Do Not Commit Sensitive Data**:
   - Never commit `.env` files, passwords, database connection strings, or personal access tokens.
2. **Do Not Commit Large Data Files**:
   - Raw datasets, large parquet files, and bulky CSV dumps must remain git-ignored under `data/raw/` or `data/staging/`.
3. **Modular Code Structure**:
   - Write clean, decoupled Python modules under `src/` that can be imported and executed both independently and within Airflow DAGs.
4. **Error Handling**:
   - Data pipeline modules must include defensive logging and write malformed records to an error/rejection log rather than terminating silently.

---

## 6. Definition of Done (DoD)

A task or feature branch is considered **Done** when:
1. All functional requirements for that specific module are fully implemented.
2. Code is accompanied by appropriate comments and docstrings.
3. Corresponding unit/integration tests are written and passing under `tests/`.
4. Relevant documentation in `docs/` or `sql/` is updated.
5. The branch is merged into `main` via an approved Pull Request with no merge conflicts.
