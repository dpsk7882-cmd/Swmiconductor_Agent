"""Process risk scoring model for fab decision support."""

from __future__ import annotations

from typing import Any

import pandas as pd

from models.platform_snapshot import DriftSignal, RiskAssessment, RiskLevel


class RiskScoringModel:
    """
    Computes Process Stability, Yield Risk, Equipment Risk,
    and an aggregate Risk Score (0–100) mapped to Low/Medium/High.
    """

    def assess(
        self,
        drifts: list[DriftSignal],
        current_yield: float | None,
        predicted_yield: float | None,
        failure_probability: float,
        log_alarm_count: int = 0,
    ) -> RiskAssessment:
        stability_score = self._stability_score(drifts)
        yield_score = self._yield_risk_score(current_yield, predicted_yield)
        equip_score = self._equipment_risk_score(drifts, failure_probability, log_alarm_count)

        aggregate = 0.35 * stability_score + 0.35 * yield_score + 0.30 * equip_score
        risk_level = self._to_level(aggregate)

        factors: list[str] = []
        high_drifts = [d for d in drifts if d.severity in ("high", "critical")]
        if high_drifts:
            factors.append(f"{len(high_drifts)} high-severity drift signal(s) active.")
        if yield_score >= 55:
            factors.append("Yield trajectory indicates elevated loss risk.")
        if equip_score >= 55:
            factors.append("Equipment instability or alarm activity detected.")

        return RiskAssessment(
            process_stability=self._to_level(stability_score),
            yield_risk=self._to_level(yield_score),
            equipment_risk=self._to_level(equip_score),
            risk_level=risk_level,
            risk_score=round(aggregate, 1),
            summary=self._summary(risk_level, factors),
            factors=factors,
        )

    def _stability_score(self, drifts: list[DriftSignal]) -> float:
        if not drifts:
            return 15.0
        score = 20.0
        for d in drifts:
            if d.severity == "critical":
                score += 22
            elif d.severity == "high":
                score += 14
            elif d.severity == "medium":
                score += 8
            else:
                score += 4
        return min(score, 100.0)

    def _yield_risk_score(
        self, current: float | None, predicted: float | None
    ) -> float:
        if current is None:
            return 40.0
        if predicted is None:
            return 35.0
        drop = current - predicted
        if drop >= 3:
            return 85.0
        if drop >= 1.5:
            return 60.0
        if drop >= 0.5:
            return 40.0
        if current < 85:
            return 70.0
        if current < 90:
            return 45.0
        return 20.0

    def _equipment_risk_score(
        self, drifts: list[DriftSignal], fail_prob: float, alarms: int
    ) -> float:
        score = fail_prob * 60
        equip_drifts = [
            d for d in drifts
            if d.category in ("RF Power Drift", "Equipment Instability", "ARC Events", "High-Z Events")
        ]
        score += len(equip_drifts) * 10
        score += min(alarms * 8, 30)
        return min(score, 100.0)

    @staticmethod
    def _to_level(score: float) -> RiskLevel:
        if score >= 60:
            return "High"
        if score >= 35:
            return "Medium"
        return "Low"

    @staticmethod
    def _summary(level: RiskLevel, factors: list[str]) -> str:
        if not factors:
            return f"Overall risk is {level}. No significant drift or degradation signals."
        return f"Overall risk is {level}. " + " ".join(factors[:2])
