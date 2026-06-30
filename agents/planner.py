"""Planner Agent — decides which analysis tools to invoke for a user query."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PlanStep:
    """Single tool invocation in the execution plan."""

    tool: str
    reason: str


@dataclass
class ExecutionPlan:
    """Ordered list of tools the orchestrator should run."""

    steps: list[PlanStep] = field(default_factory=list)
    query_type: str = "general"
    rationale: str = ""

    @property
    def tool_names(self) -> list[str]:
        return [s.tool for s in self.steps]


# Keyword patterns mapped to tools (rule-based planner — no LLM required).
INTENT_PATTERNS: list[tuple[str, list[str], list[str]]] = [
    (
        "full_analysis",
        [r"\banaly[sz]e\b", r"\bhealth\b", r"\boverview\b", r"\bdiagnos", r"\bfull report\b"],
        ["detect_anomalies", "analyze_yield", "root_cause_analysis", "forecast_yield", "recommend_maintenance"],
    ),
    (
        "anomaly",
        [r"\banomal", r"\bout of spec\b", r"\babnormal", r"\bspike", r"\bdeviat"],
        ["detect_anomalies"],
    ),
    (
        "yield",
        [r"\byield\b", r"\bdegrad", r"\bdefect", r"\bscrap", r"\bbin"],
        ["analyze_yield", "forecast_yield"],
    ),
    (
        "rca",
        [r"\broot cause\b", r"\brca\b", r"\bwhy\b", r"\bcause\b"],
        ["detect_anomalies", "analyze_yield", "root_cause_analysis"],
    ),
    (
        "forecast",
        [r"\bforecast\b", r"\bpredict\b", r"\bfuture\b", r"\btrend\b", r"\bprojection\b"],
        ["forecast_yield", "analyze_yield"],
    ),
    (
        "maintenance",
        [r"\bmaintenance\b", r"\bpm\b", r"\bprevent", r"\bfailure\b", r"\balarm\b"],
        ["detect_anomalies", "recommend_maintenance"],
    ),
    (
        "manual",
        [r"\bmanual\b", r"\bdocument", r"\bspec\b", r"\bprocedure\b", r"\brecipe\b", r"\bsop\b"],
        ["rag_query"],
    ),
]


class PlannerAgent:
    """Select analysis tools based on user intent and available uploads."""

    def __init__(self, has_pdf: bool = False, has_data: bool = False) -> None:
        self.has_pdf = has_pdf
        self.has_data = has_data

    def plan(self, user_query: str) -> ExecutionPlan:
        """Build an execution plan for the given user message."""
        query_lower = user_query.lower()
        matched_type = "general"
        tools: list[str] = []

        for query_type, patterns, tool_list in INTENT_PATTERNS:
            if any(re.search(p, query_lower) for p in patterns):
                matched_type = query_type
                tools.extend(tool_list)
                break

        # Context-aware adjustments
        if self.has_pdf and ("manual" in query_lower or "document" in query_lower or matched_type == "general"):
            if "rag_query" not in tools:
                tools.insert(0, "rag_query")

        if self.has_data and matched_type == "general":
            # Default data question → run core analysis pipeline
            tools = [
                "detect_anomalies",
                "analyze_yield",
                "root_cause_analysis",
                "forecast_yield",
                "recommend_maintenance",
            ]
            matched_type = "data_analysis"

        if not tools:
            tools = ["general_qa"]
            if self.has_pdf:
                tools.insert(0, "rag_query")

        # Deduplicate while preserving order
        seen: set[str] = set()
        unique_tools: list[str] = []
        for t in tools:
            if t not in seen:
                seen.add(t)
                unique_tools.append(t)

        steps = [
            PlanStep(tool=t, reason=self._reason_for_tool(t, matched_type))
            for t in unique_tools
        ]

        return ExecutionPlan(
            steps=steps,
            query_type=matched_type,
            rationale=self._build_rationale(matched_type, unique_tools),
        )

    def _reason_for_tool(self, tool: str, query_type: str) -> str:
        reasons = {
            "rag_query": "User query may be answered from uploaded PDF manuals.",
            "detect_anomalies": "Check process parameters against spec and statistical baselines.",
            "analyze_yield": "Identify parameters correlated with yield degradation.",
            "root_cause_analysis": "Rank hypothesized root causes from combined signals.",
            "forecast_yield": "Project future yield trend from historical data.",
            "recommend_maintenance": "Generate preventive maintenance actions.",
            "general_qa": "Answer general semiconductor process question.",
        }
        return reasons.get(tool, f"Selected for {query_type} intent.")

    def _build_rationale(self, query_type: str, tools: list[str]) -> str:
        data_note = "process data loaded" if self.has_data else "no process data"
        pdf_note = "PDF manuals loaded" if self.has_pdf else "no PDFs"
        return (
            f"Classified query as '{query_type}' with {data_note} and {pdf_note}. "
            f"Selected tools: {', '.join(tools)}."
        )
