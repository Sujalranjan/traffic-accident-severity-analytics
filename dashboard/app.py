import streamlit as st


st.set_page_config(
    page_title="Traffic Accident Analytics",
    page_icon="🚗",
    layout="wide",
)


def main():
    st.title("🚗 Traffic Accident Severity Analytics")

    st.markdown(
        """
        ### Traffic Accident Severity Analytics

        An interactive dashboard for exploring traffic accident
        patterns, geographical distribution, and accident hotspots.
        """
    )

    st.divider()

    st.subheader("Dashboard")

    st.write(
        """
        Use the navigation menu on the left to open the
        **Accident Hotspot Map** and explore accident locations
        using interactive filters.
        """
    )

    st.info(
        "Development mode: the dashboard currently uses "
        "sample data. The final version will use the project's "
        "analytical data mart."
    )


if __name__ == "__main__":
    main()