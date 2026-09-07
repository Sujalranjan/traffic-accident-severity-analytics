-- SQL contract for coordination with 1CR23AI129 (PostgreSQL Database)
--
-- 1CR23AI129 owns the base relational schema for collisions, vehicles,
-- and casualties. This file documents the additional objects required
-- by the geospatial module (1CR23AI130) without redesigning base tables.

-- ------------------------------------------------------------------
-- 1. Geometry column on the existing collisions table
-- ------------------------------------------------------------------
-- Add after the base collisions table is created and loaded.
--
-- ALTER TABLE collisions
--     ADD COLUMN IF NOT EXISTS geom geometry(Point, 4326);
--
-- COMMENT ON COLUMN collisions.geom IS
--     'WGS84 point geometry built from longitude/latitude by geospatial pipeline';

-- ------------------------------------------------------------------
-- 2. Hotspot grid table owned by the geospatial layer
-- ------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS spatial_hotspot_grid (
    grid_cell_id   TEXT PRIMARY KEY,
    grid_lon       DOUBLE PRECISION NOT NULL,
    grid_lat       DOUBLE PRECISION NOT NULL,
    geom           geometry(Point, 4326),
    accident_count INTEGER NOT NULL CHECK (accident_count >= 1),
    hotspot_score  DOUBLE PRECISION NOT NULL CHECK (hotspot_score >= 0 AND hotspot_score <= 1),
    computed_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE spatial_hotspot_grid IS
    'Grid-based accident hotspot cells produced by src/geospatial/hotspot_analysis.py';

-- ------------------------------------------------------------------
-- 3. Example geometry update for one validated collision row
-- ------------------------------------------------------------------
-- UPDATE collisions
-- SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
-- WHERE collision_index = :collision_index
--   AND latitude IS NOT NULL
--   AND longitude IS NOT NULL;

-- ------------------------------------------------------------------
-- 4. Downstream expectations
-- ------------------------------------------------------------------
-- 1CR23AI131 can join fact/mart models to spatial_hotspot_grid using
-- grid_cell_id or by snapping collision geometry to the same grid size.
-- 1CR23AI133 can query latitude/longitude, accident_count, hotspot_score
-- from mart views built on top of this table.
