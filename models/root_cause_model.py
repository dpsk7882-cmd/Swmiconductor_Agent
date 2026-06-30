"""Root cause ranking model — wraps RCA engine with explainability."""

from __future__ import annotations

from typing import Any

from models.analysis_result import RootCauseItem
from tools.rca_engine import RCAEngine


class RootCauseModel:
    """Rank and explain yield degradation root causes."""

    def __init__(self) -> None:
        self._engine = RCAEngine()

    def rank(
        self,
        drifts: list[Any],
        yield_factors: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Convert drifts + yield factors into ranked root cause dicts."""
        anomalies = [
            {
                "parameter": d.parameter if hasattr(d, "parameter") else d.get("parameter", ""),
                "message": d.message if hasattr(d, "message") else d.get("message", ""),
                "severity": d.severity if hasattr(d, "severity") else d.get("severity", "medium"),
                "type": d.category if hasattr(d, "category") else d.get("category", ""),
            }
            for d in drifts
        ]
        items: list[RootCauseItem] = self._engine.analyze(anomalies, yield_factors)
        results: list[dict[str, Any]] = []
        for item in items:
            why = self._explain_why(item, yield_factors)
            results.append({
                "rank": item.rank,
                "factor": item.factor,
                "score": item.score,
                "evidence": item.evidence,
                "explanation": why,
            })
        return results

    @staticmethod
    def _explain_why(item: RootCauseItem, yield_factors: list[dict[str, Any]]) -> str:
        matching = [f for f in yield_factors if item.factor.lower() in str(f.get("parameter", "")).lower()]
        if matching:
            return matching[0].get("interpretation", f"{item.factor} shows measurable impact on yield.")
        if item.evidence:
            return f"Ranked #{item.rank} because: {item.evidence[0]}"
        return f"{item.factor} contributes to observed process deviation patterns."
