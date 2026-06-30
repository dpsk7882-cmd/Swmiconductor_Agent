"""Main dashboard — top navbar + 6-tab analysis workspace."""

from __future__ import annotations

import streamlit as st

from utils.components import render_navbar, render_metric_row, risk_pill_html, status_pill_html
from utils.session import get_snapshot, set_page_state
from utils.theme import COLORS
from utils.uploads import get_filenames, get_uploads

C = COLORS


def render_main_dashboard() -> None:
    """Render the top navbar, summary strip, and 6-tab workspace."""
    snap     = get_snapshot()
    uploads  = get_uploads()

    # ── Top navbar ─────────────────────────────────────────────────────────
    if snap:
        ts    = snap.get("analysis_timestamp", "")
        st_   = snap.get("process_status", "Normal")
        render_navbar(status=st_, timestamp=ts, files=len(uploads))
    else:
        render_navbar()

    # ── No data guard ──────────────────────────────────────────────────────
    if not snap:
        _no_data_state()
        return

    # ── KPI strip ──────────────────────────────────────────────────────────
    risk   = snap.get("risk", {})
    pred   = snap.get("prediction", {})
    expl   = snap.get("explainability", {})
    status = snap.get("process_status", "Unknown")
    conf   = expl.get("confidence_score", 0)

    status_color = {"Normal": C["success"], "Watch": C["warning"], "Alert": C["danger"]}.get(status, C["text_muted"])

    render_metric_row([
        ("🏭", "Process Status",   status,                             f"{len(snap.get('drifts',[]))} drift signal(s)", status_color),
        ("📊", "Current Yield",    f"{snap.get('current_yield','—')}%" if snap.get('current_yield') else "—", "Measured"),
        ("🔮", "Predicted Yield",  f"{snap.get('predicted_yield','—')}%" if snap.get('predicted_yield') else "—", pred.get("yield_trend","—")),
        ("⚠️", "Risk Level",       risk.get("risk_level","—"),         f"Score {risk.get('risk_score',0):.0f}/100"),
        ("🎯", "Confidence",       f"{conf:.0f}%",                     "Reviewer-verified"),
        ("⚙️", "Equipment",        snap.get("equipment_status","—"),   "From logs + drifts"),
    ])

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Six tabs ───────────────────────────────────────────────────────────
    from utils.pages.tab_data         import render_tab_data
    from utils.pages.tab_yield_loss   import render_tab_yield_loss
    from utils.pages.tab_prediction   import render_tab_prediction
    from utils.pages.tab_maintenance  import render_tab_maintenance
    from utils.pages.tab_visualization import render_tab_visualization
    from utils.pages.tab_ai_report    import render_tab_ai_report

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Data Analysis",
        "📉 Yield Loss Analysis",
        "🔮 Yield Prediction",
        "🛠 Preventive Maintenance",
        "📈 Visualization",
        "🤖 AI Report",
    ])

    with tab1: render_tab_data(snap)
    with tab2: render_tab_yield_loss(snap)
    with tab3: render_tab_prediction(snap)
    with tab4: render_tab_maintenance(snap)
    with tab5: render_tab_visualization(snap)
    with tab6: render_tab_ai_report(snap)


# ── No-data state ─────────────────────────────────────────────────────────────

def _no_data_state() -> None:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown(
            f"""
            <div style="text-align:center;padding:5rem 2rem;">
                <div style="font-size:3rem;margin-bottom:1rem;">🏭</div>
                <h2 style="font-size:1.5rem;font-weight:800;color:{C['text']};letter-spacing:-0.03em;margin-bottom:0.5rem;">
                    No Analysis Loaded
                </h2>
                <p style="font-size:0.9rem;color:{C['text_muted']};margin-bottom:2rem;">
                    Upload semiconductor process data to begin.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("📂 Upload Files & Analyze", type="primary", use_container_width=True):
            set_page_state("landing")
            st.rerun()
