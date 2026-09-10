import pandas as pd


# ============================================================
# COLLISION / ACCIDENT MAPPINGS
# Official DfT STATS19 2024 code list
# ============================================================

COLLISION_SEVERITY_MAP = {
    1: "Fatal",
    2: "Serious",
    3: "Slight",
}

ROAD_TYPE_MAP = {
    1: "Roundabout",
    2: "One way street",
    3: "Dual carriageway",
    6: "Single carriageway",
    7: "Slip road",
    9: "Unknown",
    12: "One way street/Slip road",
}

LIGHT_CONDITIONS_MAP = {
    1: "Daylight",
    4: "Darkness - lights lit",
    5: "Darkness - lights unlit",
    6: "Darkness - no lighting",
    7: "Darkness - lighting unknown",
}

WEATHER_CONDITIONS_MAP = {
    1: "Fine no high winds",
    2: "Raining no high winds",
    3: "Snowing no high winds",
    4: "Fine + high winds",
    5: "Raining + high winds",
    6: "Snowing + high winds",
    7: "Fog or mist",
    8: "Other",
    9: "Unknown",
}

ROAD_SURFACE_CONDITIONS_MAP = {
    1: "Dry",
    2: "Wet or damp",
    3: "Snow",
    4: "Frost or ice",
    5: "Flood over 3cm deep",
    6: "Oil or diesel",
    7: "Mud",
    9: "Unknown",
}

URBAN_RURAL_MAP = {
    1: "Urban",
    2: "Rural",
    3: "Unallocated",
}


# ============================================================
# VEHICLE MAPPINGS
# Official DfT STATS19 2024 code list
# ============================================================

VEHICLE_TYPE_MAP = {
    1: "Pedal cycle",
    2: "Motorcycle 50cc and under",
    3: "Motorcycle 125cc and under",
    4: "Motorcycle over 125cc and up to 500cc",
    5: "Motorcycle over 500cc",
    8: "Taxi/Private hire car",
    9: "Car",
    10: "Minibus (8 - 16 passenger seats)",
    11: "Bus or coach (17 or more pass seats)",
    16: "Ridden horse",
    17: "Agricultural vehicle",
    18: "Tram",
    19: "Van / Goods 3.5 tonnes mgw or under",
    20: "Goods over 3.5t. and under 7.5t",
    21: "Goods 7.5 tonnes mgw and over",
    22: "Mobility scooter",
    23: "Electric motorcycle",
    90: "Other vehicle",
    97: "Motorcycle - unknown cc",
    98: "Goods vehicle - unknown weight",
    99: "Unknown vehicle type (self rep only)",

    # Historical codes retained for compatibility
    103: "Motorcycle - Scooter (1979-1998)",
    104: "Motorcycle (1979-1998)",
    105: "Motorcycle - Combination (1979-1998)",
    106: "Motorcycle over 125cc (1999-2004)",
    108: "Taxi (excluding private hire cars) (1979-2004)",
    109: "Car (including private hire cars) (1979-2004)",
    110: "Minibus/Motor caravan (1979-1998)",
    113: "Goods over 3.5 tonnes (1979-1998)",
}


SEX_OF_DRIVER_MAP = {
    1: "Male",
    2: "Female",
    3: "Not known",
}


AGE_BAND_OF_DRIVER_MAP = {
    1: "0 - 5",
    2: "6 - 10",
    3: "11 - 15",
    4: "16 - 20",
    5: "21 - 25",
    6: "26 - 35",
    7: "36 - 45",
    8: "46 - 55",
    9: "56 - 65",
    10: "66 - 75",
    11: "Over 75",
}


PROPULSION_CODE_MAP = {
    1: "Petrol",
    2: "Heavy oil",
    3: "Electric",
    4: "Steam",
    5: "Gas",
    6: "Petrol/Gas (LPG)",
    7: "Gas/Bi-fuel",
    8: "Hybrid electric",
    9: "Gas Diesel",
    10: "New fuel technology",
    11: "Fuel cells",
    12: "Electric diesel",
}


# ============================================================
# CASUALTY MAPPINGS
# Official DfT STATS19 2024 code list
# ============================================================

CASUALTY_CLASS_MAP = {
    1: "Driver or rider",
    2: "Passenger",
    3: "Pedestrian",
}

SEX_OF_CASUALTY_MAP = {
    1: "Male",
    2: "Female",
    9: "unknown (self reported)",
}

AGE_BAND_OF_CASUALTY_MAP = {
    1: "0 - 5",
    2: "6 - 10",
    3: "11 - 15",
    4: "16 - 20",
    5: "21 - 25",
    6: "26 - 35",
    7: "36 - 45",
    8: "46 - 55",
    9: "56 - 65",
    10: "66 - 75",
    11: "Over 75",
}

CASUALTY_SEVERITY_MAP = {
    1: "Fatal",
    2: "Serious",
    3: "Slight",
}

CASUALTY_TYPE_MAP = {
    0: "Pedestrian",
    1: "Cyclist",
    2: "Motorcycle 50cc and under rider or passenger",
    3: "Motorcycle 125cc and under rider or passenger",
    4: "Motorcycle over 125cc and up to 500cc rider or passenger",
    5: "Motorcycle over 500cc rider or passenger",
    8: "Taxi/Private hire car occupant",
    9: "Car occupant",
    10: "Minibus (8 - 16 passenger seats) occupant",
    11: "Bus or coach occupant (17 or more pass seats)",
    16: "Horse rider",
    17: "Agricultural vehicle occupant",
    18: "Tram occupant",
    19: "Van / Goods vehicle (3.5 tonnes mgw or under) occupant",
    20: "Goods vehicle (over 3.5t. and under 7.5t.) occupant",
    21: "Goods vehicle (7.5 tonnes mgw and over) occupant",
    22: "Mobility scooter rider",
    23: "Electric motorcycle rider or passenger",
    90: "Other vehicle occupant",
    97: "Motorcycle - unknown cc rider or passenger",
    98: "Goods vehicle (unknown weight) occupant",
    99: "Unknown vehicle type (self rep only)",

    # Historical codes
    103: "Motorcycle - Scooter (1979-1998)",
    104: "Motorcycle (1979-1998)",
    105: "Motorcycle - Combination (1979-1998)",
    106: "Motorcycle over 125cc (1999-2004)",
    108: "Taxi (excluding private hire cars) (1979-2004)",
    109: "Car (including private hire cars) (1979-2004)",
    110: "Minibus/Motor caravan (1979-1998)",
    113: "Goods over 3.5 tonnes (1979-1998)",
}


# ============================================================
# STANDARDIZATION FUNCTIONS
# ============================================================

def standardize_date(df: pd.DataFrame) -> pd.DataFrame:
    """Convert accident date to pandas datetime."""

    df["date"] = pd.to_datetime(
        df["date"],
        dayfirst=True,
        errors="coerce"
    )

    return df


def standardize_time(df: pd.DataFrame) -> pd.DataFrame:
    """Convert accident time to HH:MM:SS."""

    df["time"] = pd.to_datetime(
        df["time"],
        format="%H:%M",
        errors="coerce"
    ).dt.strftime("%H:%M:%S")

    return df


def standardize_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    """Convert coordinates to numeric and remove impossible values."""

    df["latitude"] = pd.to_numeric(
        df["latitude"],
        errors="coerce"
    )

    df["longitude"] = pd.to_numeric(
        df["longitude"],
        errors="coerce"
    )

    df.loc[
        ~df["latitude"].between(-90, 90),
        "latitude"
    ] = pd.NA

    df.loc[
        ~df["longitude"].between(-180, 180),
        "longitude"
    ] = pd.NA

    return df


def standardize_missing_codes(df: pd.DataFrame) -> pd.DataFrame:
    """Convert DfT -1 missing/out-of-range codes to pandas NA."""

    columns = [
        "road_type",
        "speed_limit",
        "light_conditions",
        "weather_conditions",
        "road_surface_conditions",
        "urban_or_rural_area",
        "vehicle_type",
        "sex_of_driver",
        "age_of_driver",
        "age_band_of_driver",
        "propulsion_code",
        "casualty_class",
        "sex_of_casualty",
        "age_of_casualty",
        "age_band_of_casualty",
        "casualty_severity",
        "casualty_type",
    ]

    for column in columns:
        if column in df.columns:
            df[column] = df[column].replace(-1, pd.NA)

    return df


def standardize_categories(df: pd.DataFrame) -> pd.DataFrame:
    """Convert official DfT numeric category codes to readable labels."""

    mappings = {
        "collision_severity": COLLISION_SEVERITY_MAP,
        "road_type": ROAD_TYPE_MAP,
        "light_conditions": LIGHT_CONDITIONS_MAP,
        "weather_conditions": WEATHER_CONDITIONS_MAP,
        "road_surface_conditions": ROAD_SURFACE_CONDITIONS_MAP,
        "urban_or_rural_area": URBAN_RURAL_MAP,
    }

    for column, mapping in mappings.items():
        if column in df.columns:
            df[column] = df[column].map(mapping)

    return df


def standardize_vehicle_categories(df: pd.DataFrame) -> pd.DataFrame:
    """Convert vehicle category codes to readable labels."""

    mappings = {
        "vehicle_type": VEHICLE_TYPE_MAP,
        "sex_of_driver": SEX_OF_DRIVER_MAP,
        "age_band_of_driver": AGE_BAND_OF_DRIVER_MAP,
        "propulsion_code": PROPULSION_CODE_MAP,
    }

    for column, mapping in mappings.items():
        if column in df.columns:
            df[column] = df[column].map(mapping)

    return df


def standardize_casualty_categories(df: pd.DataFrame) -> pd.DataFrame:
    """Convert casualty category codes to readable labels."""

    mappings = {
        "casualty_class": CASUALTY_CLASS_MAP,
        "sex_of_casualty": SEX_OF_CASUALTY_MAP,
        "age_band_of_casualty": AGE_BAND_OF_CASUALTY_MAP,
        "casualty_severity": CASUALTY_SEVERITY_MAP,
        "casualty_type": CASUALTY_TYPE_MAP,
    }

    for column, mapping in mappings.items():
        if column in df.columns:
            df[column] = df[column].map(mapping)

    return df