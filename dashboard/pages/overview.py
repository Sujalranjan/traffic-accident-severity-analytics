import pandas as pd
import streamlit as st

from components.filters import apply_filters, render_filters
from components.accident_map import render_accident_map


st.set_page_config(
    page_title="Accident Map",
    page_icon="🗺️",
    layout="wide",
)


def render_overview(df: pd.DataFrame):
    """
    Render the dashboard map and filtering interface.
    """

    st.title("🗺️ Accident Hotspot Map")

    st.markdown(
        """
        Explore the geographical distribution of traffic accidents
        using interactive filters and the accident location map.
        """
    )

    st.divider()

    # ---------------------------------------------------------
    # Filters
    # ---------------------------------------------------------

    selected_filters = render_filters(df)

    filtered_df = apply_filters(
        df,
        selected_filters
    )

    # ---------------------------------------------------------
    # Map information
    # ---------------------------------------------------------

    total_records = len(filtered_df)

    valid_coordinates = filtered_df.dropna(
        subset=["latitude", "longitude"]
    )

    mapped_records = len(valid_coordinates)

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label="📊 Records Displayed",
            value=f"{total_records:,}",
        )

    with col2:
        st.metric(
            label="📍 Mapped Locations",
            value=f"{mapped_records:,}",
        )

    st.divider()

    # ---------------------------------------------------------
    # Map section
    # ---------------------------------------------------------

    st.subheader("Traffic Accident Locations")

    st.caption(
        "Use the map controls to zoom, pan, and inspect accident "
        "locations. Hover over a marker for additional details."
    )

    render_accident_map(filtered_df)


def main():
    """
    Development entry point.

    The temporary dataset is kept separately in dev_data.py
    until the analytical data mart is available.
    """

    from dev_data import create_demo_data

    demo_df = create_demo_data()

    st.caption(
        "Development mode: using sample data until the "
        "analytical data mart is connected."
    )

    render_overview(demo_df)


if __name__ == "__main__":
    main()