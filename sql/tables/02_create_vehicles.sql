CREATE TABLE IF NOT EXISTS cleaned.vehicles (
    collision_index VARCHAR(50) NOT NULL,
    collision_year INTEGER NOT NULL,
    collision_ref_no VARCHAR(50),

    vehicle_reference INTEGER NOT NULL,

    vehicle_type INTEGER,
    towing_and_articulation INTEGER,

    vehicle_manoeuvre_historic INTEGER,
    vehicle_manoeuvre INTEGER,

    vehicle_direction_from INTEGER,
    vehicle_direction_to INTEGER,

    vehicle_location_restricted_lane_historic INTEGER,
    vehicle_location_restricted_lane INTEGER,

    junction_location INTEGER,

    skidding_and_overturning INTEGER,
    hit_object_in_carriageway INTEGER,
    vehicle_leaving_carriageway INTEGER,
    hit_object_off_carriageway INTEGER,

    first_point_of_impact INTEGER,

    vehicle_left_hand_drive INTEGER,

    journey_purpose_of_driver_historic INTEGER,
    journey_purpose_of_driver INTEGER,

    sex_of_driver INTEGER,
    age_of_driver INTEGER,
    age_band_of_driver INTEGER,

    engine_capacity_cc INTEGER,

    propulsion_code INTEGER,

    age_of_vehicle INTEGER,

    generic_make_model VARCHAR(200),

    driver_imd_decile INTEGER,

    lsoa_of_driver VARCHAR(50),

    escooter_flag INTEGER,

    driver_distance_banding INTEGER,

    PRIMARY KEY (collision_index, vehicle_reference),

    CONSTRAINT fk_vehicle_collision
        FOREIGN KEY (collision_index)
        REFERENCES cleaned.collisions(collision_index)
);