"""Streamlit session state management for the platform."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import streamlit as st

from models.message import ChatMessage

if TYPE_CHECKING:
    from agents.platform_engine import PlatformEngine

__all__ = [
    "init_session_state",
    "get_engine",
    "get_orchestrator",
    "get_snapshot",
    "set_snapshot",
    "get_last_analysis",
    "set_last_analysis",
    "run_platform_analysis",
    "get_messages",
    "append_message",
    "clear_messages",
    # UI flow
    "get_page_state",
    "set_page_state",
    "get_analysis_step",
    "set_analysis_step",
    "reset_to_landing",
]


def _create_engine() -> PlatformEngine:
    from agents.platform_engine import PlatformEngine
    from tools.registry import ToolRegistry
    return PlatformEngine(ToolRegistry())


def init_session_state() -> None:
    """Initialize all session keys on first load."""
    defaults: dict[str, Any] = {
        # UI flow state: "landing" | "analyzing" | "dashboard"
        "page_state":        "landing",
        "analysis_step":     0,
        # Data
        "messages":          [],
        "uploads":           [],
        "upload_bytes":      {},
        "platform_snapshot": None,
        "analysis_history":  [],
        # Registry tracking
        "registry_initialized": False,
        "ingested_ids":      set(),
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if "platform_engine" not in st.session_state:
        st.session_state.platform_engine = _create_engine()


# ── UI flow helpers ───────────────────────────────────────────────────────────

def get_page_state() -> str:
    return st.session_state.get("page_state", "landing")


def set_page_state(state: str) -> None:
    st.session_state.page_state = state


def get_analysis_step() -> int:
    return st.session_state.get("analysis_step", 0)


def set_analysis_step(step: int) -> None:
    st.session_state.analysis_step = step


def reset_to_landing() -> None:
    """Reset platform state so user can run a new analysis."""
    st.session_state.page_state        = "landing"
    st.session_state.analysis_step     = 0
    st.session_state.platform_snapshot = None
    st.session_state.uploads           = []
    st.session_state.upload_bytes      = {}
    st.session_state.registry_initialized = False
    st.session_state.ingested_ids      = set()
    if "platform_engine" in st.session_state:
        try:
            st.session_state.platform_engine.registry.clear()
        except Exception:
            pass


# ── Engine ────────────────────────────────────────────────────────────────────

def get_engine() -> PlatformEngine:
    if "platform_engine" not in st.session_state:
        init_session_state()
    return st.session_state.platform_engine


def get_orchestrator() -> PlatformEngine:
    """Backward-compatible alias."""
    return get_engine()


# ── Snapshot ──────────────────────────────────────────────────────────────────

def get_snapshot() -> dict[str, Any] | None:
    return st.session_state.get("platform_snapshot")


def get_last_analysis() -> dict[str, Any] | None:
    return get_snapshot()


def set_snapshot(snapshot: Any) -> None:
    if hasattr(snapshot, "to_dict"):
        data = snapshot.to_dict()
    elif isinstance(snapshot, dict):
        data = snapshot
    else:
        raise TypeError("set_snapshot expects a PlatformSnapshot or dict.")

    st.session_state.platform_snapshot = data

    history = list(st.session_state.get("analysis_history", []))
    verdict = data.get("agent_verdict") or {}
    history.insert(0, {
        "timestamp":  data.get("analysis_timestamp", ""),
        "status":     data.get("process_status", "Unknown"),
        "risk":       (data.get("risk") or {}).get("risk_level", "—"),
        "confidence": (data.get("explainability") or {}).get("confidence_score", 0),
        "summary":    verdict.get("reviewed_analysis", ""),
    })
    st.session_state.analysis_history = history[:10]


def set_last_analysis(result: Any) -> None:
    set_snapshot(result)


def run_platform_analysis(uploaded_files: list[str]) -> None:
    engine = get_engine()
    snapshot = engine.run_analysis(uploaded_files=uploaded_files)
    set_snapshot(snapshot)


# ── Messages ──────────────────────────────────────────────────────────────────

def get_messages() -> list[dict[str, str]]:
    return list(st.session_state.get("messages", []))


def append_message(role: str, content: str) -> None:
    st.session_state.messages.append(ChatMessage(role=role, content=content).to_dict())


def clear_messages() -> None:
    st.session_state.messages = []
