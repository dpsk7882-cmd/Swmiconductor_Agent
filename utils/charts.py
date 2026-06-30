"""Plotly chart builders for process data dashboards."""

from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def build_process_charts(
    dataframe: pd.DataFrame,
    sheet_name: str = "Process Data",
    forecast_df: pd.DataFrame | None = None,
    anomalies: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Generate dashboard charts from process data."""
    charts: list[dict[str, Any]] = []
    numeric = dataframe.select_dtypes(include="number").columns.tolist()
    datetime_cols = dataframe.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()

    if not numeric:
        return charts

    # Process parameter trend lines
    x_col = datetime_cols[0] if datetime_cols else None
    for col in numeric[:3]:
        if x_col:
            sorted_df = dataframe.sort_values(x_col).dropna(subset=[x_col, col])
            fig = px.line(sorted_df, x=x_col, y=col, title=f"{col} Trend", color_discrete_sequence=["#2563eb"])
        else:
            fig = px.line(y=dataframe[col].dropna(), title=f"{col} Trend", color_discrete_sequence=["#2563eb"])
            fig.update_xaxes(title="Sample Index")
        _theme(fig)
        charts.append({"title": f"Trend — {col}", "figure": fig, "type": "trend"})

    # Yield forecast chart
    if forecast_df is not None and not forecast_df.empty:
        fig = px.line(
            forecast_df, x="step", y="yield", color="series",
            title="Yield Forecast", color_discrete_map={"historical": "#2563eb", "forecast": "#dc2626"},
        )
        _theme(fig)
        charts.append({"title": "Yield Forecast", "figure": fig, "type": "forecast"})

    # Anomaly severity bar
    if anomalies:
        params = [a.get("parameter", a.get("column", "?"))[:20] for a in anomalies[:8]]
        severities = [a.get("severity", "medium") for a in anomalies[:8]]
        color_map = {"high": "#dc2626", "medium": "#f59e0b", "low": "#22c55e"}
        colors = [color_map.get(s, "#64748b") for s in severities]
        fig = go.Figure(go.Bar(x=params, y=[1] * len(params), marker_color=colors, text=severities, textposition="auto"))
        fig.update_layout(title="Detected Anomalies by Parameter", yaxis_visible=False)
        _theme(fig)
        charts.append({"title": "Anomaly Overview", "figure": fig, "type": "anomaly"})

    # Correlation heatmap
    if len(numeric) >= 2:
        corr = dataframe[numeric].corr()
        fig = go.Figure(data=go.Heatmap(z=corr.values, x=corr.columns, y=corr.columns, colorscale="RdBu", zmin=-1, zmax=1))
        fig.update_layout(title=f"Parameter Correlation — {sheet_name}")
        _theme(fig)
        charts.append({"title": "Correlation Matrix", "figure": fig, "type": "correlation"})

    # Distribution histograms
    for col in numeric[:2]:
        fig = px.histogram(dataframe, x=col, nbins=25, title=f"Distribution: {col}", color_discrete_sequence=["#7c3aed"])
        _theme(fig)
        charts.append({"title": f"Histogram — {col}", "figure": fig, "type": "histogram"})

    return charts


def build_health_gauge(health: str, confidence: float) -> go.Figure:
    """Gauge chart for process health and confidence."""
    normalized = health.lower()
    alias = {"normal": "healthy", "watch": "warning", "alert": "critical"}
    normalized = alias.get(normalized, normalized)

    health_value = {"healthy": 85, "warning": 50, "critical": 20, "unknown": 40}.get(normalized, 40)
    color = {"healthy": "#22c55e", "warning": "#f59e0b", "critical": "#dc2626", "unknown": "#94a3b8"}.get(normalized, "#94a3b8")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=health_value,
        number={"suffix": f" | {confidence:.0f}% conf."},
        title={"text": f"Process Status: {health.upper()}"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": color},
            "steps": [
                {"range": [0, 35], "color": "#fee2e2"},
                {"range": [35, 65], "color": "#fef3c7"},
                {"range": [65, 100], "color": "#dcfce7"},
            ],
        },
    ))
    _theme(fig)
    return fig


def _theme(fig: go.Figure) -> None:
    fig.update_layout(
        template="plotly_white",
        font=dict(family="Inter, Segoe UI, sans-serif", size=13),
        margin=dict(l=40, r=40, t=60, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
