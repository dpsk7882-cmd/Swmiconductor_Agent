"""Unified file upload with automatic type detection."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import streamlit as st

from tools.file_router import FileKind, FileRouter

if TYPE_CHECKING:
    from streamlit.runtime.uploaded_file_manager import UploadedFile

# Legacy sidebar uploader config (utils/ui.py)
UPLOADERS: dict[str, dict[str, object]] = {
    "pdf": {"label": "PDF manual", "types": ["pdf"], "icon": "📄"},
    "excel": {"label": "Excel process data", "types": ["xlsx", "xls"], "icon": "📊"},
    "csv": {"label": "Equipment log (CSV/TXT)", "types": ["csv", "txt"], "icon": "📋"},
}

_LEGACY_TYPE_TO_KIND: dict[str, FileKind] = {
    "pdf": "pdf",
    "excel": "excel",
    "csv": "csv",
}


def get_uploads() -> list[dict]:
    return st.session_state.uploads


def get_upload_bytes(upload_id: str) -> bytes | None:
    return st.session_state.upload_bytes.get(upload_id)


def get_uploads_by_type(file_type: str) -> list[dict]:
    """Legacy helper — filter uploads by pdf / excel / csv."""
    kind = _LEGACY_TYPE_TO_KIND.get(file_type, file_type)
    return [
        u for u in get_uploads()
        if u.get("file_kind") == kind or u.get("file_type") == file_type
    ]


def register_upload(uploaded_file: UploadedFile, file_type: str | None = None) -> dict:
    """Auto-detect file type (or use legacy file_type hint) and store metadata + bytes."""
    file_bytes = uploaded_file.getvalue()

    if file_type and file_type in _LEGACY_TYPE_TO_KIND:
        kind: FileKind = _LEGACY_TYPE_TO_KIND[file_type]
    else:
        kind = FileRouter.detect(uploaded_file.name, file_bytes[:512])

    record = {
        "upload_id": str(uuid.uuid4()),
        "filename": uploaded_file.name,
        "file_kind": kind,
        "file_type": file_type or kind,  # legacy key for older UI code
        "size_bytes": uploaded_file.size,
        "label": FileRouter.label(kind),
        "icon": FileRouter.icon(kind),
    }

    uploads = [u for u in get_uploads() if u["filename"] != uploaded_file.name]
    old_ids = [u["upload_id"] for u in get_uploads() if u["filename"] == uploaded_file.name]
    for oid in old_ids:
        st.session_state.upload_bytes.pop(oid, None)

    uploads.append(record)
    st.session_state.uploads = uploads
    st.session_state.upload_bytes[record["upload_id"]] = file_bytes
    st.session_state.registry_initialized = False
    return record


def remove_upload(upload_id: str) -> None:
    st.session_state.uploads = [u for u in get_uploads() if u["upload_id"] != upload_id]
    st.session_state.upload_bytes.pop(upload_id, None)
    st.session_state.registry_initialized = False


def clear_uploads() -> None:
    st.session_state.uploads = []
    st.session_state.upload_bytes = {}
    st.session_state.registry_initialized = False
    st.session_state.platform_snapshot = None


def get_filenames() -> list[str]:
    return [u["filename"] for u in get_uploads()]
