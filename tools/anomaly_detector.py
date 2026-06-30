"""Statistical anomaly detection for process parameters."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from models.process_rules import ProcessRuleEngine, resolve_parameter


class AnomalyDetector:
    """Detect out-of-spec and statistical anomalies in process data."""

    ZSCORE_THRESHOLD = 2.5

    def __init__(self) -> None:
        self.rule_engine = ProcessRuleEngine()

    def detect(self, df: pd.DataFrame, source: str = "process_data") -> list[dict[str, Any]]:
        """Run rule-based and z-score anomaly detection on numeric columns."""
        anomalies: list[dict[str, Any]] = []
        numeric_cols = df.select_dtypes(include="number").columns.tolist()

        column_stats: dict[str, dict[str, float]] = {}
        for col in numeric_cols:
            series = df[col].dropna()
            if series.empty:
                continue
            column_stats[col] = {
                "min": float(series.min()),
                "max": float(series.max()),
                "mean": float(series.mean()),
            }

        # Rule-based out-of-range detection
        validation = self.rule_engine.validate_readings(column_stats)
        for issue in validation.issues:
            if issue.severity == "error":
                anomalies.append(
                    {
                        "type": "out_of_spec",
                        "parameter": issue.parameter or "unknown",
                        "message": issue.message,
                        "severity": "high",
                        "source": source,
                        "value": issue.value,
                    }
                )

        # Z-score spikes on recent window vs historical baseline
        for col in numeric_cols:
            series = df[col].dropna()
            if len(series) < 10:
                continue

            mean, std = float(series.mean()), float(series.std())
            if std == 0:
                continue

            recent = series.tail(max(5, len(series) // 10))
            for idx, val in recent.items():
                z = abs((val - mean) / std)
                if z >= self.ZSCORE_THRESHOLD:
                    param = resolve_parameter(col) or col
                    anomalies.append(
                        {
                            "type": "statistical_spike",
                            "parameter": param,
                            "column": col,
                            "message": (
                                f"{col}={val:.3f} deviates |z|={z:.2f} from baseline "
                                f"(μ={mean:.3f}, σ={std:.3f})."
                            ),
                            "severity": "high" if z >= 3.5 else "medium",
                            "source": source,
                            "value": float(val),
                            "z_score": round(z, 2),
                            "row_index": int(idx) if isinstance(idx, (int, np.integer)) else str(idx),
                        }
                    )

        # Deduplicate by parameter + type, keep highest severity
        seen: dict[tuple[str, str], dict[str, Any]] = {}
        severity_rank = {"high": 3, "medium": 2, "low": 1}
        for a in anomalies:
            key = (a.get("parameter", ""), a.get("type", ""))
            if key not in seen or severity_rank.get(a["severity"], 0) > severity_rank.get(seen[key]["severity"], 0):
                seen[key] = a

        return sorted(seen.values(), key=lambda x: severity_rank.get(x["severity"], 0), reverse=True)
