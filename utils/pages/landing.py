"""Landing page — drag-and-drop upload hub, Notion-style."""

from __future__ import annotations

import streamlit as st

from tools.file_router import FileRouter
from utils.session import set_page_state
from utils.theme import COLORS
from utils.uploads import get_uploads, register_upload

C = COLORS

# Hide sidebar on landing
_HIDE_SIDEBAR = f"""
<style>
[data-testid="stSidebar"]               {{ display: none !important; }}
[data-testid="stSidebarCollapsedControl"]{{ display: none !important; }}
.main .block-container                   {{ padding-left: 2rem !important; padding-right: 2rem !important; max-width: 900px; margin: 0 auto; }}
</style>
"""


def render_landing_page() -> None:
    """Full-page landing with hero text + drag-drop upload."""
    st.markdown(_HIDE_SIDEBAR, unsafe_allow_html=True)

    # ── Slim top bar ──────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="
            display:flex;align-items:center;justify-content:space-between;
            padding:0.75rem 0 1.5rem 0;
            border-bottom:1px solid {C['border']};
            margin-bottom:0;
        ">
            <div style="font-size:1.05rem;font-weight:800;color:{C['text']};letter-spacing:-0.03em;">
                ⚗️ FabSense <span style="color:{C['accent']};">AI</span>
            </div>
            <div style="font-size:0.78rem;color:{C['text_muted']};font-weight:500;">
                Semiconductor Process Intelligence Platform
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Hero section ──────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="
            padding: 4.5rem 0 2.5rem 0;
            text-align: center;
            animation: fadeInUp 0.5s ease both;
        ">
            <div style="
                display:inline-block;
                background:{C['accent_light']};
                color:{C['accent']};
                font-size:0.78rem;
                font-weight:700;
                padding:0.3rem 1rem;
                border-radius:999px;
                border:1px solid rgba(37,99,235,0.2);
                margin-bottom:1.5rem;
                letter-spacing:0.05em;
                text-transform:uppercase;
            ">
                Powered by AI · Built for Semiconductor Engineers
            </div>
            <h1 style="
                font-size:clamp(2rem,5vw,3rem);
                font-weight:800;
                color:{C['text']};
                line-height:1.15;
                letter-spacing:-0.04em;
                margin:0 auto 1.25rem auto;
                max-width:680px;
            ">
                Semiconductor AI<br><span style="color:{C['accent']};">Analysis Platform</span>
            </h1>
            <p style="
                font-size:1.1rem;
                color:{C['text_muted']};
                line-height:1.7;
                max-width:560px;
                margin:0 auto;
                font-weight:400;
            ">
                Upload semiconductor process data and receive AI-powered yield analysis,
                prediction, and preventive maintenance recommendations.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Upload zone ───────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="
            max-width:620px;
            margin:0 auto 1.5rem auto;
            background:{C['surface']};
            border:2px dashed {C['border']};
            border-radius:20px;
            padding:2.5rem 2rem;
            text-align:center;
            transition:border-color 0.2s;
        ">
            <div style="font-size:2.5rem;margin-bottom:0.75rem;">📂</div>
            <div style="font-size:1.05rem;font-weight:700;color:{C['text']};margin-bottom:0.3rem;">
                Drag &amp; Drop your files here
            </div>
            <div style="font-size:0.82rem;color:{C['text_muted']};margin-bottom:1.25rem;">
                or use the selector below
            </div>
            <div style="
                display:flex;justify-content:center;gap:0.75rem;
                font-size:0.75rem;color:{C['text_light']};font-weight:500;
                margin-bottom:0.5rem;
            ">
                <span>📊 Excel (.xlsx)</span>
                <span>·</span>
                <span>📋 CSV</span>
                <span>·</span>
                <span>📝 TXT Logs</span>
                <span>·</span>
                <span>📄 PDF</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Center the file uploader
    _, upload_col, _ = st.columns([1, 2, 1])
    with upload_col:
        uploaded_files = st.file_uploader(
            "Choose files",
            type=FileRouter.accepted_extensions(),
            accept_multiple_files=True,
            key="landing_uploader",
            label_visibility="collapsed",
        )

        if uploaded_files:
            new_files = False
            existing_names = {u["filename"] for u in get_uploads()}
            for f in uploaded_files:
                if f.name not in existing_names:
                    register_upload(f)
                    new_files = True

            if get_uploads():
                st.success(f"✅ {len(get_uploads())} file(s) ready for analysis")
                if st.button("🚀 Start AI Analysis", type="primary", use_container_width=True):
                    set_page_state("analyzing")
                    st.rerun()

    # ── Trust indicators ──────────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="
            display:flex;justify-content:center;gap:3rem;
            margin:2rem auto 3rem auto;
            flex-wrap:wrap;
        ">
            <div style="display:flex;align-items:center;gap:0.4rem;font-size:0.82rem;color:{C['text_muted']};font-weight:500;">
                <span style="color:{C['success']};font-size:1rem;">✔</span> Secure Analysis
            </div>
            <div style="display:flex;align-items:center;gap:0.4rem;font-size:0.82rem;color:{C['text_muted']};font-weight:500;">
                <span style="color:{C['success']};font-size:1rem;">✔</span> AI Powered
            </div>
            <div style="display:flex;align-items:center;gap:0.4rem;font-size:0.82rem;color:{C['text_muted']};font-weight:500;">
                <span style="color:{C['success']};font-size:1rem;">✔</span> Semiconductor Specialized
            </div>
            <div style="display:flex;align-items:center;gap:0.4rem;font-size:0.82rem;color:{C['text_muted']};font-weight:500;">
                <span style="color:{C['success']};font-size:1rem;">✔</span> Dual-Agent Verified
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Feature row ───────────────────────────────────────────────────────
    cols = st.columns(4)
    features = [
        ("🔍", "Drift Detection", "Pressure, temperature, RF power, gas flow"),
        ("📈", "Yield Prediction", "ML-based yield & failure forecasting"),
        ("🔬", "Root Cause Analysis", "Ranked hypotheses with evidence"),
        ("🛠", "PM Recommendations", "Prioritized preventive actions"),
    ]
    for col, (icon, title, desc) in zip(cols, features):
        with col:
            st.markdown(
                f"""
                <div style="
                    background:{C['surface']};
                    border:1px solid {C['border']};
                    border-radius:12px;
                    padding:1.25rem;
                    text-align:center;
                    height:100%;
                ">
                    <div style="font-size:1.75rem;margin-bottom:0.5rem;">{icon}</div>
                    <div style="font-size:0.88rem;font-weight:700;color:{C['text']};margin-bottom:0.3rem;">{title}</div>
                    <div style="font-size:0.75rem;color:{C['text_muted']};line-height:1.5;">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
