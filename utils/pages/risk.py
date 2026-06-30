"""⚠ Process Risk Assessment page."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from utils.components import empty_state, platform_header, render_metric_row, risk_pill
from utils.navigation import PAGE_TITLES
from utils.session import get_snapshot


def render_risk_page() -> None:
    title, subtitle = PAGE_TITLES["risk"]
    platform_header(title, subtitle)

    snap = get_snapshot()
    if not snap:
        empty_state("⚠", "No Risk Assessment", "Run analysis from the Dashboard after uploading data.")
        return

    risk = snap.get("risk", {})

    render_metric_row([
        ("⚖", "Process Stability", risk.get("process_stability", "—"), risk_pill(risk.get("process_stability", "Low"))),
        ("📉", "Yield Risk", risk.get("yield_risk", "—"), risk_pill(risk.get("yield_risk", "Low"))),
        ("⚙", "Equipment Risk", risk.get("equipment_risk", "—"), risk_pill(risk.get("equipment_risk", "Low"))),
        ("🎯", "Risk Score", f"{risk.get('risk_score', 0)}/100", risk_pill(risk.get("risk_level", "Low"))),
    ])

    st.divider()
    st.markdown(f"#### Summary")
    st.markdown(risk.get("summary", ""))

    for factor in risk.get("factors", []):
        st.markdown(f"- ⚠ {factor}")

    # Radar chart
    levels = {"Low": 1, "Medium": 2, "High": 3}
    categories = ["Process Stability", "Yield Risk", "Equipment Risk", "Overall"]
    values = [
        levels.get(risk.get("process_stability", "Low"), 1),
        levels.get(risk.get("yield_risk", "Low"), 1),
        levels.get(risk.get("equipment_risk", "Low"), 1),
        levels.get(risk.get("risk_level", "Low"), 1),
    ]
    fig = go.Figure(data=go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]], fill="toself"))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 3])),
        template="plotly_dark",
        title="Risk Profile",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)

    expl = snap.get("explainability", {})
    with st.expander("🔬 Evidence Supporting Risk Assessment"):
        for e in expl.get("evidence", []):
            st.markdown(f"- {e}")
