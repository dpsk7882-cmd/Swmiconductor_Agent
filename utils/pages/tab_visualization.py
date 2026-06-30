"""Tab 5 — Visualization: charts switchboard for process parameters."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.components import empty_state, page_header, section_title
from utils.session import get_engine
from utils.theme import COLORS

C = COLORS

CHART_THEME = dict(
    template="plotly_white",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#FAFBFC",
    font=dict(family="Inter, sans-serif", size=12, color=C["text"]),
    margin=dict(l=10, r=10, t=40, b=10),
)


def _apply(fig: go.Figure, height: int = 340) -> go.Figure:
    fig.update_layout(**CHART_THEME, height=height)
    fig.update_xaxes(gridcolor=C["border"], zeroline=False)
    fig.update_yaxes(gridcolor=C["border"], zeroline=False)
    return fig


def render_tab_visualization(snap: dict[str, Any]) -> None:
    page_header("📈 Visualization", "Interactive charts for yield trends, correlations, distributions, and time series")

    engine = get_engine()
    if not engine.registry.combined_frames:
        empty_state("📈", "No Data Loaded", "Upload process data to view interactive visualizations.")
        return

    df, source = engine.registry.combined_frames[0]
    numeric    = df.select_dtypes(include="number").columns.tolist()
    date_cols  = df.select_dtypes(include=["datetime","datetimetz"]).columns.tolist()

    if not numeric:
        st.warning("No numeric columns found for visualization.")
        return

    # ── Chart selector ─────────────────────────────────────────────────────
    chart_type = st.selectbox(
        "Select chart type",
        ["📈 Yield Trend", "🌡 Correlation Heatmap", "📊 Parameter Distribution",
         "🔵 Scatter Plot", "⏱ Time Series", "📦 Box Plot"],
        label_visibility="visible",
    )
    st.markdown("")

    # ── Yield Trend ────────────────────────────────────────────────────────
    if "Yield Trend" in chart_type:
        yield_col = _find_yield(df)
        if yield_col:
            c1, c2 = st.columns([4, 1])
            with c2:
                window = st.slider("Smoothing", 1, 15, 5)
            with c1:
                y = df[yield_col].dropna()
                fig = go.Figure()
                fig.add_trace(go.Scatter(y=y, mode="lines+markers", name="Yield",
                    line=dict(color=C["border"], width=1), marker=dict(size=4, color=C["accent"])))
                if window > 1:
                    rolled = y.rolling(window, center=True).mean()
                    fig.add_trace(go.Scatter(y=rolled, mode="lines", name=f"{window}-pt MA",
                        line=dict(color=C["accent"], width=2.5)))
                fig.update_layout(title=f"{yield_col} — Yield Trend")
                _apply(fig)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Add a yield column (e.g. `yield_pct`) for yield trend charting.")

    # ── Correlation Heatmap ────────────────────────────────────────────────
    elif "Correlation" in chart_type:
        cols_sel = st.multiselect("Select parameters (max 12)", numeric, default=numeric[:8])
        if len(cols_sel) >= 2:
            corr = df[cols_sel].corr()
            fig  = go.Figure(go.Heatmap(
                z=corr.values, x=corr.columns, y=corr.columns,
                colorscale="RdBu", zmin=-1, zmax=1,
                colorbar=dict(title="r"),
            ))
            fig.update_layout(title="Parameter Correlation Matrix")
            _apply(fig, height=420)
            st.plotly_chart(fig, use_container_width=True)

    # ── Distribution ───────────────────────────────────────────────────────
    elif "Distribution" in chart_type:
        col_sel = st.selectbox("Parameter", numeric)
        fig = px.histogram(df, x=col_sel, nbins=30, title=f"Distribution — {col_sel}",
                           color_discrete_sequence=[C["accent"]])
        fig.add_vline(x=df[col_sel].mean(), line_dash="dash", line_color=C["warning"],
                      annotation_text=f"Mean: {df[col_sel].mean():.2f}")
        _apply(fig)
        st.plotly_chart(fig, use_container_width=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Mean",   f"{df[col_sel].mean():.3f}")
        c2.metric("Std Dev",f"{df[col_sel].std():.3f}")
        c3.metric("Skew",   f"{df[col_sel].skew():.3f}")

    # ── Scatter Plot ───────────────────────────────────────────────────────
    elif "Scatter" in chart_type:
        c1, c2, c3 = st.columns(3)
        x_col = c1.selectbox("X axis", numeric, index=0)
        y_col = c2.selectbox("Y axis", numeric, index=min(1, len(numeric)-1))
        color_col = c3.selectbox("Color by (optional)", ["—"] + numeric)

        kw = dict(title=f"{x_col} vs {y_col}", color_discrete_sequence=[C["accent"]])
        if color_col != "—":
            fig = px.scatter(df, x=x_col, y=y_col, color=color_col,
                             color_continuous_scale="Blues", **{k:v for k,v in kw.items() if k!="color_discrete_sequence"})
        else:
            fig = px.scatter(df, x=x_col, y=y_col, **kw, opacity=0.7)

        # Trendline
        mask = df[[x_col, y_col]].dropna()
        if len(mask) > 3:
            m, b = np.polyfit(mask[x_col], mask[y_col], 1)
            x_range = np.linspace(mask[x_col].min(), mask[x_col].max(), 100)
            fig.add_trace(go.Scatter(x=x_range, y=m*x_range+b, mode="lines",
                name="Trend", line=dict(color=C["danger"], width=2, dash="dash")))
        _apply(fig)
        st.plotly_chart(fig, use_container_width=True)

    # ── Time Series ────────────────────────────────────────────────────────
    elif "Time Series" in chart_type:
        if date_cols:
            date_col = st.selectbox("Time column", date_cols)
            param_cols = st.multiselect("Parameters", numeric, default=numeric[:2])
            if param_cols:
                sorted_df = df.sort_values(date_col).dropna(subset=[date_col])
                fig = go.Figure()
                palette = [C["accent"], C["danger"], C["success"], C["warning"], C["info"]]
                for i, col in enumerate(param_cols):
                    color = palette[i % len(palette)]
                    fig.add_trace(go.Scatter(
                        x=sorted_df[date_col], y=sorted_df[col],
                        mode="lines", name=col,
                        line=dict(color=color, width=2),
                    ))
                fig.update_layout(title="Time Series — Process Parameters", hovermode="x unified")
                _apply(fig, height=360)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No datetime column detected. Dates must be parseable (e.g. YYYY-MM-DD).")

    # ── Box Plot ───────────────────────────────────────────────────────────
    elif "Box" in chart_type:
        cols_sel = st.multiselect("Select parameters", numeric, default=numeric[:4])
        if cols_sel:
            melted = df[cols_sel].melt(var_name="Parameter", value_name="Value")
            fig = px.box(melted, x="Parameter", y="Value", color="Parameter",
                         color_discrete_sequence=px.colors.qualitative.Set2,
                         title="Parameter Distribution — Box Plot")
            _apply(fig)
            st.plotly_chart(fig, use_container_width=True)


def _find_yield(df: pd.DataFrame) -> str | None:
    aliases = {"yield", "yield_pct", "yield_percent", "bin_yield"}
    for col in df.columns:
        if col.lower().replace(" ", "_").replace("-", "_") in aliases or "yield" in col.lower():
            return col
    return None
