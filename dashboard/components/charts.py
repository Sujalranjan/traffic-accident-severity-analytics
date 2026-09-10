"""Plotly chart builders for dashboard analytics views."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


SEVERITY_COLORS = {
    "Fatal": "#c2410c",
    "Serious": "#d97706",
    "Slight": "#2563eb",
    "Unknown": "#6b7280",
}


def severity_bar(data: pd.DataFrame) -> go.Figure:
    figure = px.bar(
        data,
        x="severity",
        y="accidents",
        color="severity",
        color_discrete_map=SEVERITY_COLORS,
        text_auto=True,
        labels={"severity": "Severity", "accidents": "Accidents"},
    )
    return _finish_chart(figure, show_legend=False)


def hourly_line(data: pd.DataFrame) -> go.Figure:
    figure = px.line(
        data,
        x="hour",
        y="accidents",
        markers=True,
        labels={"hour": "Hour of day", "accidents": "Accidents"},
    )
    figure.update_xaxes(dtick=1)
    return _finish_chart(figure)


def weekday_bar(data: pd.DataFrame) -> go.Figure:
    figure = px.bar(
        data,
        x="weekday",
        y="accidents",
        text_auto=True,
        labels={"weekday": "Weekday", "accidents": "Accidents"},
    )
    return _finish_chart(figure)


def dimension_bar(data: pd.DataFrame, dimension: str, label: str) -> go.Figure:
    figure = px.bar(
        data,
        x=dimension,
        y="accidents",
        text_auto=True,
        labels={dimension: label, "accidents": "Accidents"},
    )
    figure.update_xaxes(tickangle=-25)
    return _finish_chart(figure)


def casualty_rate_bar(data: pd.DataFrame, dimension: str, label: str) -> go.Figure:
    figure = px.bar(
        data,
        x=dimension,
        y="avg_casualties",
        hover_data=["accidents", "casualties"],
        text_auto=".2f",
        labels={
            dimension: label,
            "avg_casualties": "Average casualties per accident",
            "accidents": "Accidents",
            "casualties": "Casualties",
        },
    )
    figure.update_xaxes(tickangle=-25)
    return _finish_chart(figure)


def _finish_chart(figure: go.Figure, *, show_legend: bool = True) -> go.Figure:
    figure.update_layout(
        margin={"l": 10, "r": 10, "t": 24, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=show_legend,
        height=360,
    )
    figure.update_traces(marker_line_width=0)
    return figure
