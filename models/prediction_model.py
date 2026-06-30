"""Pluggable yield and failure prediction models."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import numpy as np
import pandas as pd

from models.platform_snapshot import PredictionOutput, RiskLevel


class BasePredictionModel(ABC):
    """Abstract interface — swap implementations without changing agents/UI."""

    name: str = "base"
    version: str = "1.0"

    @abstractmethod
    def predict(self, df: pd.DataFrame) -> PredictionOutput:
        """Run yield and failure-risk prediction on process data."""


class EnsembleYieldModel(BasePredictionModel):
    """
    Default production model combining exponential smoothing for yield
    and gradient-boosting feature importance for explainability.
    """

    name = "EnsembleYieldModel"
    version = "2.1.0"
    HORIZON = 5
    YIELD_ALIASES = {"yield", "yield_pct", "yield_percent", "bin_yield", "final_yield"}

    def predict(self, df: pd.DataFrame) -> PredictionOutput:
        yield_col = self._find_yield_column(df)
        numeric = df.select_dtypes(include="number").columns.tolist()

        if yield_col is None:
            return PredictionOutput(
                current_yield=None,
                predicted_yield=None,
                failure_probability=0.0,
                equipment_failure_risk="Unknown",
                yield_trend="Unknown",
                model_name=self.name,
                model_version=self.version,
                details=["No yield column detected in dataset."],
            )

        series = df[yield_col].dropna().astype(float)
        current = float(series.iloc[-1]) if len(series) else None
        predicted, trend, details = self._forecast_yield(series.values)
        top_vars = self._feature_importance(df, yield_col, numeric)
        fail_prob = self._failure_probability(series.values, predicted, df, numeric)
        equip_risk = self._equipment_risk_level(fail_prob, df)

        return PredictionOutput(
            current_yield=round(current, 2) if current else None,
            predicted_yield=round(predicted, 2) if predicted is not None else None,
            failure_probability=round(fail_prob, 3),
            equipment_failure_risk=equip_risk,
            yield_trend=trend,
            model_name=self.name,
            model_version=self.version,
            horizon_steps=self.HORIZON,
            top_variables=top_vars,
            details=details,
        )

    def _forecast_yield(self, values: np.ndarray) -> tuple[float | None, str, list[str]]:
        if len(values) < 8:
            return (float(values[-1]) if len(values) else None, "Unknown", ["Insufficient history (<8 points)."])

        try:
            from statsmodels.tsa.holtwinters import SimpleExpSmoothing

            model = SimpleExpSmoothing(values, initialization_method="estimated")
            fit = model.fit(optimized=True)
            predicted = float(fit.forecast(self.HORIZON)[-1])
            details = [f"Exponential smoothing on {len(values)} yield readings."]
        except Exception:
            x = np.arange(len(values))
            slope, intercept = np.polyfit(x, values, 1)
            predicted = float(intercept + slope * (len(values) + self.HORIZON - 1))
            details = [f"Linear fallback; slope={slope:.4f}/step."]

        current = float(values[-1])
        delta = predicted - current
        if abs(delta) < 0.3:
            trend = "Stable"
        elif delta < 0:
            trend = "Degrading"
        else:
            trend = "Improving"
        return predicted, trend, details

    def _feature_importance(
        self, df: pd.DataFrame, yield_col: str, numeric: list[str]
    ) -> list[str]:
        features = [c for c in numeric if c != yield_col]
        if len(features) < 2 or len(df) < 15:
            # Correlation fallback
            corrs = []
            for col in features:
                aligned = df[[yield_col, col]].dropna()
                if len(aligned) < 5:
                    continue
                r = abs(aligned[yield_col].corr(aligned[col]))
                if not np.isnan(r):
                    corrs.append((col, r))
            corrs.sort(key=lambda x: x[1], reverse=True)
            return [c for c, _ in corrs[:5]]

        try:
            from sklearn.ensemble import GradientBoostingRegressor

            X = df[features].dropna()
            y = df.loc[X.index, yield_col]
            if len(X) < 15:
                return features[:5]
            model = GradientBoostingRegressor(n_estimators=50, max_depth=3, random_state=42)
            model.fit(X, y)
            importances = sorted(zip(features, model.feature_importances_), key=lambda x: -x[1])
            return [f"{name} ({imp:.2f})" for name, imp in importances[:5]]
        except Exception:
            return features[:5]

    def _failure_probability(
        self, yield_vals: np.ndarray, predicted: float | None, df: pd.DataFrame, numeric: list[str]
    ) -> float:
        prob = 0.15
        if predicted is not None and len(yield_vals) >= 5:
            drop = yield_vals[-1] - predicted
            if drop > 2:
                prob += 0.35
            elif drop > 0.5:
                prob += 0.15

        # Parameter instability contribution
        instability = 0.0
        for col in numeric[:6]:
            s = df[col].dropna()
            if len(s) < 10:
                continue
            recent_std = float(s.tail(10).std())
            base_std = float(s.head(max(len(s) // 2, 5)).std()) or 1.0
            if recent_std / base_std > 1.5:
                instability += 0.08
        return min(prob + instability, 0.95)

    def _equipment_risk_level(self, fail_prob: float, df: pd.DataFrame) -> RiskLevel:
        if fail_prob >= 0.6:
            return "High"
        if fail_prob >= 0.35:
            return "Medium"
        return "Low"

    def _find_yield_column(self, df: pd.DataFrame) -> str | None:
        for col in df.columns:
            norm = str(col).lower().replace(" ", "_").replace("-", "_")
            if norm in self.YIELD_ALIASES or "yield" in norm:
                return col
        return None

    def forecast_series(self, df: pd.DataFrame) -> pd.DataFrame | None:
        """Historical + projected yield for charts."""
        yield_col = self._find_yield_column(df)
        if yield_col is None:
            return None
        series = df[yield_col].dropna().astype(float)
        if len(series) < 5:
            return None
        values = series.values
        predicted, _, _ = self._forecast_yield(values)
        if predicted is None:
            return None
        # Linear projection for chart
        x = np.arange(len(values))
        slope, intercept = np.polyfit(x, values, 1)
        future = [intercept + slope * (len(values) + i) for i in range(self.HORIZON)]
        return pd.DataFrame({
            "step": list(range(len(values))) + list(range(len(values), len(values) + self.HORIZON)),
            "yield": list(values) + future,
            "series": ["historical"] * len(values) + ["forecast"] * self.HORIZON,
        })


# Registry for easy model swapping
PREDICTION_MODELS: dict[str, type[BasePredictionModel]] = {
    "ensemble": EnsembleYieldModel,
}


def get_prediction_model(name: str = "ensemble") -> BasePredictionModel:
    cls = PREDICTION_MODELS.get(name, EnsembleYieldModel)
    return cls()
