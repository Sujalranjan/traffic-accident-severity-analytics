CREATE INDEX IF NOT EXISTS idx_collisions_date
ON cleaned.collisions(date);

CREATE INDEX IF NOT EXISTS idx_collisions_severity
ON cleaned.collisions(collision_severity);

CREATE INDEX IF NOT EXISTS idx_collisions_weather
ON cleaned.collisions(weather_conditions);

CREATE INDEX IF NOT EXISTS idx_collisions_road_type
ON cleaned.collisions(road_type);

CREATE INDEX IF NOT EXISTS idx_collisions_day
ON cleaned.collisions(day_of_week);

CREATE INDEX IF NOT EXISTS idx_collisions_year
ON cleaned.collisions(collision_year);

CREATE INDEX IF NOT EXISTS idx_vehicles_collision
ON cleaned.vehicles(collision_index);

CREATE INDEX IF NOT EXISTS idx_casualties_collision
ON cleaned.casualties(collision_index);