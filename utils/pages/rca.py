"""🔍 Root Cause Analysis page."""

from __future__ import annotations

import plotly.express as px
import streamlit as st

from utils.components import empty_state, platform_header
from utils.executive_report import extract_top_root_causes, render_executive_report
from utils.navigation import PAGE_TITLES
from utils.session import get_snapshot


def render_rca_page() -> None:
    title, subtitle = PAGE_TITLES["rca"]
    platform_header(title, subtitle)

    snap = get_snapshot()
    if not snap:
        empty_state("🔍", "No RCA Results", "Run platform analysis after uploading process data.")
        return

    render_executive_report(snap)

    top = extract_top_root_causes(snap, limit=5)
    if len(top) >= 2:
        st.markdown("#### 📊 Contribution Chart")
        fig = px.bar(
            x=[p for _, p in top],
            y=[n for n, _ in top],
            orientation="h",
            labels={"x": "Importance %", "y": "Root Cause"},
            color=[p for _, p in top],
            color_continuous_scale="Blues",
        )
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### 📝 Detailed Explanations")
    for rc in snap.get("root_causes", []):
        with st.expander(f"#{rc.get('rank', '')} {rc.get('factor', '')}"):
            st.markdown(rc.get("explanation", ""))
            for ev in rc.get("evidence", []):
                st.markdown(f"- {ev}")
