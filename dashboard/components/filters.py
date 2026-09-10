import pandas as pd
import streamlit as st


def render_filters(df: pd.DataFrame):
    """
    Render the dashboard filters in the Streamlit sidebar.

    The available filter options are generated from the data
    provided to the dashboard.
    """

    st.sidebar.header("🔎 Dashboard Filters")

    if df.empty:
        st.sidebar.info("No data available for filtering.")
        return {}

    filters = {}

    # ---------------------------------------------------------
    # Reset filters
    # ---------------------------------------------------------

    if st.sidebar.button(
        "↻ Reset Filters",
        use_container_width=True
    ):
        for key in [
            "accident_year_filter",
            "severity_filter",
            "road_type_filter",
            "weather_filter",
            "area_filter",
        ]:
            st.session_state.pop(key, None)

        st.rerun()

    st.sidebar.divider()

    # ---------------------------------------------------------
    # Accident Year
    # ---------------------------------------------------------

    if "collision_year" in df.columns:

        years = sorted(
            df["collision_year"]
            .dropna()
            .unique()
            .tolist()
        )

        if years:
            filters["collision_year"] = st.sidebar.multiselect(
                "📅 Accident Year",
                options=years,
                default=years,
                key="accident_year_filter",
            )

    # ---------------------------------------------------------
    # Accident Severity
    # ---------------------------------------------------------

    if "collision_severity" in df.columns:

        severity = sorted(
            df["collision_severity"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        if severity:
            filters["collision_severity"] = st.sidebar.multiselect(
                "⚠️ Accident Severity",
                options=severity,
                default=severity,
                key="severity_filter",
            )

    # ---------------------------------------------------------
    # Road Type
    # ---------------------------------------------------------

    if "road_type" in df.columns:

        road_types = sorted(
            df["road_type"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        if road_types:
            filters["road_type"] = st.sidebar.multiselect(
                "🛣️ Road Type",
                options=road_types,
                default=road_types,
                key="road_type_filter",
            )

    # ---------------------------------------------------------
    # Weather Conditions
    # ---------------------------------------------------------

    if "weather_conditions" in df.columns:

        weather = sorted(
            df["weather_conditions"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        if weather:
            filters["weather_conditions"] = st.sidebar.multiselect(
                "🌦️ Weather Conditions",
                options=weather,
                default=weather,
                key="weather_filter",
            )

    # ---------------------------------------------------------
    # Urban / Rural Area
    # ---------------------------------------------------------

    if "urban_or_rural_area" in df.columns:

        areas = sorted(
            df["urban_or_rural_area"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        if areas:
            filters["urban_or_rural_area"] = st.sidebar.multiselect(
                "📍 Area Type",
                options=areas,
                default=areas,
                key="area_filter",
            )

    return filters


def apply_filters(
    df: pd.DataFrame,
    filters: dict
) -> pd.DataFrame:
    """
    Apply the selected dashboard filters to the accident data.

    A filter with no selected values produces an empty result.
    """

    filtered_df = df.copy()

    for column, selected_values in filters.items():

        if column not in filtered_df.columns:
            continue

        if not selected_values:
            return filtered_df.iloc[0:0]

        filtered_df = filtered_df[
            filtered_df[column].isin(selected_values)
        ]

    return filtered_df