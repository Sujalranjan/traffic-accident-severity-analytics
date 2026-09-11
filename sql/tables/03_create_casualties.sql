CREATE TABLE IF NOT EXISTS cleaned.casualties (
    collision_index VARCHAR(50) NOT NULL,
    collision_year INTEGER NOT NULL,
    collision_ref_no VARCHAR(50),

    vehicle_reference INTEGER NOT NULL,
    casualty_reference INTEGER NOT NULL,

    casualty_class INTEGER,
    sex_of_casualty INTEGER,
    age_of_casualty INTEGER,
    age_band_of_casualty INTEGER,

    casualty_severity INTEGER,

    pedestrian_location INTEGER,
    pedestrian_movement INTEGER,

    car_passenger INTEGER,
    bus_or_coach_passenger INTEGER,

    pedestrian_road_maintenance_worker INTEGER,

    casualty_type INTEGER,

    casualty_imd_decile INTEGER,

    lsoa_of_casualty VARCHAR(50),

    enhanced_casualty_severity INTEGER,
    casualty_injury_based INTEGER,

    casualty_adjusted_severity_serious DOUBLE PRECISION,
    casualty_adjusted_severity_slight DOUBLE PRECISION,

    casualty_distance_banding INTEGER,

    PRIMARY KEY (
        collision_index,
        vehicle_reference,
        casualty_reference
    ),

    CONSTRAINT fk_casualty_vehicle
        FOREIGN KEY (
            collision_index,
            vehicle_reference
        )
        REFERENCES cleaned.vehicles (
            collision_index,
            vehicle_reference
        )
);