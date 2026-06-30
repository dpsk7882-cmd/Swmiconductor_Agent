"""Root Cause Analysis engine combining anomalies and yield factors."""

from __future__ import annotations

from typing import Any

from models.analysis_result import RootCauseItem


class RCAEngine:
    """Rank root-cause hypotheses from anomalies and yield degradation signals."""

    # Known causal relationships in fab processes (simplified knowledge graph).
    CAUSAL_HINTS: dict[str, list[str]] = {
        "chamber_temp_c": ["thermal_uniformity", "film_stress", "cd_variation"],
        "chamber_pressure_mtorr": ["plasma_instability", "etch_non_uniformity"],
        "rf_power_w": ["plasma_density", "selectivity", "chamber_conditioning"],
        "gas_flow_sccm": ["chemistry_balance", "particle_generation"],
        "etch_rate_nm_min": ["endpoint_detection", "profile_control"],
        "overlay_nm": ["litho_alignment", "tool_matching"],
        "defect_density_cm2": ["particle_contamination", "cleaning_cycle"],
    }

    def analyze(
        self,
        anomalies: list[dict[str, Any]],
        yield_factors: list[dict[str, Any]],
    ) -> list[RootCauseItem]:
        """Produce a ranked list of root-cause hypotheses."""
        scores: dict[str, dict[str, Any]] = {}

        for anomaly in anomalies:
            param = anomaly.get("parameter", anomaly.get("column", "unknown"))
            weight = 1.0 if anomaly.get("severity") == "high" else 0.6
            if param not in scores:
                scores[param] = {"score": 0.0, "evidence": []}
            scores[param]["score"] += weight
            scores[param]["evidence"].append(anomaly.get("message", str(anomaly)))

        for factor in yield_factors:
            param = factor.get("parameter", "unknown")
            impact = factor.get("impact_score", 0.5)
            if param not in scores:
                scores[param] = {"score": 0.0, "evidence": []}
            scores[param]["score"] += impact * 1.2
            scores[param]["evidence"].append(factor.get("interpretation", str(factor)))

        if not scores:
            return [
                RootCauseItem(
                    rank=1,
                    factor="Insufficient data",
                    score=0.0,
                    evidence=["Upload process Excel or equipment logs for RCA."],
                )
            ]

        # Normalize scores to 0–1
        max_score = max(v["score"] for v in scores.values()) or 1.0
        ranked = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)

        results: list[RootCauseItem] = []
        for rank, (param, data) in enumerate(ranked[:5], 1):
            hints = self.CAUSAL_HINTS.get(param, [])
            evidence = list(data["evidence"][:3])
            if hints:
                evidence.append(f"Known downstream effects: {', '.join(hints)}.")

            results.append(
                RootCauseItem(
                    rank=rank,
                    factor=self._humanize(param),
                    score=round(data["score"] / max_score, 3),
                    evidence=evidence,
                )
            )
        return results

    @staticmethod
    def _humanize(param: str) -> str:
        return param.replace("_", " ").title()
