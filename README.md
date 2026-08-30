# Traffic Accident Severity Analytics and Prediction

## Project Overview

This repository hosts the **Traffic Accident Severity Analytics and Prediction** project. The primary objective is to build an end-to-end data engineering and analytics platform that ingests, cleans, enriches, validates, stores, and visualizes road traffic accident data combined with historical meteorological conditions to uncover critical factors influencing accident severity.

> **Scope Notice (Part 1 Only)**:
> The current development scope is strictly limited to **Part 1: Data Engineering and Analytics**.
> 
> *Part 2 (Machine Learning modeling, MLflow tracking, model registry, FastAPI serving, Dockerized model deployment, drift detection, and automated retraining) is explicitly out of scope at this stage and will be implemented in a subsequent phase.*

---

## Part 1 Architecture

The data pipeline integrates accident records with weather telemetry through a multi-tier data engineering architecture:

```
┌────────────────────────────────────────┐       ┌─────────────────────────────────────┐
│  UK DfT Road Safety Open Data Source   │       │  Open-Meteo Historical Weather API │
└───────────────────┬────────────────────┘       └──────────────────┬──────────────────┘
                    │                                               │
                    └───────────────────────┬───────────────────────┘
                                            ▼
                                  ┌───────────────────┐
                                  │  Raw Data Layer   │
                                  └─────────┬─────────┘
                                            │
                                            ▼
                                 ┌─────────────────────┐
                                 │   Apache Airflow    │
                                 │ (ETL Orchestration) │
                                 └──────────┬──────────┘
                                            │
                                            ▼
                                  ┌───────────────────┐
                                  │   Staging Layer   │
                                  └─────────┬─────────┘
                                            │
                                            ▼
                                ┌───────────────────────┐
                                │ Cleaning & Validation │
                                │ (Error & DQ Logging)  │
                                └───────────┬───────────┘
                                            │
                                            ▼
                                ┌───────────────────────┐
                                │  PostgreSQL / PostGIS │
                                │ (Spatial & Relational)│
                                └───────────┬───────────┘
                                            │
                                            ▼
                                ┌───────────────────────┐
                                │ Analytical Data Mart  │
                                │ (Dimensional Schema)  │
                                └───────────┬───────────┘
                                            │
                                            ▼
                                ┌───────────────────────┐
                                │  Streamlit Dashboard  │
                                │ (Interactive Insights)│
                                └───────────────────────┘
```

---

## Data Sources

1. **Primary Accident Data**: UK Department for Transport (DfT) Road Safety Open Data
   - Contains comprehensive road safety records including accident severity, collision circumstances, road conditions, speed limits, vehicle types, and casualty details with geospatial coordinates.
2. **Meteorological Data**: Open-Meteo Historical Weather API
   - Supplies hourly historical weather parameters corresponding to collision timestamps and locations (precipitation, temperature, visibility, surface conditions, wind speed).

---

## Technology Stack

- **Programming & Analysis**: Python, Pandas, NumPy
- **API & Networking**: Requests
- **Database & Spatial Engine**: PostgreSQL, PostGIS, SQLAlchemy, psycopg2-binary
- **Geospatial Processing**: GeoPandas, Shapely
- **Workflow & Orchestration**: Apache Airflow
- **Visualization & Dashboard**: Streamlit, Plotly
- **Version Control & Collaboration**: Git, GitHub
- **Testing & Quality Assurance**: Pytest

---

## Team Members & Responsibilities

| USN | Role / Responsibility | Scope of Work |
| :--- | :--- | :--- |
| **1CR23AI119** *(Lead)* | Dataset Acquisition & Research | Acquisition strategy, dataset schema documentation, data provenance. |
| **1CR23AI121** | Accident Data Ingestion | Raw accident data extraction, file handling, initial ingestion pipeline. |
| **1CR23AI123** | Weather Data Integration | Open-Meteo API ingestion, hourly weather enrichment, API caching. |
| **1CR23AI124** | Data Cleaning & Standardization | Data cleansing, type casting, missing value handling, standard schemas. |
| **1CR23AI126** | Data Quality & Validation | Validation rules, threshold checks, rejected record logging. |
| **1CR23AI127** | Apache Airflow Orchestration | DAG design, task scheduling, dependency management, pipeline retry logic. |
| **1CR23AI129** | PostgreSQL Database | Relational database schema, table definitions, indexing, connection pooling. |
| **1CR23AI130** | PostGIS & Geospatial Processing | Spatial extensions, coordinate reference systems, geospatial indexing, queries. |
| **1CR23AI131** | Analytical Data Mart | Dimensional modeling (star/snowflake schema), fact and dimension tables, marts. |
| **1CR23AI132** | Dashboard Analytics | Metric calculations, aggregation views (hour, day, road type, weather), KPIs. |
| **1CR23AI133** | Dashboard Map & UI | Streamlit interface, geospatial accident density mapping, Plotly charts. |
| **1CR23AI135** | Integration, Testing & Documentation | End-to-end integration testing, test suites, architecture documentation, reporting. |

---

## Repository Structure

```
traffic-accident-severity-analytics/
├── .env.example               # Environment variable configuration template
├── .gitignore                  # Git ignore rules for caches, secrets, and large datasets
├── README.md                   # Project overview, architecture, and team guide
├── requirements.txt            # Python package dependencies
│
├── airflow/
│   └── dags/                   # Apache Airflow DAG definitions and pipeline schedules
│
├── dashboard/
│   ├── components/             # Reusable Streamlit UI components and chart widgets
│   └── pages/                  # Multi-page dashboard views and analytical interfaces
│
├── data/
│   ├── raw/                    # Untouched initial raw datasets (git-ignored)
│   ├── staging/                # Intermediate transformed and joined data (git-ignored)
│   └── processed/              # Cleaned, validated, and analytical-ready datasets
│
├── docs/
│   ├── architecture/           # System architecture diagrams and technical design documents
│   ├── data_dictionary/        # Data field definitions, data types, and allowed values
│   ├── dataset/                # Dataset source metadata, citations, and research notes
│   ├── screenshots/            # Evidence of execution, dashboard views, and test runs
│   └── validation/             # Data quality rules and rejected record schemas
│
├── report/                     # Academic and technical reports, presentations, and submissions
│
├── sql/
│   ├── dimensions/             # Dimension table definitions (e.g., date, weather, road)
│   ├── facts/                  # Fact table definitions (e.g., fact_accidents)
│   ├── marts/                  # Analytical data mart views and aggregation tables
│   ├── schemas/                # Database schema creation scripts
│   └── tables/                 # Base database table definitions
│
├── src/
│   ├── geospatial/             # PostGIS integration, coordinate transformations, and spatial queries
│   ├── ingestion/              # Accident data extraction and ingestion scripts
│   ├── transformation/         # Cleaning, normalization, and feature standardization logic
│   ├── validation/             # Data quality assertion functions and rejected record loggers
│   └── weather/                # Open-Meteo API fetching and weather joining logic
│
└── tests/                      # Automated unit, integration, and data validation tests
```

---

## Git Workflow & Collaboration Guidelines

To ensure stable and organized collaboration, the team follows a structured Git branching workflow:

```
main (stable, production-ready branch)
  │
  ├─── feature branch (e.g., feature/accident-ingestion-121)
  │      │
  │      ├── local development & testing
  │      ├── granular, descriptive commits
  │      └── push to remote feature branch
  │
  └─── Pull Request (PR) -> Code Review -> Merge to main
```

### Collaboration Rules:
1. **`main` is protected**: Direct commits to `main` are strictly prohibited.
2. **Feature Branching**: Every member must work in their dedicated feature branch named according to standard convention (e.g., `feature/<task-name>-<usn>`).
3. **Pull Requests & Code Reviews**: All changes must be merged into `main` via a Pull Request reviewed by the team lead or a peer.
4. **Descriptive Commits**: Use conventional commits (e.g., `feat:`, `fix:`, `docs:`, `test:`, `chore:`).
5. **No Secrets**: Never commit `.env` files, passwords, or API credentials.
6. **No Large Raw Datasets**: Do not commit large binary/raw data dumps to GitHub. Use the ingestion scripts to download or place files locally in `data/raw/`.

---

## Environment Setup & Getting Started

### 1. Prerequisites
- Python 3.10+ (or compatible version)
- PostgreSQL with PostGIS extension enabled
- Git

### 2. Environment Configuration
Copy the environment template and configure your local environment variables:
```bash
cp .env.example .env
```

### 3. Dependency Installation
Create a virtual environment and install the required dependencies:
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```
*(Note: Apache Airflow installation on local environments may require specific constraint files depending on your OS and Python version).*
