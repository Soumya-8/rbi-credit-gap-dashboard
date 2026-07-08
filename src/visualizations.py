"""Plotly chart builders for the dashboard."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config import THEME_TEMPLATE


def line_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    color: str | None,
    title: str,
    labels: dict[str, str] | None = None,
) -> go.Figure:
    """Create a line chart with markers and hover labels."""
    fig = px.line(df, x=x, y=y, color=color, markers=True, title=title, labels=labels, template=THEME_TEMPLATE)
    fig.update_layout(hovermode="x unified", margin=dict(l=10, r=10, t=55, b=10))
    return fig


def bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: str | None = None,
    orientation: str = "v",
) -> go.Figure:
    """Create a bar chart."""
    fig = px.bar(df, x=x, y=y, color=color, title=title, orientation=orientation, template=THEME_TEMPLATE)
    fig.update_traces(hovertemplate="%{x}<br>%{y:,.2f}<extra></extra>")
    fig.update_layout(margin=dict(l=10, r=10, t=55, b=10))
    return fig


def stacked_bar(df: pd.DataFrame, x: str, y: str, color: str, title: str) -> go.Figure:
    """Create a stacked bar chart."""
    fig = px.bar(df, x=x, y=y, color=color, title=title, template=THEME_TEMPLATE)
    fig.update_layout(barmode="stack", hovermode="x unified", margin=dict(l=10, r=10, t=55, b=10))
    return fig


def pie_chart(df: pd.DataFrame, names: str, values: str, title: str) -> go.Figure:
    """Create a donut chart."""
    fig = px.pie(df, names=names, values=values, hole=0.45, title=title, template=THEME_TEMPLATE)
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(margin=dict(l=10, r=10, t=55, b=10))
    return fig


def treemap(df: pd.DataFrame, path: list[str], values: str, title: str) -> go.Figure:
    """Create a treemap."""
    fig = px.treemap(df, path=path, values=values, title=title, template=THEME_TEMPLATE)
    fig.update_layout(margin=dict(l=10, r=10, t=55, b=10))
    return fig


def heatmap(df: pd.DataFrame, x: str, y: str, z: str, title: str) -> go.Figure:
    """Create a heatmap from long-form data."""
    pivot = df.pivot_table(index=y, columns=x, values=z, aggfunc="sum").fillna(0)
    fig = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale="Tealrose",
        title=title,
        template=THEME_TEMPLATE,
        labels={"color": z},
    )
    fig.update_layout(margin=dict(l=10, r=10, t=55, b=10))
    return fig


def scatter_bubble(
    df: pd.DataFrame,
    x: str,
    y: str,
    size: str,
    color: str,
    hover_name: str,
    title: str,
) -> go.Figure:
    """Create a bubble scatter plot."""
    fig = px.scatter(
        df,
        x=x,
        y=y,
        size=size,
        color=color,
        hover_name=hover_name,
        size_max=42,
        title=title,
        template=THEME_TEMPLATE,
    )
    fig.update_layout(margin=dict(l=10, r=10, t=55, b=10))
    return fig


def india_choropleth(df: pd.DataFrame, color: str, title: str) -> go.Figure:
    """Create an India state choropleth-like map using state centroids.

    Plotly does not ship Indian state geometry. The dashboard therefore uses a
    geo-scatter map with official state labels and metric-scaled markers.
    """
    centroids = pd.DataFrame(
        [
            ("Maharashtra", 19.75, 75.71),
            ("Tamil Nadu", 11.13, 78.66),
            ("Karnataka", 15.32, 75.71),
            ("Gujarat", 22.26, 71.19),
            ("Uttar Pradesh", 26.85, 80.95),
            ("West Bengal", 22.99, 87.85),
            ("Rajasthan", 27.02, 74.21),
            ("Telangana", 18.11, 79.02),
            ("Kerala", 10.85, 76.27),
            ("Madhya Pradesh", 22.97, 78.66),
            ("Bihar", 25.10, 85.31),
            ("Delhi", 28.61, 77.21),
            ("Punjab", 31.15, 75.34),
            ("Haryana", 29.06, 76.09),
            ("Odisha", 20.95, 85.10),
            ("Assam", 26.20, 92.94),
        ],
        columns=["state", "lat", "lon"],
    )
    map_df = df.merge(centroids, on="state", how="left").dropna(subset=["lat", "lon"])
    fig = px.scatter_geo(
        map_df,
        lat="lat",
        lon="lon",
        size=color,
        color=color,
        hover_name="state",
        hover_data={"region": True, color: ":,.2f", "lat": False, "lon": False},
        scope="asia",
        projection="natural earth",
        title=title,
        template=THEME_TEMPLATE,
        color_continuous_scale="Viridis",
    )
    fig.update_geos(center={"lat": 22.5, "lon": 80.0}, lataxis_range=[6, 36], lonaxis_range=[67, 98])
    fig.update_layout(margin=dict(l=10, r=10, t=55, b=10), height=520)
    return fig


def forecast_chart(history: pd.DataFrame, forecast: pd.DataFrame) -> go.Figure:
    """Create a historical plus forecast line chart."""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=history["date"],
            y=history["credit_crore"],
            mode="lines+markers",
            name="Historical credit",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=forecast["date"],
            y=forecast["forecast_crore"],
            mode="lines+markers",
            name="Forecast",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=pd.concat([forecast["date"], forecast["date"][::-1]]),
            y=pd.concat([forecast["upper_crore"], forecast["lower_crore"][::-1]]),
            fill="toself",
            fillcolor="rgba(43, 120, 142, 0.18)",
            line=dict(color="rgba(255,255,255,0)"),
            hoverinfo="skip",
            name="80% confidence interval",
        )
    )
    fig.update_layout(
        title="Credit Forecast",
        template=THEME_TEMPLATE,
        hovermode="x unified",
        margin=dict(l=10, r=10, t=55, b=10),
    )
    return fig

