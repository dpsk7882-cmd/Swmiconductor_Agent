"""Sync uploads into the platform tool registry."""

from __future__ import annotations

import streamlit as st

from utils.uploads import get_upload_bytes, get_uploads


def sync_registry() -> None:
    engine = st.session_state.platform_engine
    registry = engine.registry

    current_ids = {u["upload_id"] for u in get_uploads()}
    if st.session_state.get("registry_initialized") and current_ids == st.session_state.get("ingested_ids", set()):
        return

    registry.clear()
    ingested: set[str] = set()

    for record in get_uploads():
        uid = record["upload_id"]
        data = get_upload_bytes(uid)
        if not data:
            continue
        kind = record["file_kind"]
        name = record["filename"]
        try:
            if kind == "pdf":
                registry.ingest_pdf(data, name)
            elif kind == "excel":
                registry.ingest_excel(data, name)
            elif kind in ("csv", "log_txt"):
                registry.ingest_log(data, name)
            ingested.add(uid)
        except Exception as exc:
            st.session_state.setdefault("ingest_errors", {})[uid] = str(exc)

    st.session_state.ingested_ids = ingested
    st.session_state.registry_initialized = True


# Backward-compatible alias for legacy modules
sync_uploads_to_registry = sync_registry
