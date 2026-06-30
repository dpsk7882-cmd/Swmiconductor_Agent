from openai import OpenAI

from src.config import OPENAI_API_KEY, OPENAI_MODEL, SYSTEM_PROMPT


class ChatAgent:
    """OpenAI-powered chat agent with document context."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or OPENAI_API_KEY
        self.model = model or OPENAI_MODEL
        self._client: OpenAI | None = None

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    @property
    def client(self) -> OpenAI:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not set.")
        if self._client is None:
            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def build_messages(
        self,
        user_message: str,
        history: list[dict],
        pdf_context: str = "",
        excel_context: str = "",
    ) -> list[dict]:
        context_parts = []
        if pdf_context:
            context_parts.append(pdf_context)
        if excel_context:
            context_parts.append(excel_context)

        system_content = SYSTEM_PROMPT
        if context_parts:
            system_content += "\n\nUse the following uploaded document context when answering:\n\n"
            system_content += "\n\n".join(context_parts)

        messages: list[dict] = [{"role": "system", "content": system_content}]
        for turn in history:
            messages.append({"role": turn["role"], "content": turn["content"]})
        messages.append({"role": "user", "content": user_message})
        return messages

    def chat(
        self,
        user_message: str,
        history: list[dict],
        pdf_context: str = "",
        excel_context: str = "",
    ) -> str:
        messages = self.build_messages(user_message, history, pdf_context, excel_context)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,
        )
        return response.choices[0].message.content or "No response generated."
