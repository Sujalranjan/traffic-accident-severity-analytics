"""KPI rendering helpers for the Streamlit dashboard."""

from __future__ import annotations

import streamlit as st


def render_kpi_cards(metrics: dict[str, float | int]) -> None:
    """Render top-level dashboard KPI values."""

    columns = st.columns(5)
    columns[0].metric("Total accidents", f"{metrics['total_accidents']:,}")
    columns[1].metric("Fatal", f"{metrics['fatal_accidents']:,}")
    columns[2].metric("Serious", f"{metrics['serious_accidents']:,}")
    columns[3].metric("Total casualties", f"{metrics['total_casualties']:,}")
    columns[4].metric(
        "Avg casualties",
        f"{metrics['avg_casualties_per_accident']:.2f}",
    )
