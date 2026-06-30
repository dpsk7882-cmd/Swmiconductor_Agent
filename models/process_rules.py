"""Rule-based validation engine for semiconductor process knowledge."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# Typical operating ranges for common fab process parameters (demo / reference values).
PROCESS_PARAMETER_RULES: dict[str, dict[str, float]] = {
    "chamber_temp_c": {"min": 180.0, "max": 450.0, "unit": "°C"},
    "chamber_pressure_mtorr": {"min": 1.0, "max": 500.0, "unit": "mTorr"},
    "rf_power_w": {"min": 50.0, "max": 3000.0, "unit": "W"},
    "gas_flow_sccm": {"min": 5.0, "max": 2000.0, "unit": "sccm"},
    "etch_rate_nm_min": {"min": 10.0, "max": 800.0, "unit": "nm/min"},
    "deposition_rate_nm_min": {"min": 1.0, "max": 200.0, "unit": "nm/min"},
    "cd_nm": {"min": 20.0, "max": 500.0, "unit": "nm"},
    "overlay_nm": {"min": 0.0, "max": 15.0, "unit": "nm"},
    "yield_pct": {"min": 70.0, "max": 100.0, "unit": "%"},
    "defect_density_cm2": {"min": 0.0, "max": 5.0, "unit": "/cm²"},
}

# Column name aliases mapped to canonical rule keys.
COLUMN_ALIASES: dict[str, str] = {
    "temperature": "chamber_temp_c",
    "temp": "chamber_temp_c",
    "chamber_temp": "chamber_temp_c",
    "pressure": "chamber_pressure_mtorr",
    "chamber_pressure": "chamber_pressure_mtorr",
    "rf_power": "rf_power_w",
    "power": "rf_power_w",
    "gas_flow": "gas_flow_sccm",
    "flow": "gas_flow_sccm",
    "etch_rate": "etch_rate_nm_min",
    "dep_rate": "deposition_rate_nm_min",
    "deposition_rate": "deposition_rate_nm_min",
    "cd": "cd_nm",
    "critical_dimension": "cd_nm",
    "overlay": "overlay_nm",
    "yield": "yield_pct",
    "yield_percent": "yield_pct",
    "defect_density": "defect_density_cm2",
    "defects": "defect_density_cm2",
}


@dataclass
class ValidationIssue:
    """A single rule violation or warning."""

    severity: str  # "error" | "warning" | "info"
    message: str
    parameter: str = ""
    value: float | None = None


@dataclass
class ValidationReport:
    """Aggregated output from the rule engine."""

    passed: bool
    issues: list[ValidationIssue] = field(default_factory=list)
    matched_parameters: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "issues": [asdict_issue(i) for i in self.issues],
            "matched_parameters": self.matched_parameters,
        }


def asdict_issue(issue: ValidationIssue) -> dict[str, Any]:
    return {"severity": issue.severity, "message": issue.message,
            "parameter": issue.parameter, "value": issue.value}


def resolve_parameter(column_name: str) -> str | None:
    """Map a dataframe column name to a canonical process parameter key."""
    normalized = column_name.strip().lower().replace(" ", "_").replace("-", "_")
    if normalized in PROCESS_PARAMETER_RULES:
        return normalized
    return COLUMN_ALIASES.get(normalized)


class ProcessRuleEngine:
    """Validate process readings and analysis conclusions against fab knowledge."""

    def validate_readings(
        self,
        column_stats: dict[str, dict[str, float]],
    ) -> ValidationReport:
        """
        Check min/max/mean values for known process columns.

        column_stats: {column_name: {"min": ..., "max": ..., "mean": ...}}
        """
        issues: list[ValidationIssue] = []
        matched: list[str] = []

        for col, stats in column_stats.items():
            param = resolve_parameter(col)
            if not param:
                continue
            matched.append(param)
            rules = PROCESS_PARAMETER_RULES[param]
            lo, hi = rules["min"], rules["max"]
            unit = rules.get("unit", "")

            for stat_name in ("min", "max", "mean"):
                val = stats.get(stat_name)
                if val is None:
                    continue
                if val < lo or val > hi:
                    issues.append(
                        ValidationIssue(
                            severity="error",
                            message=(
                                f"{col} {stat_name}={val:.2f}{unit} is outside "
                                f"valid range [{lo}, {hi}]{unit}."
                            ),
                            parameter=param,
                            value=val,
                        )
                    )

        errors = [i for i in issues if i.severity == "error"]
        return ValidationReport(passed=len(errors) == 0, issues=issues, matched_parameters=matched)

    def validate_conclusion(
        self,
        process_health: str,
        confidence: float,
        anomalies: list[dict[str, Any]],
    ) -> ValidationReport:
        """Sanity-check agent conclusions before presenting to the user."""
        issues: list[ValidationIssue] = []

        if process_health == "healthy" and len(anomalies) >= 3:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    message="Health marked healthy but multiple anomalies were detected.",
                )
            )

        if process_health == "critical" and not anomalies:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    message="Critical health status without supporting anomaly evidence.",
                )
            )

        if confidence >= 90 and len(anomalies) == 0 and process_health != "healthy":
            issues.append(
                ValidationIssue(
                    severity="warning",
                    message="High confidence assigned without anomaly evidence.",
                )
            )

        if confidence < 20:
            issues.append(
                ValidationIssue(
                    severity="info",
                    message="Very low confidence — insufficient data for reliable conclusions.",
                )
            )

        errors = [i for i in issues if i.severity == "error"]
        return ValidationReport(passed=len(errors) == 0, issues=issues)
