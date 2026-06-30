"""Reviewer Agent — verifies Analysis Agent conclusions before release."""

from __future__ import annotations

from models.platform_snapshot import AgentVerdict, PlatformSnapshot


class ReviewerAgent:
    """
    Agent 2 — reviews every conclusion, checks evidence consistency,
    detects contradictions, and requests more data when confidence is low.
    """

    MIN_CONFIDENCE = 45.0
    HIGH_CONFIDENCE = 75.0

    def review(self, snapshot: PlatformSnapshot, has_data: bool, has_pdf: bool) -> PlatformSnapshot:
        """Review snapshot, set confidence, and produce dual-agent verdict."""
        score = self._compute_confidence(snapshot, has_data, has_pdf)
        issues = self._find_contradictions(snapshot)
        needs_data, requests = self._check_data_sufficiency(snapshot, has_data, score)

        score = self._adjust_score(score, issues, needs_data)
        explanation = self._explain_confidence(score, snapshot, has_data, has_pdf, issues, needs_data)
        evidence_strength = self._evidence_strength(snapshot, has_data, issues)

        approved = score >= self.MIN_CONFIDENCE and not needs_data
        reviewed = self._build_reviewed_analysis(snapshot, approved, issues, needs_data)

        notes = "Reviewer: Analysis approved — evidence supports conclusions."
        if issues:
            notes = f"Reviewer: Adjusted for contradictions — {'; '.join(issues)}"
        if needs_data:
            notes = f"Reviewer: Insufficient data — {'; '.join(requests)}"
        if not approved and not needs_data:
            notes = "Reviewer: Low confidence — interpret with engineering judgment."

        snapshot.explainability.confidence_score = round(score, 1)
        snapshot.explainability.confidence_explanation = explanation
        snapshot.agent_verdict = AgentVerdict(
            original_analysis=snapshot.agent_verdict.original_analysis if snapshot.agent_verdict else "",
            reviewed_analysis=reviewed,
            approved=approved,
            reviewer_notes=notes,
            needs_more_data=needs_data,
            data_requests=requests,
            analysis_verified=approved and not needs_data,
            contradiction_found=len(issues) > 0,
            evidence_strength=round(evidence_strength, 1),
        )
        return snapshot

    def _evidence_strength(self, snap: PlatformSnapshot, has_data: bool, issues: list[str]) -> float:
        """Score how strongly available evidence supports the analysis (0–100)."""
        score = 30.0 if has_data else 10.0
        score += min(len(snap.explainability.evidence) * 8, 24.0)
        score += min(len(snap.drifts) * 5, 20.0)
        score += min(len(snap.yield_factors) * 4, 12.0)
        if snap.root_causes and snap.root_causes[0].get("factor") != "Insufficient data":
            score += 10.0
        score -= len(issues) * 12
        return max(0.0, min(100.0, score))

    def _compute_confidence(self, snap: PlatformSnapshot, has_data: bool, has_pdf: bool) -> float:
        score = 25.0
        if has_data:
            score += 30.0
        if has_pdf:
            score += 8.0
        score += min(len(snap.drifts) * 4, 16.0)
        score += min(len(snap.yield_factors) * 3, 12.0)
        if snap.root_causes and snap.root_causes[0].get("factor") != "Insufficient data":
            score += 10.0
        if snap.prediction.current_yield is not None:
            score += 12.0
        if snap.prediction.model_name:
            score += 5.0
        return min(score, 92.0)

    def _find_contradictions(self, snap: PlatformSnapshot) -> list[str]:
        issues: list[str] = []
        if snap.process_status == "Normal" and len(snap.drifts) >= 3:
            issues.append("Status Normal but multiple drift signals detected")
            snap.process_status = "Watch"
        if snap.risk.risk_level == "Low" and snap.process_status == "Alert":
            issues.append("Risk Low conflicts with Alert status — risk elevated")
            snap.risk.risk_level = "Medium"
        if snap.explainability.confidence_score >= 90 and not snap.drifts and not snap.yield_factors:
            issues.append("High confidence without supporting signals")
        return issues

    def _check_data_sufficiency(
        self, snap: PlatformSnapshot, has_data: bool, score: float
    ) -> tuple[bool, list[str]]:
        requests: list[str] = []
        if not has_data:
            requests.append("Upload Excel process data or equipment logs for quantitative analysis.")
            return True, requests
        if snap.prediction.current_yield is None:
            requests.append("Dataset lacks a yield column — add yield_pct for prediction.")
        if len(snap.drifts) == 0 and len(snap.yield_factors) == 0 and score < 50:
            requests.append("Insufficient signal in current dataset — upload additional lots or longer history.")
            return True, requests
        return False, requests

    def _adjust_score(self, score: float, issues: list[str], needs_data: bool) -> float:
        score -= len(issues) * 10
        if needs_data:
            score = min(score, 40.0)
        return max(0.0, min(100.0, score))

    def _explain_confidence(
        self, score, snap, has_data, has_pdf, issues, needs_data
    ) -> str:
        tier = "High" if score >= self.HIGH_CONFIDENCE else "Moderate" if score >= self.MIN_CONFIDENCE else "Low"
        parts = [f"{tier} confidence ({score:.0f}%)."]
        if has_data:
            parts.append(f"{len(snap.drifts)} drift signal(s), {len(snap.yield_factors)} yield factor(s).")
        else:
            parts.append("No process data — conclusions are advisory only.")
        if snap.prediction.top_variables:
            parts.append(f"Key drivers: {', '.join(snap.prediction.top_variables[:3])}.")
        if issues:
            parts.append(f"Reviewer adjustments: {'; '.join(issues)}.")
        if needs_data:
            parts.append("More data recommended before acting on predictions.")
        return " ".join(parts)

    @staticmethod
    def _build_reviewed_analysis(
        snap: PlatformSnapshot, approved: bool, issues: list[str], needs_data: bool
    ) -> str:
        if needs_data:
            return (
                f"⚠️ Analysis incomplete — upload additional data before final decisions. "
                f"Preliminary: {snap.process_status} status, {snap.risk.risk_level} risk."
            )
        status_icon = {"Normal": "🟢", "Watch": "🟡", "Alert": "🔴"}.get(snap.process_status, "⚪")
        verdict = "Verified" if approved else "Low confidence — verify manually"
        return (
            f"{status_icon} {verdict}: Process {snap.process_status}, "
            f"Risk {snap.risk.risk_level} ({snap.risk.risk_score}/100). "
            f"Yield {snap.current_yield}% → {snap.predicted_yield}%. "
            f"{len(snap.drifts)} drift(s), top cause: "
            f"{snap.root_causes[0].get('factor', 'N/A') if snap.root_causes else 'N/A'}."
        )
