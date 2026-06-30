"""Platform-level analysis snapshot for the industrial dashboard."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

RiskLevel = Literal["Low", "Medium", "High"]
ProcessStatus = Literal["Normal", "Watch", "Alert", "Unknown"]
EquipmentStatus = Literal["Stable", "Degraded", "Critical", "Unknown"]


@dataclass
class DriftSignal:
    """A detected process drift or abnormality."""

    category: str
    parameter: str
    severity: str
    message: str
    evidence: str
    drift_pct: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RiskAssessment:
    """Process risk dimensions replacing generic 'health' terminology."""

    process_stability: RiskLevel
    yield_risk: RiskLevel
    equipment_risk: RiskLevel
    risk_level: RiskLevel
    risk_score: float  # 0–100
    summary: str
    factors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PredictionOutput:
    """ML prediction results — model-agnostic container."""

    current_yield: float | None
    predicted_yield: float | None
    failure_probability: float  # 0–1
    equipment_failure_risk: RiskLevel
    yield_trend: Literal["Improving", "Stable", "Degrading", "Unknown"]
    model_name: str
    model_version: str
    horizon_steps: int = 5
    top_variables: list[str] = field(default_factory=list)
    details: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ExplainabilityBundle:
    """Explainable AI output attached to every decision."""

    evidence: list[str] = field(default_factory=list)
    important_variables: list[str] = field(default_factory=list)
    reasoning: list[str] = field(default_factory=list)
    confidence_score: float = 0.0
    confidence_explanation: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AgentVerdict:
    """Dual-agent output: original analysis + reviewed conclusion."""

    original_analysis: str
    reviewed_analysis: str
    approved: bool
    reviewer_notes: str
    needs_more_data: bool = False
    data_requests: list[str] = field(default_factory=list)
    analysis_verified: bool = False
    contradiction_found: bool = False
    evidence_strength: float = 0.0  # 0–100

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PlatformSnapshot:
    """Complete platform state displayed across all dashboard pages."""

    process_status: ProcessStatus
    current_yield: float | None
    predicted_yield: float | None
    risk: RiskAssessment
    prediction: PredictionOutput
    drifts: list[DriftSignal] = field(default_factory=list)
    yield_factors: list[dict[str, Any]] = field(default_factory=list)
    root_causes: list[dict[str, Any]] = field(default_factory=list)
    recommendations: list[dict[str, Any]] = field(default_factory=list)
    equipment_status: EquipmentStatus = "Unknown"
    model_status: str = "Ready"
    explainability: ExplainabilityBundle = field(default_factory=ExplainabilityBundle)
    agent_verdict: AgentVerdict | None = None
    uploaded_files: list[str] = field(default_factory=list)
    analysis_timestamp: str = ""
    tools_executed: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "process_status": self.process_status,
            "current_yield": self.current_yield,
            "predicted_yield": self.predicted_yield,
            "risk": self.risk.to_dict(),
            "prediction": self.prediction.to_dict(),
            "drifts": [d.to_dict() for d in self.drifts],
            "yield_factors": self.yield_factors,
            "root_causes": self.root_causes,
            "recommendations": self.recommendations,
            "equipment_status": self.equipment_status,
            "model_status": self.model_status,
            "explainability": self.explainability.to_dict(),
            "agent_verdict": self.agent_verdict.to_dict() if self.agent_verdict else None,
            "uploaded_files": self.uploaded_files,
            "analysis_timestamp": self.analysis_timestamp,
            "tools_executed": self.tools_executed,
        }
