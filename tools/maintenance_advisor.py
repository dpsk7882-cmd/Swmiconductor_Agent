"""Preventive maintenance recommendation engine."""

from __future__ import annotations

from typing import Any

import pandas as pd

from models.analysis_result import MaintenanceRecommendation


class MaintenanceAdvisor:
    """Recommend PM actions based on anomalies, trends, and log patterns."""

    PM_RULES: list[dict[str, Any]] = [
        {
            "trigger_params": {"chamber_temp_c", "temperature", "temp", "chamber_temp"},
            "equipment": "Process Chamber",
            "action": "Inspect heater zones and recalibrate thermal uniformity map.",
            "priority": "high",
            "rationale": "Temperature anomalies often precede film stress and yield loss.",
        },
        {
            "trigger_params": {"rf_power_w", "rf_power", "power"},
            "equipment": "RF Generator / Matcher",
            "action": "Check RF match network, clean electrode, verify reflected power.",
            "priority": "high",
            "rationale": "RF power drift indicates plasma instability or arcing risk.",
        },
        {
            "trigger_params": {"chamber_pressure_mtorr", "pressure", "chamber_pressure"},
            "equipment": "Vacuum System",
            "action": "Inspect throttle valve, pump performance, and chamber leak rate.",
            "priority": "medium",
            "rationale": "Pressure excursions affect etch/deposition uniformity.",
        },
        {
            "trigger_params": {"gas_flow_sccm", "gas_flow", "flow"},
            "equipment": "Gas Delivery System",
            "action": "Verify MFC calibration and replace filters on affected lines.",
            "priority": "medium",
            "rationale": "Flow instability impacts chemistry and particle generation.",
        },
        {
            "trigger_params": {"defect_density_cm2", "defect_density", "defects", "defect"},
            "equipment": "Cleanroom / Tool Set",
            "action": "Schedule wet clean and particle baseline verification.",
            "priority": "high",
            "rationale": "Rising defect density is a leading indicator of yield collapse.",
        },
        {
            "trigger_params": {"overlay_nm", "overlay"},
            "equipment": "Lithography Track / Scanner",
            "action": "Run overlay matching and reticle alignment verification.",
            "priority": "medium",
            "rationale": "Overlay drift causes systematic CD and yield loss.",
        },
    ]

    LOG_KEYWORDS: list[tuple[str, str, str]] = [
        ("alarm", "Equipment Controller", "Review alarm history and reset recurring fault codes.", "high"),
        ("error", "Equipment Controller", "Investigate error log entries and replace suspect modules.", "high"),
        ("maint", "General", "Upcoming maintenance window detected — verify PM checklist completion.", "medium"),
        ("leak", "Vacuum System", "Perform helium leak check on affected chamber.", "high"),
        ("overheat", "Process Chamber", "Inspect cooling lines and thermal interlocks.", "high"),
    ]

    def recommend(
        self,
        anomalies: list[dict[str, Any]],
        yield_forecast_trend: str = "unknown",
        log_df: pd.DataFrame | None = None,
    ) -> list[MaintenanceRecommendation]:
        """Generate ranked preventive maintenance recommendations."""
        recommendations: list[MaintenanceRecommendation] = []
        triggered: set[str] = set()

        anomaly_params = {
            str(a.get("parameter", "")).lower()
            for a in anomalies
        } | {
            str(a.get("column", "")).lower()
            for a in anomalies
        }

        for rule in self.PM_RULES:
            if anomaly_params & {p.lower() for p in rule["trigger_params"]}:
                key = rule["action"]
                if key in triggered:
                    continue
                triggered.add(key)
                severity_boost = 0.2 if any(a.get("severity") == "high" for a in anomalies) else 0.0
                recommendations.append(
                    MaintenanceRecommendation(
                        priority=rule["priority"],
                        action=rule["action"],
                        equipment=rule["equipment"],
                        rationale=rule["rationale"],
                        estimated_risk_reduction=min(0.5 + severity_boost, 0.85),
                    )
                )

        if yield_forecast_trend == "degrading":
            recommendations.append(
                MaintenanceRecommendation(
                    priority="high",
                    action="Accelerate scheduled PM and run SPC review on top yield drivers.",
                    equipment="Fab Line",
                    rationale="Forecast indicates degrading yield trend — proactive PM recommended.",
                    estimated_risk_reduction=0.6,
                )
            )

        if log_df is not None:
            recommendations.extend(self._from_logs(log_df, triggered))

        if not recommendations:
            recommendations.append(
                MaintenanceRecommendation(
                    priority="low",
                    action="Continue routine PM schedule; no immediate intervention required.",
                    equipment="General",
                    rationale="No critical anomaly patterns detected in current data.",
                    estimated_risk_reduction=0.15,
                )
            )

        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda r: priority_order.get(r.priority, 3))
        return recommendations[:6]

    def _from_logs(
        self, log_df: pd.DataFrame, triggered: set[str]
    ) -> list[MaintenanceRecommendation]:
        results: list[MaintenanceRecommendation] = []
        text_cols = log_df.select_dtypes(include=["object", "string"]).columns.tolist()

        combined = ""
        if "log_line" in log_df.columns:
            combined = " ".join(log_df["log_line"].astype(str).tolist()).lower()
        else:
            for col in text_cols:
                combined += " " + " ".join(log_df[col].astype(str).tolist())
        combined = combined.lower()

        for keyword, equipment, action, priority in self.LOG_KEYWORDS:
            if keyword in combined and action not in triggered:
                triggered.add(action)
                results.append(
                    MaintenanceRecommendation(
                        priority=priority,
                        action=action,
                        equipment=equipment,
                        rationale=f"Equipment log contains '{keyword}' events.",
                        estimated_risk_reduction=0.55 if priority == "high" else 0.35,
                    )
                )
        return results
