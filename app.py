"""
FabSense AI — Semiconductor Process Intelligence Platform

Run:
    streamlit run app.py
"""

import streamlit as st

from utils.config  import APP_ICON, APP_TITLE
from utils.session import get_page_state, init_session_state
from utils.theme   import inject_theme


def main() -> None:
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout="wide",
        initial_sidebar_state="auto",
    )

    inject_theme()
    init_session_state()

    page = get_page_state()

    # ── Landing — no sidebar ───────────────────────────────────────────────
    if page == "landing":
        from utils.pages.landing import render_landing_page
        render_landing_page()
        return

    # ── Analysis workflow — no sidebar ────────────────────────────────────
    if page == "analyzing":
        from utils.pages.analyzing import render_analyzing_page
        render_analyzing_page()
        return

    # ── Settings ──────────────────────────────────────────────────────────
    if page == "settings":
        with st.sidebar:
            from utils.sidebar import render_sidebar
            render_sidebar()
        from utils.sidebar import render_settings_sidebar_page
        render_settings_sidebar_page()
        return

    # ── Main dashboard with tabs (default) ────────────────────────────────
    with st.sidebar:
        from utils.sidebar import render_sidebar
        render_sidebar()

    from utils.pages.main_dashboard import render_main_dashboard
    render_main_dashboard()


if __name__ == "__main__":
    main()
