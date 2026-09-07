-- Spatial indexes for the geospatial layer (1CR23AI130)
-- Run after the geometry columns described in schema_contract.sql exist.

-- GIST index for collision point lookups (bounding box and radius queries)
CREATE INDEX IF NOT EXISTS idx_collisions_geom_gist
    ON collisions
    USING GIST (geom)
    WHERE geom IS NOT NULL;

-- GIST index for hotspot grid centroids
CREATE INDEX IF NOT EXISTS idx_spatial_hotspot_grid_geom_gist
    ON spatial_hotspot_grid
    USING GIST (geom)
    WHERE geom IS NOT NULL;
