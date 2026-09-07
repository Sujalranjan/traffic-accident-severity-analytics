import pandas as pd


def create_demo_data():
    """
    Create a small development dataset for testing
    the dashboard UI.

    This data is temporary and is not project production data.
    """

    return pd.DataFrame(
        {
            "collision_year": [
                2020, 2020, 2021, 2021, 2022,
                2022, 2023, 2023, 2024, 2024
            ],
            "collision_severity": [
                "Slight", "Serious", "Slight", "Fatal", "Serious",
                "Slight", "Fatal", "Serious", "Slight", "Serious"
            ],
            "road_type": [
                "Single carriageway",
                "Dual carriageway",
                "Single carriageway",
                "Roundabout",
                "Dual carriageway",
                "Single carriageway",
                "Single carriageway",
                "Roundabout",
                "Dual carriageway",
                "Single carriageway",
            ],
            "weather_conditions": [
                "Fine",
                "Rain",
                "Fine",
                "Fine",
                "Rain",
                "Snow",
                "Fine",
                "Rain",
                "Fine",
                "Fog or mist",
            ],
            "urban_or_rural_area": [
                "Urban",
                "Urban",
                "Rural",
                "Urban",
                "Rural",
                "Rural",
                "Urban",
                "Urban",
                "Rural",
                "Urban",
            ],
            "number_of_casualties": [
                1, 2, 1, 3, 2,
                1, 4, 2, 1, 2
            ],
            "number_of_vehicles": [
                2, 2, 1, 3, 2,
                2, 3, 2, 2, 1
            ],
            "latitude": [
                51.5074,
                52.4862,
                53.4808,
                51.4545,
                52.2053,
                53.8008,
                51.4816,
                52.9548,
                53.3811,
                50.8225,
            ],
            "longitude": [
                -0.1278,
                -1.8904,
                -2.2426,
                -2.5879,
                0.1218,
                -1.5491,
                -2.2350,
                -1.1581,
                -1.4707,
                -0.1372,
            ],
        }
    )