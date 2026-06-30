"""Automatic file type detection and routing to appropriate tools."""

from __future__ import annotations

from typing import Literal

FileKind = Literal["pdf", "excel", "csv", "log_txt", "unknown"]

EXTENSION_MAP: dict[str, FileKind] = {
    ".pdf": "pdf",
    ".xlsx": "excel",
    ".xls": "excel",
    ".csv": "csv",
    ".txt": "log_txt",
    ".log": "log_txt",
}


class FileRouter:
    """Recognize uploaded file types and route to the correct ingestion tool."""

    @staticmethod
    def detect(filename: str, content_preview: bytes | None = None) -> FileKind:
        ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext in EXTENSION_MAP:
            return EXTENSION_MAP[ext]

        if content_preview:
            if content_preview[:4] == b"%PDF":
                return "pdf"
            if b"," in content_preview[:200] or b"\t" in content_preview[:200]:
                return "csv"

        return "unknown"

    @staticmethod
    def label(kind: FileKind) -> str:
        return {
            "pdf": "📄 PDF Manual",
            "excel": "📊 Excel Process Data",
            "csv": "📋 CSV Dataset",
            "log_txt": "📝 Equipment Log",
            "unknown": "❓ Unknown",
        }.get(kind, "❓ Unknown")

    @staticmethod
    def icon(kind: FileKind) -> str:
        return {
            "pdf": "📄",
            "excel": "📊",
            "csv": "📋",
            "log_txt": "📝",
            "unknown": "❓",
        }.get(kind, "❓")

    @staticmethod
    def accepted_extensions() -> list[str]:
        return ["pdf", "xlsx", "xls", "csv", "txt", "log"]
