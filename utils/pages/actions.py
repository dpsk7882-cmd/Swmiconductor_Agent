"""🛠 Recommended Actions page."""

from __future__ import annotations

import streamlit as st

from utils.components import empty_state, platform_header
from utils.executive_report import extract_recommended_actions, render_executive_report
from utils.navigation import PAGE_TITLES
from utils.session import get_snapshot

PRIORITY_ICON = {"high": "🔴", "medium": "🟡", "low": "🟢"}


def render_actions_page() -> None:
    title, subtitle = PAGE_TITLES["actions"]
    platform_header(title, subtitle)

    snap = get_snapshot()
    if not snap:
        empty_state("🛠", "No Recommendations", "Run platform analysis to generate prioritized actions.")
        return

    render_executive_report(snap)

    st.markdown("#### 📋 Action Details")
    recs = snap.get("recommendations", [])
    if not recs:
        for i, action in enumerate(extract_recommended_actions(snap), 1):
            st.markdown(f"**{i}. {action}** — pending detailed rationale after next analysis run.")
        return

    for rec in recs:
        pri = rec.get("priority", "medium")
        icon = PRIORITY_ICON.get(pri, "🟡")
        with st.container(border=True):
            st.markdown(f"**{icon} {rec.get('action', '')}**")
            st.caption(f"🔧 {rec.get('equipment', '')}")
            st.markdown(f"_{rec.get('rationale', '')}_")
            st.metric("Estimated Risk Reduction", f"{rec.get('risk_reduction', 0):.0%}")
