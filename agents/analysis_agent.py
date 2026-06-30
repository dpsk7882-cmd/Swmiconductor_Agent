"""Analysis Agent — primary agent responsible for data analysis and conclusions."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pandas as pd

from models.platform_snapshot import (
    AgentVerdict,
    DriftSignal,
    EquipmentStatus,
    ExplainabilityBundle,
    PlatformSnapshot,
    ProcessStatus,
)
from models.prediction_model import get_prediction_model
from models.risk_model import RiskScoringModel
from models.root_cause_model import RootCauseModel
from tools.drift_detector import ProcessDriftDetector
from tools.maintenance_advisor import MaintenanceAdvisor
from tools.registry import ToolRegistry
from tools.yield_analyzer import YieldAnalyzer


class AnalysisAgent:
    """
    Agent 1 — analyzes process data, generates conclusions and evidence.
    Does NOT finalize confidence; that is the Reviewer Agent's role.
    """

    def __init__(self, registry: ToolRegistry | None = None) -> None:
        self.registry = registry or ToolRegistry()
        self.drift_detector = ProcessDriftDetector()
        self.yield_analyzer = YieldAnalyzer()
        self.risk_model = RiskScoringModel()
        self.rca_model = RootCauseModel()
        self.prediction_model = get_prediction_model()
        self.maintenance = MaintenanceAdvisor()

    def analyze(self, uploaded_files: list[str] | None = None) -> PlatformSnapshot:
        """Execute full process analysis pipeline and return platform snapshot."""
        drifts: list[DriftSignal] = []
        yield_factors: list[dict[str, Any]] = []
        log_alarms = 0
        primary_df: pd.DataFrame | None = None

        for df, source in self.registry.combined_frames:
            drifts.extend(self.drift_detector.detect(df, source=source))
            yield_factors.extend(self.yield_analyzer.analyze(df, source=source))
            if primary_df is None:
                primary_df = df

        log_df = self.registry.get_log_dataframe()
        if log_df is not None:
            log_alarms = self._count_log_alarms(log_df)

        yield_factors.sort(key=lambda x: x.get("impact_score", 0), reverse=True)
        yield_factors = yield_factors[:10]

        prediction = self.prediction_model.predict(primary_df) if primary_df is not None else (
            self.prediction_model.predict(pd.DataFrame())
        )

        risk = self.risk_model.assess(
            drifts=drifts,
            current_yield=prediction.current_yield,
            predicted_yield=prediction.predicted_yield,
            failure_probability=prediction.failure_probability,
            log_alarm_count=log_alarms,
        )

        root_causes = self.rca_model.rank(drifts, yield_factors)
        recommendations = self._build_recommendations(drifts, prediction.yield_trend, log_df)

        process_status = self._process_status(risk.risk_level, drifts)
        equipment_status = self._equipment_status(risk.equipment_risk, log_alarms)

        evidence = self._collect_evidence(drifts, yield_factors, prediction, log_alarms)
        reasoning = self._build_reasoning(drifts, root_causes, prediction, risk)

        original = self._format_analysis(process_status, risk, prediction, drifts, root_causes)

        return PlatformSnapshot(
            process_status=process_status,
            current_yield=prediction.current_yield,
            predicted_yield=prediction.predicted_yield,
            risk=risk,
            prediction=prediction,
            drifts=drifts,
            yield_factors=yield_factors,
            root_causes=root_causes,
            recommendations=recommendations,
            equipment_status=equipment_status,
            model_status=f"{prediction.model_name} v{prediction.model_version} — Active",
            explainability=ExplainabilityBundle(
                evidence=evidence,
                important_variables=prediction.top_variables,
                reasoning=reasoning,
                confidence_score=0.0,  # Set by Reviewer
            ),
            uploaded_files=uploaded_files or [],
            analysis_timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            tools_executed=["drift_detector", "yield_analyzer", "prediction_model", "risk_model", "rca_model"],
            agent_verdict=AgentVerdict(
                original_analysis=original,
                reviewed_analysis="",  # Filled by Reviewer
                approved=False,
                reviewer_notes="",
            ),
        )

    def _build_recommendations(
        self, drifts: list[DriftSignal], trend: str, log_df: pd.DataFrame | None
    ) -> list[dict[str, Any]]:
        anomalies = [{"parameter": d.parameter, "severity": d.severity, "message": d.message} for d in drifts]
        actions = self.maintenance.recommend(anomalies, yield_forecast_trend=trend.lower(), log_df=log_df)

        # Map to fab-standard action names
        action_map = {
            "temperature": ("Chamber Cleaning", "Process Chamber", 1),
            "rf_power": ("ESC Inspection", "Electrostatic Chuck", 1),
            "gas_flow": ("MFC Calibration", "Gas Delivery System", 2),
            "pressure": ("Verify Recipe", "Vacuum / Recipe", 2),
            "defect": ("Chamber Cleaning", "Process Chamber", 1),
            "particle": ("Chamber Cleaning", "Process Chamber", 1),
            "arc": ("Preventive Maintenance", "RF System", 1),
        }

        recs: list[dict[str, Any]] = []
        for i, action in enumerate(actions):
            matched_name = action.action
            for key, (name, equip, pri) in action_map.items():
                if key in action.action.lower() or key in action.rationale.lower():
                    matched_name = name
                    break
            recs.append({
                "priority": action.priority,
                "action": matched_name,
                "detail": action.action,
                "equipment": action.equipment,
                "rationale": action.rationale,
                "risk_reduction": action.estimated_risk_reduction,
                "rank": i + 1,
            })
        return recs

    @staticmethod
    def _count_log_alarms(log_df: pd.DataFrame) -> int:
        text = ""
        if "log_line" in log_df.columns:
            text = " ".join(log_df["log_line"].astype(str).tolist()).upper()
        else:
            for col in log_df.select_dtypes(include=["object", "string"]).columns:
                text += " " + " ".join(log_df[col].astype(str).tolist())
        return text.upper().count("ALARM") + text.upper().count("ERROR")

    @staticmethod
    def _process_status(risk_level: str, drifts: list[DriftSignal]) -> ProcessStatus:
        if risk_level == "High" or any(d.severity == "critical" for d in drifts):
            return "Alert"
        if risk_level == "Medium" or drifts:
            return "Watch"
        if risk_level == "Low":
            return "Normal"
        return "Unknown"

    @staticmethod
    def _equipment_status(equip_risk: str, alarms: int) -> EquipmentStatus:
        if equip_risk == "High" or alarms >= 3:
            return "Critical"
        if equip_risk == "Medium" or alarms >= 1:
            return "Degraded"
        if equip_risk == "Low":
            return "Stable"
        return "Unknown"

    @staticmethod
    def _collect_evidence(
        drifts: list[DriftSignal],
        yield_factors: list[dict],
        prediction: Any,
        alarms: int,
    ) -> list[str]:
        ev: list[str] = []
        for d in drifts[:5]:
            ev.append(f"[{d.category}] {d.message}")
        for f in yield_factors[:3]:
            ev.append(f.get("interpretation", str(f)))
        if prediction.current_yield is not None:
            ev.append(f"Current yield: {prediction.current_yield}%; predicted: {prediction.predicted_yield}%.")
        if alarms:
            ev.append(f"Equipment log: {alarms} alarm/error event(s) detected.")
        return ev

    @staticmethod
    def _build_reasoning(drifts, root_causes, prediction, risk) -> list[str]:
        lines = [risk.summary]
        if root_causes:
            lines.append(f"Top root cause: {root_causes[0].get('factor')} — {root_causes[0].get('explanation', '')}")
        lines.append(f"Yield trend classified as {prediction.yield_trend}.")
        lines.append(f"Failure probability estimated at {prediction.failure_probability:.0%}.")
        return lines

    @staticmethod
    def _format_analysis(status, risk, prediction, drifts, root_causes) -> str:
        parts = [
            f"Process Status: {status}",
            f"Risk Level: {risk.risk_level} (score {risk.risk_score})",
            f"Stability={risk.process_stability}, Yield Risk={risk.yield_risk}, Equipment Risk={risk.equipment_risk}",
            f"Yield: {prediction.current_yield}% → {prediction.predicted_yield}% ({prediction.yield_trend})",
            f"Drift signals: {len(drifts)}",
        ]
        if root_causes:
            parts.append(f"Primary root cause: {root_causes[0].get('factor')}")
        return " | ".join(parts)
