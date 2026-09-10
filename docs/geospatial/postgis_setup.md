# PostGIS Geospatial Setup

This document describes the geospatial layer implemented by **1CR23AI130**
for the Traffic Accident Severity Analytics project.

## PostGIS requirement

The project stores collision locations as spatial points in PostgreSQL using
the **PostGIS** extension. PostGIS must be installed on the PostgreSQL
server before running the geospatial SQL scripts.

Enable the extension with:

```bash
psql -d traffic_analytics -f sql/geospatial/enable_postgis.sql
```

## Coordinate reference system

The UK DfT collision dataset provides:

- `latitude`
- `longitude`

These values are stored and queried in **EPSG:4326 (WGS 84)**.

Geometry is represented as:

```sql
ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
```

Important: PostGIS `POINT` uses **X = longitude** and **Y = latitude**.

## Geometry representation

The geospatial Python module builds Shapely points and EWKT strings such as:

```text
SRID=4326;POINT(-0.1278 51.5074)
```

The base relational `collisions` table is owned by **1CR23AI129**. The
geospatial layer adds a nullable geometry column through the documented
contract in:

```text
sql/geospatial/schema_contract.sql
```

Rows with missing or invalid coordinates remain in the source table but
do not receive a geometry value.

## Spatial index requirement

Spatial queries such as bounding-box and radius searches rely on a **GIST**
index on the geometry column:

```bash
psql -d traffic_analytics -f sql/geospatial/spatial_indexes.sql
```

Without the GIST index, map and hotspot queries become much slower on the
full collision dataset (~514k rows).

## Python module layout

```text
src/geospatial/
├── coordinates.py        # Validate latitude/longitude
├── geometry_builder.py   # Build WGS84 point geometries
├── spatial_queries.py    # PostGIS bounding-box and radius queries
└── hotspot_analysis.py   # Grid-based hotspot aggregation
```

## How the spatial functions are used

### 1. Coordinate validation

```python
from geospatial.coordinates import validate_coordinates_batch

valid_df, rejected_df = validate_coordinates_batch(collision_df)
```

Invalid rows are flagged, not deleted.

### 2. Geometry creation

```python
from geospatial.geometry_builder import build_geometries_batch

valid_geometries, rejected = build_geometries_batch(collision_df)
```

Each valid row receives a Shapely point and EWKT value for database loading.

### 3. Spatial queries

```python
from geospatial.spatial_queries import BoundingBox, query_by_bounding_box

bbox = BoundingBox(min_lon=-3.0, min_lat=50.0, max_lon=-1.0, max_lat=55.0)
accidents = query_by_bounding_box(bbox)
```

Radius search:

```python
from geospatial.spatial_queries import query_within_radius

nearby = query_within_radius(center_lon=-2.24, center_lat=53.48, radius_meters=1000)
```

Connection settings are read from `.env`:

- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`

### 4. Hotspot analysis

```python
from geospatial.hotspot_analysis import compute_hotspot_grid

hotspots = compute_hotspot_grid(valid_df, grid_size_deg=0.01)
```

Each grid cell returns:

- `grid_cell_id`
- `latitude` / `longitude` (cell centroid)
- `accident_count`
- `hotspot_score` (normalized from 0 to 1)

The same logic can be refreshed in PostgreSQL using
`refresh_hotspot_grid()` after **1CR23AI129** creates
`spatial_hotspot_grid`.

## Coordination with other team members

| Team member | Responsibility |
|---|---|
| 1CR23AI129 | Base PostgreSQL tables and collision data load |
| 1CR23AI130 | PostGIS geometry, spatial queries, hotspot grid |
| 1CR23AI131 | Analytical data mart built from hotspot outputs |
| 1CR23AI133 | Dashboard map consuming mart latitude/longitude and hotspot fields |

## Running tests

```bash
pytest tests/test_coordinates.py tests/test_geometry_builder.py tests/test_hotspot_analysis.py tests/test_spatial_queries.py -v
```

Tests cover valid coordinates, invalid latitude/longitude, missing
coordinates, geometry creation, and hotspot counting.
