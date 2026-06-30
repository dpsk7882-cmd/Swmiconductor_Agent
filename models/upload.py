"""Uploaded file metadata model."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

FileType = Literal["pdf", "excel", "csv"]


@dataclass
class UploadedFileRecord:
    """Metadata for a file uploaded through the sidebar."""

    filename: str
    file_type: FileType
    size_bytes: int
    upload_id: str

    def to_dict(self) -> dict[str, str | int]:
        return asdict(self)

    @property
    def size_label(self) -> str:
        size = float(self.size_bytes)
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024 or unit == "GB":
                return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
            size /= 1024
        return f"{self.size_bytes} B"
