"""Clean white sidebar for the industrial platform."""

from __future__ import annotations

import streamlit as st

from utils.session import (
    get_page_state,
    get_snapshot,
    reset_to_landing,
    set_page_state,
)
from utils.theme import COLORS
from utils.uploads import clear_uploads, get_uploads

C = COLORS


def render_sidebar() -> None:
    """Render the full sidebar: branding, navigation, status, file list."""
    _render_branding()
    _render_nav()
    st.markdown(f'<hr style="border-top:1px solid {C["border"]};margin:0.75rem 0;">', unsafe_allow_html=True)
    _render_status()
    _render_file_list()
    _render_footer()


# ── Branding ──────────────────────────────────────────────────────────────────

def _render_branding() -> None:
    st.markdown(
        f"""
        <div class="nav-brand">
            ⚗️&nbsp;<span>FabSense&nbsp;<span class="nb-accent">AI</span></span>
        </div>
        <div class="nav-tagline">Semiconductor Process Intelligence</div>
        """,
        unsafe_allow_html=True,
    )


# ── Navigation ────────────────────────────────────────────────────────────────

_NAV_ITEMS = [
    ("dashboard",  "🏠", "Dashboard"),
    ("analyzing",  "🔄", "New Analysis"),
    ("settings",   "⚙️", "Settings"),
]


def _render_nav() -> None:
    page = get_page_state()
    st.markdown(f'<div class="nav-section-label">Menu</div>', unsafe_allow_html=True)

    # Dashboard
    active = "active" if page == "dashboard" else ""
    if st.button("🏠  Dashboard",     key="nav_dash",     use_container_width=True):
        if get_snapshot():
            set_page_state("dashboard")
            st.rerun()

    # New Analysis
    if st.button("📂  New Analysis",  key="nav_new",      use_container_width=True):
        reset_to_landing()
        st.rerun()

    # Settings
    if st.button("⚙️  Settings",     key="nav_settings", use_container_width=True):
        set_page_state("settings")
        st.rerun()


# ── Current analysis status ───────────────────────────────────────────────────

def _render_status() -> None:
    snap = get_snapshot()
    if not snap:
        st.caption("No analysis loaded.")
        return

    status    = snap.get("process_status", "Unknown")
    risk      = (snap.get("risk") or {}).get("risk_level", "—")
    conf      = (snap.get("explainability") or {}).get("confidence_score", 0)
    pred      = snap.get("predicted_yield")
    ts        = snap.get("analysis_timestamp", "")

    color_map = {"Normal": C["success"], "Watch": C["warning"], "Alert": C["danger"]}
    status_color = color_map.get(status, C["text_muted"])

    st.markdown(
        f"""
        <div style="background:{C['surface']};border:1px solid {C['border']};border-radius:10px;padding:0.85rem 1rem;margin:0.5rem 0;">
            <div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;color:{C['text_muted']};margin-bottom:0.6rem;">Current Analysis</div>
            <div style="display:flex;justify-content:space-between;margin-bottom:0.3rem;">
                <span style="font-size:0.82rem;color:{C['text_muted']};">Status</span>
                <span style="font-size:0.82rem;font-weight:700;color:{status_color};">{status}</span>
            </div>
            <div style="display:flex;justify-content:space-between;margin-bottom:0.3rem;">
                <span style="font-size:0.82rem;color:{C['text_muted']};">Risk</span>
                <span style="font-size:0.82rem;font-weight:700;color:{C['text']};">{risk}</span>
            </div>
            <div style="display:flex;justify-content:space-between;margin-bottom:0.3rem;">
                <span style="font-size:0.82rem;color:{C['text_muted']};">Confidence</span>
                <span style="font-size:0.82rem;font-weight:700;color:{C['accent']};">{conf:.0f}%</span>
            </div>
            {f'<div style="display:flex;justify-content:space-between;"><span style="font-size:0.82rem;color:{C["text_muted"]};">Pred. Yield</span><span style="font-size:0.82rem;font-weight:700;color:{C["text"]};">{pred:.1f}%</span></div>' if pred else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )
    if ts:
        st.caption(f"🕐 {ts}")


# ── Loaded files ──────────────────────────────────────────────────────────────

def _render_file_list() -> None:
    uploads = get_uploads()
    if not uploads:
        return

    st.markdown(
        f'<div class="nav-section-label">Loaded Files ({len(uploads)})</div>',
        unsafe_allow_html=True,
    )
    for u in uploads:
        icon = u.get("icon", "📄")
        name = u.get("filename", "")
        size = u.get("size_bytes", 0)
        size_label = f"{size/1024:.1f} KB" if size < 1024 * 1024 else f"{size/1024/1024:.1f} MB"
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;gap:0.5rem;padding:0.45rem 0.5rem;border-radius:6px;background:{C['surface']};margin-bottom:0.3rem;">
                <span style="font-size:1rem;">{icon}</span>
                <div style="overflow:hidden;">
                    <div style="font-size:0.78rem;font-weight:600;color:{C['text']};white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{name}</div>
                    <div style="font-size:0.68rem;color:{C['text_muted']};">{size_label}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ── Footer ────────────────────────────────────────────────────────────────────

def _render_footer() -> None:
    st.markdown(f'<hr style="border-top:1px solid {C["border"]};margin:0.75rem 0;">', unsafe_allow_html=True)
    st.caption("FabSense AI v2.0 · Semiconductor Process Intelligence")


# ── Settings page renderer ────────────────────────────────────────────────────

def render_settings_sidebar_page() -> None:
    """Full settings page (called from app.py when settings nav item clicked)."""
    from utils.session import clear_messages
    from utils.config import OPENAI_API_KEY, OPENAI_MODEL

    st.markdown("#### ⚙️ Platform Settings")

    with st.expander("🤖 LLM Configuration", expanded=True):
        llm_ok = bool(OPENAI_API_KEY and OPENAI_API_KEY not in ("sk-your-key-here", ""))
        st.markdown(f"**Status:** {'✅ Active' if llm_ok else '⚪ Disabled (template mode)'}")
        st.text_input("Model", value=OPENAI_MODEL, disabled=True)
        st.caption("Set `OPENAI_API_KEY` in `.env` for enhanced AI narratives.")

    with st.expander("🏗 Agent Pipeline"):
        st.markdown("""
| Agent | Role |
|-------|------|
| **Analysis Agent** | Analyzes data, detects drifts, generates conclusions |
| **Reviewer Agent** | Verifies evidence, assigns confidence, flags contradictions |
| **Platform Engine** | Orchestrates full pipeline |
""")

    with st.expander("🧬 ML Models (Swappable)"):
        st.markdown("""
| Model | Purpose |
|-------|---------|
| `EnsembleYieldModel` | Yield & failure prediction |
| `RiskScoringModel` | Process/yield/equipment risk |
| `RootCauseModel` | RCA ranking |
""")
        st.caption("Replace models via `models/prediction_model.py` PREDICTION_MODELS registry.")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑 Clear Chat", use_container_width=True):
            clear_messages(); st.success("Cleared.")
    with col2:
        if st.button("🔄 New Analysis", use_container_width=True):
            reset_to_landing(); st.rerun()
