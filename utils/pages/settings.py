"""⚙ Settings page."""

from __future__ import annotations

import streamlit as st

from utils.components import platform_header
from utils.config import OPENAI_API_KEY, OPENAI_MODEL
from utils.navigation import PAGE_TITLES
from utils.session import clear_messages
from utils.uploads import clear_uploads


def render_settings_page() -> None:
    title, subtitle = PAGE_TITLES["settings"]
    platform_header(title, subtitle)

    llm_ok = bool(OPENAI_API_KEY and OPENAI_API_KEY != "sk-your-key-here")

    st.markdown("#### 🤖 LLM Configuration")
    st.markdown(f"**Status:** {'✅ Active' if llm_ok else '⚪ Disabled (template mode)'}")
    st.text_input("Model", value=OPENAI_MODEL, disabled=True)
    st.caption("Set OPENAI_API_KEY in `.env` for enhanced AI Assistant narratives.")

    st.divider()
    st.markdown("#### 🏗 Agent Pipeline")
    st.markdown("""
    | Agent | Role |
    |-------|------|
    | **Analysis Agent** | Analyzes data, detects drifts, generates conclusions |
    | **Reviewer Agent** | Verifies evidence, adjusts confidence, requests more data |
    | **Planner Agent** | Routes assistant queries to appropriate tools |
    """)

    st.divider()
    st.markdown("#### 🧬 ML Models")
    st.markdown("""
    | Model | Purpose | Swappable |
    |-------|---------|-----------|
    | `EnsembleYieldModel` | Yield & failure prediction | ✅ via `models/prediction_model.py` |
    | `RiskScoringModel` | Process/yield/equipment risk | ✅ via `models/risk_model.py` |
    | `RootCauseModel` | RCA ranking | ✅ via `models/root_cause_model.py` |
    """)

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑 Clear Chat History", use_container_width=True):
            clear_messages()
            st.success("Chat cleared.")
    with col2:
        if st.button("🗑 Clear All Uploads", use_container_width=True):
            clear_uploads()
            st.session_state.platform_snapshot = None
            st.session_state.platform_engine.registry.clear()
            st.success("Uploads cleared.")
