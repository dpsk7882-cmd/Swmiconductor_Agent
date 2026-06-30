"""Yield degradation factor analysis."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


class YieldAnalyzer:
    """Identify parameters correlated with yield loss."""

    YIELD_ALIASES = {"yield", "yield_pct", "yield_percent", "yield_%", "bin_yield", "final_yield"}

    def analyze(self, df: pd.DataFrame, source: str = "process_data") -> list[dict[str, Any]]:
        """Rank process variables by correlation with yield column."""
        yield_col = self._find_yield_column(df)
        if yield_col is None:
            return self._fallback_defect_analysis(df, source)

        numeric = [c for c in df.select_dtypes(include="number").columns if c != yield_col]
        if not numeric:
            return []

        factors: list[dict[str, Any]] = []
        y = df[yield_col].dropna()
        if len(y) < 5:
            return []

        recent_yield = float(y.tail(max(5, len(y) // 10)).mean())
        baseline_yield = float(y.head(max(len(y) // 2, 5)).mean())
        yield_delta = recent_yield - baseline_yield

        for col in numeric:
            aligned = df[[yield_col, col]].dropna()
            if len(aligned) < 5:
                continue
            corr = aligned[yield_col].corr(aligned[col])
            if np.isnan(corr):
                continue

            impact = abs(corr)
            if impact < 0.15:
                continue

            direction = "negative" if corr < 0 else "positive"
            factors.append(
                {
                    "parameter": col,
                    "correlation_with_yield": round(float(corr), 3),
                    "impact_score": round(impact, 3),
                    "direction": direction,
                    "interpretation": self._interpret(col, corr, direction),
                    "source": source,
                    "recent_yield": round(recent_yield, 2),
                    "baseline_yield": round(baseline_yield, 2),
                    "yield_delta": round(yield_delta, 2),
                }
            )

        factors.sort(key=lambda x: x["impact_score"], reverse=True)
        return factors[:8]

    def _find_yield_column(self, df: pd.DataFrame) -> str | None:
        for col in df.columns:
            norm = str(col).lower().replace(" ", "_").replace("-", "_")
            if norm in self.YIELD_ALIASES or "yield" in norm:
                return col
        return None

    def _fallback_defect_analysis(self, df: pd.DataFrame, source: str) -> list[dict[str, Any]]:
        """When no yield column exists, use defect-related columns."""
        defect_cols = [
            c for c in df.columns
            if any(k in str(c).lower() for k in ("defect", "reject", "scrap", "fail"))
        ]
        factors: list[dict[str, Any]] = []
        for col in defect_cols:
            series = df[col].dropna()
            if series.empty:
                continue
            recent = float(series.tail(max(5, len(series) // 10)).mean())
            baseline = float(series.head(max(len(series) // 2, 5)).mean())
            if baseline == 0:
                continue
            change_pct = ((recent - baseline) / abs(baseline)) * 100
            if abs(change_pct) < 5:
                continue
            factors.append(
                {
                    "parameter": col,
                    "impact_score": min(abs(change_pct) / 100, 1.0),
                    "direction": "negative" if change_pct > 0 else "positive",
                    "interpretation": (
                        f"{col} changed {change_pct:+.1f}% vs baseline — "
                        f"likely yield degradation driver."
                    ),
                    "source": source,
                    "change_pct": round(change_pct, 1),
                }
            )
        factors.sort(key=lambda x: x["impact_score"], reverse=True)
        return factors

    @staticmethod
    def _interpret(col: str, corr: float, direction: str) -> str:
        if direction == "negative":
            return f"Higher {col} correlates with lower yield (r={corr:.2f})."
        return f"Higher {col} correlates with higher yield (r={corr:.2f}) — check for over-optimization."
