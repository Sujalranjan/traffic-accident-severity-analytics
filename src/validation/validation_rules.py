"""
Validation rules for cleaned traffic accident datasets.

This module defines data-quality rules for:
- Collision records
- Vehicle records
- Casualty records

The rules validate cleaned data without modifying or deleting records.
"""


# ---------------------------------------------------------
# Collision validation rules
# ---------------------------------------------------------

COLLISION_RULES = {
    "collision_index_not_null": {
        "column": "collision_index",
        "description": "Collision ID must not be null.",
    },

    "latitude_valid": {
        "column": "latitude",
        "description": "Latitude must be between -90 and 90.",
    },

    "longitude_valid": {
        "column": "longitude",
        "description": "Longitude must be between -180 and 180.",
    },

    "date_valid": {
        "column": "date",
        "description": "Accident date must be valid.",
    },

    "severity_valid": {
        "column": "collision_severity",
        "description": (
            "Collision severity must be Fatal, Serious, or Slight."
        ),
    },

    "number_of_vehicles_valid": {
        "column": "number_of_vehicles",
        "description": "Number of vehicles must be greater than or equal to 0.",
    },

    "number_of_casualties_valid": {
        "column": "number_of_casualties",
        "description": "Number of casualties must be greater than or equal to 0.",
    },
}


# ---------------------------------------------------------
# Vehicle validation rules
# ---------------------------------------------------------

VEHICLE_RULES = {
    "collision_index_not_null": {
        "column": "collision_index",
        "description": "Collision ID must not be null.",
    },

    "vehicle_reference_valid": {
        "column": "vehicle_reference",
        "description": "Vehicle reference must be greater than 0.",
    },

    "age_of_driver_valid": {
        "column": "age_of_driver",
        "description": "Driver age must be greater than or equal to 0 when present.",
    },

    "age_of_vehicle_valid": {
        "column": "age_of_vehicle",
        "description": "Vehicle age must be greater than or equal to 0 when present.",
    },
}


# ---------------------------------------------------------
# Casualty validation rules
# ---------------------------------------------------------

CASUALTY_RULES = {
    "collision_index_not_null": {
        "column": "collision_index",
        "description": "Collision ID must not be null.",
    },

    "casualty_reference_valid": {
        "column": "casualty_reference",
        "description": "Casualty reference must be greater than 0.",
    },

    "age_of_casualty_valid": {
        "column": "age_of_casualty",
        "description": "Casualty age must be greater than or equal to 0 when present.",
    },

    "casualty_severity_valid": {
        "column": "casualty_severity",
        "description": (
            "Casualty severity must be Fatal, Serious, or Slight."
        ),
    },
}


# ---------------------------------------------------------
# Allowed categorical values
# ---------------------------------------------------------

VALID_COLLISION_SEVERITIES = {
    "Fatal",
    "Serious",
    "Slight",
}


VALID_CASUALTY_SEVERITIES = {
    "Fatal",
    "Serious",
    "Slight",
}


# ---------------------------------------------------------
# Validation thresholds
# ---------------------------------------------------------

LATITUDE_MIN = -90
LATITUDE_MAX = 90

LONGITUDE_MIN = -180
LONGITUDE_MAX = 180

MIN_NON_NEGATIVE_VALUE = 0
MIN_REFERENCE_VALUE = 1