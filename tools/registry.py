"""Tool registry — maps tool names to callable analysis functions."""

from __future__ import annotations

from typing import Any, Callable

import pandas as pd

from tools.anomaly_detector import AnomalyDetector
from tools.excel_loader import ExcelLoader
from tools.forecaster import YieldForecaster
from tools.log_loader import LogLoader
from tools.maintenance_advisor import MaintenanceAdvisor
from tools.pdf_rag import PDFRAGStore
from tools.rca_engine import RCAEngine
from tools.yield_analyzer import YieldAnalyzer

# Tool identifiers used by the Planner Agent
TOOL_NAMES = (
    "rag_query",
    "load_excel",
    "load_logs",
    "detect_anomalies",
    "analyze_yield",
    "root_cause_analysis",
    "forecast_yield",
    "recommend_maintenance",
    "general_qa",
)


class ToolRegistry:
    """Central registry holding tool instances and shared data context."""

    def __init__(self) -> None:
        self.pdf_rag = PDFRAGStore()
        self.excel_loader = ExcelLoader()
        self.log_loader = LogLoader()
        self.anomaly_detector = AnomalyDetector()
        self.yield_analyzer = YieldAnalyzer()
        self.rca_engine = RCAEngine()
        self.forecaster = YieldForecaster()
        self.maintenance_advisor = MaintenanceAdvisor()

        # Cached parsed data from uploads
        self.excel_data: list[dict[str, Any]] = []
        self.log_data: list[dict[str, Any]] = []
        self.combined_frames: list[tuple[pd.DataFrame, str]] = []

    def ingest_pdf(self, file_bytes: bytes, filename: str) -> dict[str, Any]:
        return self.pdf_rag.add_pdf(file_bytes, filename)

    def ingest_excel(self, file_bytes: bytes, filename: str) -> dict[str, Any]:
        parsed = self.excel_loader.load(file_bytes, filename)
        self.excel_data.append(parsed)
        for sheet, df in parsed["dataframes"].items():
            self.combined_frames.append((df, f"{filename}/{sheet}"))
        return parsed

    def ingest_log(self, file_bytes: bytes, filename: str) -> dict[str, Any]:
        parsed = self.log_loader.load(file_bytes, filename)
        self.log_data.append(parsed)
        df = parsed["dataframe"]
        if not df.empty:
            self.combined_frames.append((df, filename))
        return parsed

    def clear(self) -> None:
        self.pdf_rag = PDFRAGStore()
        self.excel_data = []
        self.log_data = []
        self.combined_frames = []

    def get_tool_descriptions(self) -> dict[str, str]:
        return {
            "rag_query": "Search uploaded PDF manuals for relevant process documentation.",
            "load_excel": "Parse uploaded Excel process data workbooks.",
            "load_logs": "Parse equipment log files (CSV/TXT).",
            "detect_anomalies": "Detect out-of-spec and statistical process anomalies.",
            "analyze_yield": "Identify yield degradation factors via correlation analysis.",
            "root_cause_analysis": "Rank root causes from anomalies and yield factors.",
            "forecast_yield": "Predict future yield using time-series forecasting.",
            "recommend_maintenance": "Suggest preventive maintenance before failures.",
            "general_qa": "Answer general semiconductor process engineering questions.",
        }

    def run_detect_anomalies(self) -> list[dict[str, Any]]:
        all_anomalies: list[dict[str, Any]] = []
        for df, source in self.combined_frames:
            all_anomalies.extend(self.anomaly_detector.detect(df, source=source))
        return all_anomalies

    def run_analyze_yield(self) -> list[dict[str, Any]]:
        all_factors: list[dict[str, Any]] = []
        for df, source in self.combined_frames:
            all_factors.extend(self.yield_analyzer.analyze(df, source=source))
        # Deduplicate and re-rank
        all_factors.sort(key=lambda x: x.get("impact_score", 0), reverse=True)
        return all_factors[:10]

    def run_forecast(self):
        for df, _ in self.combined_frames:
            result = self.forecaster.forecast(df)
            if result.current_yield is not None:
                return result
        from models.analysis_result import YieldForecast
        return YieldForecast(
            current_yield=None, predicted_yield=None, horizon_steps=5,
            trend="unknown", method="none", details=["No yield data available."],
        )

    def get_log_dataframe(self) -> pd.DataFrame | None:
        if not self.log_data:
            return None
        return self.log_data[-1]["dataframe"]
