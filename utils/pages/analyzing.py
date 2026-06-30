"""Analysis workflow page — animated progress steps while AI runs."""

from __future__ import annotations

import time

import streamlit as st

from utils.components import render_analysis_progress
from utils.data_sync import sync_registry
from utils.session import (
    get_snapshot,
    run_platform_analysis,
    set_page_state,
)
from utils.theme import COLORS
from utils.uploads import get_filenames, get_uploads

C = COLORS

_HIDE_SIDEBAR = f"""
<style>
[data-testid="stSidebar"]                {{ display: none !important; }}
[data-testid="stSidebarCollapsedControl"] {{ display: none !important; }}
.main .block-container                    {{ padding-left: 2rem !important; max-width: 800px; margin: 0 auto; }}
</style>
"""


def render_analyzing_page() -> None:
    """Show animated progress, run the full AI pipeline, then redirect to dashboard."""
    st.markdown(_HIDE_SIDEBAR, unsafe_allow_html=True)

    # Guard: if analysis is already done, go straight to dashboard
    if get_snapshot() is not None:
        set_page_state("dashboard")
        st.rerun()
        return

    if not get_uploads():
        set_page_state("landing")
        st.rerun()
        return

    # ── Page header ────────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="
            display:flex;align-items:center;justify-content:space-between;
            padding:0.75rem 0 1.5rem 0;
            border-bottom:1px solid {C['border']};
        ">
            <div style="font-size:1.05rem;font-weight:800;color:{C['text']};letter-spacing:-0.03em;">
                ⚗️ FabSense <span style="color:{C['accent']};">AI</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Centered analysis card ─────────────────────────────────────────────
    _, center, _ = st.columns([1, 2, 1])
    with center:
        st.markdown(
            f"""
            <div style="text-align:center;padding:3rem 0 1.5rem 0;">
                <div style="font-size:2.5rem;margin-bottom:1rem;">🧠</div>
                <h2 style="font-size:1.5rem;font-weight:800;color:{C['text']};letter-spacing:-0.03em;margin-bottom:0.4rem;">
                    Analyzing your semiconductor data
                </h2>
                <p style="font-size:0.9rem;color:{C['text_muted']};margin-bottom:0;">
                    Please wait while the AI pipeline processes your files
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Progress bar placeholder
        progress_bar = st.progress(0, text="Initializing…")

        # Steps visual placeholder
        steps_placeholder = st.empty()

        # ── Run pipeline step by step ──────────────────────────────────────
        filenames = get_filenames()

        def _update(completed: int, active: int, pct: int, text: str) -> None:
            progress_bar.progress(pct, text=text)
            with steps_placeholder.container():
                render_analysis_progress(completed, active)
            time.sleep(0.35)

        _update(0, 0, 5,  "📂 Reading uploaded files…")
        sync_registry()

        _update(1, 1, 15, "🔍 Loading process data…")
        time.sleep(0.2)

        _update(2, 2, 28, "📊 Detecting abnormal parameters…")
        time.sleep(0.2)

        _update(3, 3, 42, "🧠 Running AI yield analysis…")
        # ── Heavy lifting happens here ──
        run_platform_analysis(filenames)

        _update(4, 4, 62, "📉 Predicting future yield…")
        time.sleep(0.25)

        _update(5, 5, 78, "⚠️ Evaluating process risk…")
        time.sleep(0.25)

        _update(6, 6, 92, "🤖 Reviewer AI verification…")
        time.sleep(0.3)

        # Mark all complete
        progress_bar.progress(100, text="✅ Analysis complete!")
        with steps_placeholder.container():
            render_analysis_progress(8, -1)  # all done

        time.sleep(0.6)

    # ── Transition to dashboard ────────────────────────────────────────────
    set_page_state("dashboard")
    st.rerun()
