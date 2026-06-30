"""Semiconductor-specific process drift and abnormality detection."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from models.platform_snapshot import DriftSignal


class ProcessDriftDetector:
    """
    Detect fab-relevant drift patterns:
    Pressure, Temperature, RF Power, Gas Flow, Particles,
    ARC count, High-Z events, Equipment instability.
    """

    DRIFT_RULES: list[dict[str, Any]] = [
        {
            "category": "Temperature Drift",
            "aliases": ["chamber_temp_c", "temperature", "temp", "chamber_temp", "heater_temp"],
            "threshold_pct": 3.0,
        },
        {
            "category": "Pressure Drift",
            "aliases": ["chamber_pressure_mtorr", "pressure", "chamber_pressure", "vacuum_pressure"],
            "threshold_pct": 5.0,
        },
        {
            "category": "RF Power Drift",
            "aliases": ["rf_power_w", "rf_power", "power", "forward_power", "reflected_power"],
            "threshold_pct": 4.0,
        },
        {
            "category": "Gas Flow Abnormality",
            "aliases": ["gas_flow_sccm", "gas_flow", "flow", "mfc_flow", "cf4_flow", "o2_flow"],
            "threshold_pct": 6.0,
        },
        {
            "category": "Particle Increase",
            "aliases": ["particle_count", "particles", "defect_density_cm2", "defect_density", "defects"],
            "threshold_pct": 8.0,
            "direction": "increase",
        },
        {
            "category": "ARC Count Increase",
            "aliases": ["arc_count", "arcs", "arc_events", "arc_rate"],
            "threshold_pct": 10.0,
            "direction": "increase",
        },
        {
            "category": "High-Z Events",
            "aliases": ["high_z", "highz", "high_z_events", "metal_contamination"],
            "threshold_pct": 5.0,
            "direction": "increase",
        },
    ]

    def detect(self, df: pd.DataFrame, source: str = "process") -> list[DriftSignal]:
        """Run all drift detectors on numeric process columns."""
        signals: list[DriftSignal] = []
        col_map = {self._norm(c): c for c in df.columns}

        for rule in self.DRIFT_RULES:
            col = self._match_column(rule["aliases"], col_map)
            if col is None:
                continue
            signal = self._detect_drift(df, col, rule, source)
            if signal:
                signals.append(signal)

        signals.extend(self._equipment_instability(df, source))
        signals.sort(key=lambda s: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(s.severity, 4))
        return signals

    def _detect_drift(
        self, df: pd.DataFrame, col: str, rule: dict[str, Any], source: str
    ) -> DriftSignal | None:
        series = df[col].dropna()
        if len(series) < 12:
            return None

        split = max(len(series) // 2, 6)
        baseline = series.iloc[:split]
        recent = series.iloc[-max(8, len(series) // 5):]

        base_mean = float(baseline.mean())
        recent_mean = float(recent.mean())
        if base_mean == 0:
            return None

        drift_pct = ((recent_mean - base_mean) / abs(base_mean)) * 100
        direction = rule.get("direction", "any")
        threshold = rule["threshold_pct"]

        triggered = False
        if direction == "increase" and drift_pct >= threshold:
            triggered = True
        elif direction == "any" and abs(drift_pct) >= threshold:
            triggered = True

        if not triggered:
            # Z-score spike on recent window
            std = float(series.std()) or 1.0
            z = abs((recent_mean - base_mean) / std)
            if z < 2.0:
                return None
            drift_pct = z * 3  # normalize for display

        severity = "high" if abs(drift_pct) >= threshold * 2 else "medium"
        if abs(drift_pct) >= threshold * 3:
            severity = "critical"

        return DriftSignal(
            category=rule["category"],
            parameter=col,
            severity=severity,
            message=(
                f"{rule['category']}: {col} shifted {drift_pct:+.1f}% "
                f"(baseline μ={base_mean:.2f} → recent μ={recent_mean:.2f})."
            ),
            evidence=f"Source={source}; baseline n={len(baseline)}, recent n={len(recent)}.",
            drift_pct=round(drift_pct, 2),
        )

    def _equipment_instability(self, df: pd.DataFrame, source: str) -> list[DriftSignal]:
        """Flag high coefficient-of-variation across key parameters."""
        signals: list[DriftSignal] = []
        numeric = df.select_dtypes(include="number").columns.tolist()
        unstable: list[str] = []

        for col in numeric[:8]:
            s = df[col].dropna()
            if len(s) < 15:
                continue
            cv = float(s.std()) / (abs(float(s.mean())) + 1e-9)
            if cv > 0.12:
                unstable.append(f"{col}(CV={cv:.2f})")

        if len(unstable) >= 2:
            signals.append(
                DriftSignal(
                    category="Equipment Instability",
                    parameter="multi-parameter",
                    severity="high" if len(unstable) >= 4 else "medium",
                    message=f"Equipment instability: elevated variability in {', '.join(unstable[:4])}.",
                    evidence=f"Source={source}; {len(unstable)} parameters exceed CV threshold.",
                )
            )
        return signals

    @staticmethod
    def _norm(name: str) -> str:
        return str(name).lower().replace(" ", "_").replace("-", "_")

    def _match_column(self, aliases: list[str], col_map: dict[str, str]) -> str | None:
        for alias in aliases:
            if alias in col_map:
                return col_map[alias]
        for alias in aliases:
            for norm, orig in col_map.items():
                if alias in norm or norm in alias:
                    return orig
        return None
