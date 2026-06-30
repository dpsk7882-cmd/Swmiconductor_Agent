"""Optional LLM client for narrative generation (OpenAI-compatible)."""

from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()

SEMICONDUCTOR_SYSTEM_PROMPT = """You are an expert semiconductor process engineering AI assistant.
You analyze fab process data, equipment logs, and technical manuals to help engineers:
- Detect abnormal process parameters
- Identify yield degradation factors
- Perform root cause analysis
- Forecast yield trends
- Recommend preventive maintenance

Always cite evidence from the provided analysis context. Be precise with units and terminology.
Structure responses clearly with headers. Include confidence caveats when data is limited.
Do not invent measurements not present in the context."""


class LLMClient:
    """Thin wrapper around OpenAI chat completions with graceful fallback."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self._client: Any = None

    @property
    def is_available(self) -> bool:
        return bool(self.api_key and self.api_key != "sk-your-key-here")

    def _get_client(self) -> Any:
        if not self.is_available:
            raise ValueError("OPENAI_API_KEY not configured.")
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def chat(
        self,
        user_message: str,
        history: list[dict[str, str]] | None = None,
        system_prompt: str = SEMICONDUCTOR_SYSTEM_PROMPT,
        extra_context: str = "",
    ) -> str:
        """Send a chat completion request."""
        if not self.is_available:
            return ""

        system = system_prompt
        if extra_context:
            system += f"\n\n--- Analysis Context ---\n{extra_context}\n--- End Context ---"

        messages: list[dict[str, str]] = [{"role": "system", "content": system}]
        for turn in history or []:
            if turn["role"] in ("user", "assistant"):
                messages.append({"role": turn["role"], "content": turn["content"]})
        messages.append({"role": "user", "content": user_message})

        client = self._get_client()
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.2,
        )
        return response.choices[0].message.content or ""
