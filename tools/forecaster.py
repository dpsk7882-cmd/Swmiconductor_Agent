"""Time-series yield forecasting."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from models.analysis_result import YieldForecast


class YieldForecaster:
    """Predict future yield using exponential smoothing or linear trend."""

    YIELD_ALIASES = {"yield", "yield_pct", "yield_percent", "yield_%", "bin_yield", "final_yield"}
    HORIZON = 5

    def forecast(self, df: pd.DataFrame) -> YieldForecast:
        """Generate a yield forecast from historical data."""
        yield_col = self._find_yield_column(df)
        if yield_col is None:
            return YieldForecast(
                current_yield=None,
                predicted_yield=None,
                horizon_steps=self.HORIZON,
                trend="unknown",
                method="none",
                details=["No yield column found in uploaded data."],
            )

        series = df[yield_col].dropna().astype(float)
        if len(series) < 8:
            current = float(series.iloc[-1]) if len(series) else None
            return YieldForecast(
                current_yield=current,
                predicted_yield=current,
                horizon_steps=self.HORIZON,
                trend="unknown",
                method="insufficient_data",
                details=[f"Need ≥8 yield readings; found {len(series)}."],
            )

        current = float(series.iloc[-1])
        values = series.values

        # Try Holt-Winters if statsmodels available and enough data
        predicted, method, details = self._holt_linear(values)
        if predicted is None:
            predicted, method, details = self._linear_trend(values)

        trend = self._classify_trend(current, predicted, values)
        return YieldForecast(
            current_yield=round(current, 2),
            predicted_yield=round(predicted, 2) if predicted is not None else None,
            horizon_steps=self.HORIZON,
            trend=trend,
            method=method,
            details=details,
        )

    def _holt_linear(self, values: np.ndarray) -> tuple[float | None, str, list[str]]:
        try:
            from statsmodels.tsa.holtwinters import SimpleExpSmoothing

            model = SimpleExpSmoothing(values, initialization_method="estimated")
            fit = model.fit(optimized=True)
            forecast = fit.forecast(self.HORIZON)
            predicted = float(forecast[-1])
            return predicted, "exponential_smoothing", [
                f"Smoothing level α estimated from {len(values)} historical points.",
                f"Forecast horizon: {self.HORIZON} steps.",
            ]
        except Exception as exc:
            return None, "", [f"Exponential smoothing unavailable: {exc}"]

    def _linear_trend(self, values: np.ndarray) -> tuple[float | None, str, list[str]]:
        x = np.arange(len(values))
        coeffs = np.polyfit(x, values, 1)
        slope, intercept = coeffs[0], coeffs[1]
        future_x = len(values) + self.HORIZON - 1
        predicted = float(intercept + slope * future_x)
        return predicted, "linear_regression", [
            f"Linear trend slope: {slope:.4f} yield-units/step.",
            f"Projected {self.HORIZON} steps ahead.",
        ]

    def _classify_trend(
        self, current: float, predicted: float | None, values: np.ndarray
    ) -> str:
        if predicted is None:
            return "unknown"
        delta = predicted - current
        if abs(delta) < 0.3:
            return "stable"
        return "degrading" if delta < 0 else "improving"

    def _find_yield_column(self, df: pd.DataFrame) -> str | None:
        for col in df.columns:
            norm = str(col).lower().replace(" ", "_").replace("-", "_")
            if norm in self.YIELD_ALIASES or "yield" in norm:
                return col
        return None

    def forecast_series(self, df: pd.DataFrame) -> pd.DataFrame | None:
        """Return historical + projected yield for charting."""
        yield_col = self._find_yield_column(df)
        if yield_col is None:
            return None

        series = df[yield_col].dropna().astype(float)
        if len(series) < 5:
            return None

        values = series.values
        _, method, _ = self._holt_linear(values)
        if method == "":
            _, _, _ = self._linear_trend(values)
            x = np.arange(len(values))
            slope, intercept = np.polyfit(x, values, 1)
            future = [intercept + slope * (len(values) + i) for i in range(self.HORIZON)]
        else:
            from statsmodels.tsa.holtwinters import SimpleExpSmoothing
            model = SimpleExpSmoothing(values, initialization_method="estimated")
            fit = model.fit(optimized=True)
            future = fit.forecast(self.HORIZON).tolist()

        hist_idx = list(range(len(values)))
        proj_idx = list(range(len(values), len(values) + self.HORIZON))
        return pd.DataFrame(
            {
                "step": hist_idx + proj_idx,
                "yield": list(values) + future,
                "series": ["historical"] * len(values) + ["forecast"] * self.HORIZON,
            }
        )
