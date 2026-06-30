"""Chat message data model."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Literal

Role = Literal["user", "assistant", "system"]


@dataclass
class ChatMessage:
    """Represents a single message in the conversation history."""

    role: Role
    content: str

    def to_dict(self) -> dict[str, str]:
        """Serialize the message for Streamlit session state storage."""
        return asdict(self)
