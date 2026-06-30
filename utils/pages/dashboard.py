"""🏠 Operations Dashboard — primary landing page."""

from __future__ import annotations

import streamlit as st

from utils.components import empty_state, platform_header, render_metric_row
from utils.data_sync import sync_registry
from utils.executive_report import render_executive_report
from utils.navigation import PAGE_TITLES
from utils.session import get_snapshot, run_platform_analysis
from utils.uploads import get_filenames, get_uploads


def render_dashboard_page() -> None:
    title, subtitle = PAGE_TITLES["dashboard"]
    platform_header(title, subtitle)

    sync_registry()
    snap = get_snapshot()
    uploads = get_uploads()

    if uploads and not snap:
        if st.button("🔄 Run Full Platform Analysis", type="primary", use_container_width=True):
            run_platform_analysis(get_filenames())
            st.rerun()

    if not snap:
        empty_state(
            "🏭",
            "Awaiting Process Data",
            "Upload Excel, CSV, or equipment logs in the sidebar, then run analysis.",
        )
        if uploads:
            st.info(f"📁 {len(uploads)} file(s) ready — click **Run Full Platform Analysis** above.")
        return

    # Compact status strip
    risk = snap.get("risk", {})
    pred = snap.get("prediction", {})
    expl = snap.get("explainability", {})
    status = snap.get("process_status", "Unknown")

    render_metric_row([
        ("🟢", "Process Status", status, snap.get("equipment_status", "—")),
        ("📊", "Current Yield", f"{snap.get('current_yield', '—')}%", "Measured"),
        ("📈", "Predicted Yield", f"{snap.get('predicted_yield', '—')}%", pred.get("yield_trend", "—")),
        ("⚠", "Risk Score", f"{risk.get('risk_score', 0):.0f}", risk.get("risk_level", "—")),
    ])

    # Primary deliverable — executive AI report
    st.markdown("#### 📋 AI Decision Report")
    render_executive_report(snap)

    # Expandable technical detail
    with st.expander("🔬 Detailed Analysis & Evidence", expanded=False):
        verdict = snap.get("agent_verdict") or {}
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Reviewer Analysis**")
            st.markdown(verdict.get("reviewed_analysis", ""))
            st.caption(verdict.get("reviewer_notes", ""))
        with col_b:
            st.markdown("**Evidence**")
            for ev in expl.get("evidence", []):
                st.markdown(f"- {ev}")
            if verdict.get("needs_more_data"):
                st.warning("Additional data requested: " + "; ".join(verdict.get("data_requests", [])))

        with st.expander("Original Analysis (Agent 1)"):
            st.text(verdict.get("original_analysis", ""))

    history = st.session_state.get("analysis_history", [])
    if len(history) > 1:
        with st.expander("🕐 Analysis History"):
            for h in history[1:6]:
                st.caption(
                    f"{h.get('timestamp')} — {h.get('status')} | "
                    f"Risk {h.get('risk')} | {h.get('confidence', 0):.0f}%"
                )

    if st.button("🔄 Re-run Analysis", use_container_width=True):
        run_platform_analysis(get_filenames())
        st.rerun()
