import pandas as pd
import plotly.express as px
import streamlit as st


def _prepare_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare latitude and longitude values for mapping.
    """

    map_df = df.copy()

    map_df["latitude"] = pd.to_numeric(
        map_df["latitude"],
        errors="coerce"
    )

    map_df["longitude"] = pd.to_numeric(
        map_df["longitude"],
        errors="coerce"
    )

    # Keep only valid coordinate values.
    map_df = map_df.dropna(
        subset=["latitude", "longitude"]
    )

    # Basic geographic validation for the UK dataset.
    map_df = map_df[
        map_df["latitude"].between(-90, 90)
        & map_df["longitude"].between(-180, 180)
    ]

    return map_df


def _build_hover_data(df: pd.DataFrame) -> dict:
    """
    Build hover information using only columns available
    in the supplied analytical dataset.
    """

    hover_data = {}

    optional_columns = [
        "collision_index",
        "collision_severity",
        "collision_year",
        "number_of_casualties",
        "number_of_vehicles",
        "road_type",
        "weather_conditions",
        "road_surface_conditions",
        "urban_or_rural_area",
        "accident_count",
        "hotspot_score",
    ]

    for column in optional_columns:
        if column in df.columns:
            hover_data[column] = True

    return hover_data


def render_accident_map(
    df: pd.DataFrame,
    map_height: int = 600
):
    """
    Render the interactive traffic accident map.

    The function is intentionally presentation-focused.
    Geospatial processing and hotspot calculations belong
    to the project's geospatial/data-mart layers.
    """

    if df.empty:
        st.warning(
            "No accidents match the selected filters."
        )
        return

    required_columns = {
        "latitude",
        "longitude",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        st.error(
            "Map cannot be displayed because the data is missing "
            "required geographical columns: "
            + ", ".join(sorted(missing_columns))
        )
        return

    map_df = _prepare_coordinates(df)

    if map_df.empty:
        st.warning(
            "No valid geographical coordinates are available "
            "for the selected data."
        )
        return

    hover_data = _build_hover_data(map_df)

    # ---------------------------------------------------------
    # Use hotspot counts when the geospatial/data-mart layer
    # provides them.
    # ---------------------------------------------------------

    if "accident_count" in map_df.columns:

        map_df["accident_count"] = pd.to_numeric(
            map_df["accident_count"],
            errors="coerce"
        )

        map_df["accident_count"] = (
            map_df["accident_count"].fillna(1)
        )

        fig = px.scatter_map(
            map_df,
            lat="latitude",
            lon="longitude",
            size="accident_count",
            color=(
                "collision_severity"
                if "collision_severity" in map_df.columns
                else None
            ),
            hover_data=hover_data,
            center={
                "lat": 54.5,
                "lon": -3.0,
            },
            zoom=5,
            height=map_height,
            title="Traffic Accident Hotspots",
            size_max=30,
        )

    # ---------------------------------------------------------
    # Otherwise display individual accident locations.
    # ---------------------------------------------------------

    else:

        fig = px.scatter_map(
            map_df,
            lat="latitude",
            lon="longitude",
            color=(
                "collision_severity"
                if "collision_severity" in map_df.columns
                else None
            ),
            hover_data=hover_data,
            center={
                "lat": 54.5,
                "lon": -3.0,
            },
            zoom=5,
            height=map_height,
            title="Traffic Accident Locations",
        )

    # ---------------------------------------------------------
    # Marker appearance.
    # ---------------------------------------------------------

    fig.update_traces(
        marker={
            "size": 9,
            "opacity": 0.70,
        }
    )

    # ---------------------------------------------------------
    # Map layout.
    # ---------------------------------------------------------

    fig.update_layout(
        margin={
            "l": 0,
            "r": 0,
            "t": 50,
            "b": 0,
        },
        legend_title_text="Accident Severity",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )