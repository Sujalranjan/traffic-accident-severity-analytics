CREATE TABLE IF NOT EXISTS cleaned.collisions (
    collision_index VARCHAR(50) PRIMARY KEY,
    collision_year INTEGER NOT NULL,
    collision_ref_no VARCHAR(50),

    location_easting_osgr DOUBLE PRECISION,
    location_northing_osgr DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    latitude DOUBLE PRECISION,

    police_force INTEGER NOT NULL,
    collision_severity INTEGER NOT NULL,

    number_of_vehicles INTEGER NOT NULL,
    number_of_casualties INTEGER NOT NULL,

    date DATE NOT NULL,
    day_of_week INTEGER NOT NULL,
    time TIME NOT NULL,

    local_authority_district INTEGER,
    local_authority_ons_district VARCHAR(100),
    local_authority_highway VARCHAR(100),
    local_authority_highway_current VARCHAR(100),

    first_road_class INTEGER,
    first_road_number INTEGER,
    road_type INTEGER,
    speed_limit INTEGER,

    junction_detail_historic INTEGER,
    junction_detail INTEGER,
    junction_control INTEGER,

    second_road_class INTEGER,
    second_road_number INTEGER,

    pedestrian_crossing_human_control_historic INTEGER,
    pedestrian_crossing_physical_facilities_historic INTEGER,
    pedestrian_crossing INTEGER,

    light_conditions INTEGER,
    weather_conditions INTEGER,
    road_surface_conditions INTEGER,

    special_conditions_at_site INTEGER,

    carriageway_hazards_historic INTEGER,
    carriageway_hazards INTEGER,

    urban_or_rural_area INTEGER,

    did_police_officer_attend_scene_of_accident INTEGER,

    trunk_road_flag INTEGER,

    lsoa_of_accident_location VARCHAR(50),

    enhanced_severity_collision INTEGER,
    collision_injury_based INTEGER,

    collision_adjusted_severity_serious DOUBLE PRECISION,
    collision_adjusted_severity_slight DOUBLE PRECISION
);