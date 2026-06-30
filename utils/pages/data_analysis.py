"""📊 Data Analysis page — drift detection results."""

from __future__ import annotations

import streamlit as st

from utils.charts import build_process_charts
from utils.components import empty_state, platform_header, risk_pill
from utils.data_sync import sync_registry
from utils.navigation import PAGE_TITLES
from utils.session import get_engine, get_snapshot, run_platform_analysis
from utils.uploads import get_filenames, get_uploads


def render_data_analysis_page() -> None:
    title, subtitle = PAGE_TITLES["data_analysis"]
    platform_header(title, subtitle)

    sync_registry()
    snap = get_snapshot()
    uploads = get_uploads()

    if not uploads:
        empty_state("📊", "No Data Loaded", "Upload Excel (.xlsx) or CSV process data.")
        return

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("▶ Analyze", type="primary", use_container_width=True):
            run_platform_analysis(get_filenames())
            st.rerun()

    engine = get_engine()
    if engine.registry.combined_frames:
        df, source = engine.registry.combined_frames[0]
        st.caption(f"Primary dataset: **{source}** · {len(df)} rows · {len(df.columns)} columns")

        drifts = snap.get("drifts", []) if snap else []
        charts = build_process_charts(df, sheet_name=source, anomalies=drifts)
        if charts:
            for i in range(0, min(len(charts), 4), 2):
                cols = st.columns(2)
                for j, col in enumerate(cols):
                    idx = i + j
                    if idx < len(charts):
                        with col:
                            st.plotly_chart(charts[idx]["figure"], use_container_width=True)

    st.divider()
    st.markdown("#### ⚠ Detected Drift & Abnormalities")

    if not snap or not snap.get("drifts"):
        st.info("Run analysis to detect pressure, temperature, RF, gas flow, particle, and ARC drifts.")
        return

    for d in snap["drifts"]:
        sev = d.get("severity", "medium")
        pill = risk_pill("High" if sev in ("high", "critical") else "Medium" if sev == "medium" else "Low")
        with st.expander(f"{d.get('category', 'Drift')} — {d.get('parameter', '')} {pill}", expanded=sev in ("high", "critical")):
            st.markdown(d.get("message", ""))
            st.caption(f"Evidence: {d.get('evidence', '')}")
            if d.get("drift_pct") is not None:
                st.metric("Drift Magnitude", f"{d['drift_pct']:+.1f}%")
