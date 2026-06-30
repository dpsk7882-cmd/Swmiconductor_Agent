"""💬 AI Assistant — secondary engineering copilot."""

from __future__ import annotations

import streamlit as st

from utils.components import platform_header
from utils.data_sync import sync_registry
from utils.navigation import PAGE_TITLES
from utils.session import append_message, get_engine, get_messages, get_snapshot


def render_assistant_page() -> None:
    title, subtitle = PAGE_TITLES["assistant"]
    platform_header(title, subtitle)

    sync_registry()
    snap_dict = get_snapshot()
    messages = get_messages()

    st.caption(
        "Secondary engineering copilot. Primary decisions should use the dedicated analysis pages."
    )

    if snap_dict:
        with st.expander("📊 Current Platform Context", expanded=False):
            st.json({
                "status": snap_dict.get("process_status"),
                "risk": snap_dict.get("risk", {}).get("risk_level"),
                "confidence": snap_dict.get("explainability", {}).get("confidence_score"),
            })

    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ask about process conditions, drifts, yield, or maintenance...")
    if prompt:
        append_message("user", prompt)
        engine = get_engine()
        history = [m for m in messages if m["role"] in ("user", "assistant")]
        reply = engine.query_assistant(prompt, snapshot_dict=snap_dict, history=history)
        append_message("assistant", reply)
        st.rerun()
