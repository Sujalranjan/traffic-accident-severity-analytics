-- Geospatial layer setup for 1CR23AI130
-- Safe to run after the base PostgreSQL database exists.
-- Does not create or modify the base relational tables owned by 1CR23AI129.

CREATE EXTENSION IF NOT EXISTS postgis;
