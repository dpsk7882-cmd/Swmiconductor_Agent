"""Structured analysis output models for agent conclusions."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

HealthStatus = Literal["healthy", "warning", "critical", "unknown"]


@dataclass
class RootCauseItem:
    """Single ranked root-cause hypothesis with supporting evidence."""

    rank: int
    factor: str
    score: float  # 0.0 – 1.0 relative contribution
    evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class YieldForecast:
    """Future yield prediction from time-series analysis."""

    current_yield: float | None
    predicted_yield: float | None
    horizon_steps: int
    trend: Literal["improving", "stable", "degrading", "unknown"]
    method: str
    details: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MaintenanceRecommendation:
    """Preventive maintenance action suggested before equipment failure."""

    priority: Literal["high", "medium", "low"]
    action: str
    equipment: str
    rationale: str
    estimated_risk_reduction: float  # 0.0 – 1.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AnalysisResult:
    """Complete output from the semiconductor process analysis pipeline."""

    process_health: HealthStatus
    health_summary: str
    anomalies: list[dict[str, Any]] = field(default_factory=list)
    yield_factors: list[dict[str, Any]] = field(default_factory=list)
    root_causes: list[RootCauseItem] = field(default_factory=list)
    yield_forecast: YieldForecast | None = None
    maintenance_actions: list[MaintenanceRecommendation] = field(default_factory=list)
    confidence_score: float = 0.0  # 0 – 100
    confidence_explanation: str = ""
    evidence: list[str] = field(default_factory=list)
    tools_used: list[str] = field(default_factory=list)
    reviewer_notes: str = ""
    validation_passed: bool = True
    validation_issues: list[str] = field(default_factory=list)
    narrative: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        if self.yield_forecast:
            data["yield_forecast"] = self.yield_forecast.to_dict()
        data["root_causes"] = [rc.to_dict() for rc in self.root_causes]
        data["maintenance_actions"] = [m.to_dict() for m in self.maintenance_actions]
        return data
