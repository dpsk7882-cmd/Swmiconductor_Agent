"""📈 Yield Prediction page."""

from __future__ import annotations

import streamlit as st

from utils.charts import build_process_charts
from utils.components import empty_state, platform_header
from utils.data_sync import sync_registry
from utils.executive_report import render_executive_report
from utils.navigation import PAGE_TITLES
from utils.session import get_engine, get_snapshot


def render_yield_prediction_page() -> None:
    title, subtitle = PAGE_TITLES["yield_prediction"]
    platform_header(title, subtitle)

    sync_registry()
    snap = get_snapshot()

    if not snap:
        empty_state("📈", "No Predictions Available", "Upload process data and run analysis from the Dashboard.")
        return

    render_executive_report(snap)

    pred = snap.get("prediction", {})
    st.markdown("#### 🤖 Model Details")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"- **Model:** {pred.get('model_name', '—')}")
        st.markdown(f"- **Version:** {pred.get('model_version', '—')}")
        st.markdown(f"- **Failure Probability:** {pred.get('failure_probability', 0):.0%}")
    with col2:
        st.markdown("**Key Variables**")
        for var in pred.get("top_variables", []):
            st.markdown(f"- {var}")

    engine = get_engine()
    if engine.registry.combined_frames:
        df, _ = engine.registry.combined_frames[0]
        from models.prediction_model import get_prediction_model
        forecast_df = get_prediction_model().forecast_series(df)
        if forecast_df is not None:
            charts = build_process_charts(df, forecast_df=forecast_df)
            forecast_charts = [c for c in charts if c.get("type") == "forecast"]
            if forecast_charts:
                st.plotly_chart(forecast_charts[0]["figure"], use_container_width=True)
