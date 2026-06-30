"""Platform engine — coordinates Analysis Agent, Reviewer Agent, and data sync."""

from __future__ import annotations

from agents.analysis_agent import AnalysisAgent
from agents.reviewer_agent import ReviewerAgent
from models.platform_snapshot import PlatformSnapshot
from tools.registry import ToolRegistry


class PlatformEngine:
    """Top-level orchestrator for the industrial AI platform."""

    def __init__(self, registry: ToolRegistry | None = None) -> None:
        self.registry = registry or ToolRegistry()
        self.analysis_agent = AnalysisAgent(self.registry)
        self.reviewer_agent = ReviewerAgent()

    def run_analysis(self, uploaded_files: list[str] | None = None) -> PlatformSnapshot:
        """Execute Analysis Agent → Reviewer Agent pipeline."""
        snapshot = self.analysis_agent.analyze(uploaded_files=uploaded_files)
        has_data = len(self.registry.combined_frames) > 0
        has_pdf = not self.registry.pdf_rag.is_empty
        return self.reviewer_agent.review(snapshot, has_data=has_data, has_pdf=has_pdf)

    def query_manual(self, question: str, top_k: int = 4) -> list[dict[str, str]]:
        """RAG query against uploaded PDF knowledge base."""
        return self.registry.pdf_rag.retrieve(question, top_k=top_k)

    def query_assistant(
        self,
        question: str,
        snapshot: PlatformSnapshot | None = None,
        snapshot_dict: dict | None = None,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        """Context-aware assistant response (secondary to dashboard)."""
        from utils.llm import LLMClient, SEMICONDUCTOR_SYSTEM_PROMPT

        llm = LLMClient()
        context_parts: list[str] = []

        sd = snapshot_dict
        if snapshot and not sd:
            sd = snapshot.to_dict()

        if sd:
            context_parts.append(f"Platform Status: {sd.get('process_status')}")
            risk = sd.get("risk", {})
            context_parts.append(f"Risk: {risk.get('risk_level')} ({risk.get('risk_score')})")
            expl = sd.get("explainability", {})
            context_parts.append(f"Confidence: {expl.get('confidence_score')}%")
            verdict = sd.get("agent_verdict") or {}
            if verdict.get("reviewed_analysis"):
                context_parts.append(verdict["reviewed_analysis"])

        rag = self.registry.pdf_rag.build_context(question)
        if rag:
            context_parts.append(rag)

        if llm.is_available:
            return llm.chat(question, history or [], SEMICONDUCTOR_SYSTEM_PROMPT, "\n".join(context_parts))

        conf = (sd or {}).get("explainability", {}).get("confidence_score", 0)
        if sd and sd.get("drifts"):
            verdict = sd.get("agent_verdict") or {}
            return (
                f"**Engineering Summary** (confidence {conf:.0f}%)\n\n"
                f"{verdict.get('reviewed_analysis', '')}\n\n"
                f"Active drifts: {len(sd.get('drifts', []))}. "
                f"See **Process Risk Assessment** and **Root Cause Analysis** pages."
            )
        return (
            "Upload process data via the sidebar, then run **Full Platform Analysis** from the Dashboard. "
            "Primary intelligence is on the dedicated analysis pages — not this chat."
        )
