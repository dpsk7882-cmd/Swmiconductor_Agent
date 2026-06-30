"""Reviewer Agent — verifies primary analysis reasoning and adjusts confidence."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from models.analysis_result import AnalysisResult
from models.process_rules import ProcessRuleEngine


@dataclass
class ReviewOutcome:
    """Result of the reviewer agent's verification pass."""

    approved: bool
    adjusted_confidence: float
    confidence_explanation: str
    reviewer_notes: str
    validation_issues: list[str] = field(default_factory=list)


class ReviewerAgent:
    """
    Second-pass agent that validates conclusions, checks evidence consistency,
    and produces a calibrated confidence score with explanation.
    """

    def __init__(self) -> None:
        self.rule_engine = ProcessRuleEngine()

    def review(
        self,
        result: AnalysisResult,
        tools_used: list[str],
        has_data: bool,
        has_pdf: bool,
        rag_hits: int = 0,
    ) -> ReviewOutcome:
        """Verify analysis result and compute final confidence score."""
        validation = self.rule_engine.validate_conclusion(
            result.process_health,
            result.confidence_score,
            result.anomalies,
        )

        issues = [i.message for i in validation.issues]
        score = self._base_confidence(has_data, has_pdf, tools_used, result)
        score = self._adjust_for_evidence(score, result, rag_hits)
        score = self._adjust_for_validation(score, validation.issues)
        score = max(0.0, min(100.0, score))

        explanation = self._explain_confidence(
            score, has_data, has_pdf, result, rag_hits, issues
        )
        notes = self._reviewer_notes(result, validation.passed, issues)

        return ReviewOutcome(
            approved=validation.passed or score >= 40,
            adjusted_confidence=round(score, 1),
            confidence_explanation=explanation,
            reviewer_notes=notes,
            validation_issues=issues,
        )

    def _base_confidence(
        self,
        has_data: bool,
        has_pdf: bool,
        tools_used: list[str],
        result: AnalysisResult,
    ) -> float:
        score = 30.0  # baseline for any response

        if has_data:
            score += 25.0
        if has_pdf:
            score += 10.0
        if len(tools_used) >= 3:
            score += 10.0
        if result.anomalies:
            score += min(len(result.anomalies) * 5, 15.0)
        if result.yield_factors:
            score += min(len(result.yield_factors) * 4, 12.0)
        if result.root_causes and result.root_causes[0].factor != "Insufficient data":
            score += 8.0
        if result.yield_forecast and result.yield_forecast.method not in ("none", "insufficient_data"):
            score += 10.0

        return score

    def _adjust_for_evidence(
        self, score: float, result: AnalysisResult, rag_hits: int
    ) -> float:
        if rag_hits > 0:
            score += min(rag_hits * 3, 9.0)
        if not result.anomalies and result.process_health in ("warning", "critical"):
            score -= 15.0
        if result.process_health == "healthy" and not result.anomalies:
            score += 5.0
        return score

    def _adjust_for_validation(self, score: float, issues: list) -> float:
        for issue in issues:
            if issue.severity == "warning":
                score -= 8.0
            elif issue.severity == "error":
                score -= 15.0
        return score

    def _explain_confidence(
        self,
        score: float,
        has_data: bool,
        has_pdf: bool,
        result: AnalysisResult,
        rag_hits: int,
        issues: list[str],
    ) -> str:
        parts: list[str] = []

        if score >= 75:
            parts.append("High confidence — strong quantitative evidence supports conclusions.")
        elif score >= 50:
            parts.append("Moderate confidence — conclusions supported but some gaps remain.")
        else:
            parts.append("Low confidence — limited data; treat as preliminary guidance.")

        if has_data:
            parts.append(f"Process data analyzed ({len(result.anomalies)} anomalies, "
                         f"{len(result.yield_factors)} yield factors).")
        else:
            parts.append("No process data uploaded — analysis is knowledge-based only.")

        if has_pdf and rag_hits:
            parts.append(f"PDF manual context: {rag_hits} relevant excerpt(s) retrieved.")
        elif has_pdf:
            parts.append("PDF loaded but no strongly relevant manual excerpts matched the query.")

        if result.yield_forecast and result.yield_forecast.predicted_yield is not None:
            parts.append(
                f"Yield forecast via {result.yield_forecast.method}: "
                f"{result.yield_forecast.current_yield}% → "
                f"{result.yield_forecast.predicted_yield}% projected."
            )

        if issues:
            parts.append(f"Reviewer flags: {'; '.join(issues)}")

        return " ".join(parts)

    def _reviewer_notes(
        self, result: AnalysisResult, validation_passed: bool, issues: list[str]
    ) -> str:
        if validation_passed and not issues:
            return "Reviewer: Analysis reasoning is internally consistent with available evidence."
        if issues:
            return f"Reviewer: Adjusted confidence due to: {'; '.join(issues)}"
        return "Reviewer: Conclusions accepted with standard caveats."
