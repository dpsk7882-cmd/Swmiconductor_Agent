"""Main orchestrator — coordinates planner, tools, and reviewer agents."""

from __future__ import annotations

from typing import Any

from agents.planner import PlannerAgent
from agents.reviewer_agent import ReviewerAgent
from models.analysis_result import AnalysisResult, MaintenanceRecommendation, RootCauseItem
from tools.registry import ToolRegistry
from utils.llm import LLMClient, SEMICONDUCTOR_SYSTEM_PROMPT


class Orchestrator:
    """End-to-end pipeline: plan → execute tools → review → narrative."""

    def __init__(self, registry: ToolRegistry | None = None) -> None:
        self.registry = registry or ToolRegistry()
        self.reviewer = ReviewerAgent()
        self.llm = LLMClient()

    def process_query(
        self,
        user_query: str,
        chat_history: list[dict[str, str]] | None = None,
    ) -> AnalysisResult:
        """Run the full agent pipeline for a user message."""
        has_pdf = not self.registry.pdf_rag.is_empty
        has_data = len(self.registry.combined_frames) > 0

        planner = PlannerAgent(has_pdf=has_pdf, has_data=has_data)
        plan = planner.plan(user_query)
        tools_used = plan.tool_names

        # Execute planned tools
        rag_context = ""
        rag_hits = 0
        anomalies: list[dict[str, Any]] = []
        yield_factors: list[dict[str, Any]] = []
        root_causes: list[RootCauseItem] = []
        yield_forecast = None
        maintenance: list[MaintenanceRecommendation] = []
        evidence: list[str] = [plan.rationale]

        for step in plan.steps:
            if step.tool == "rag_query":
                hits = self.registry.pdf_rag.retrieve(user_query, top_k=4)
                rag_hits = len(hits)
                rag_context = self.registry.pdf_rag.build_context(user_query)
                if hits:
                    evidence.append(f"RAG retrieved {rag_hits} manual excerpt(s).")

            elif step.tool == "detect_anomalies":
                anomalies = self.registry.run_detect_anomalies()
                if anomalies:
                    evidence.append(f"Detected {len(anomalies)} process anomaly signal(s).")

            elif step.tool == "analyze_yield":
                yield_factors = self.registry.run_analyze_yield()
                if yield_factors:
                    evidence.append(f"Identified {len(yield_factors)} yield degradation factor(s).")

            elif step.tool == "root_cause_analysis":
                if not anomalies:
                    anomalies = self.registry.run_detect_anomalies()
                if not yield_factors:
                    yield_factors = self.registry.run_analyze_yield()
                root_causes = self.registry.rca_engine.analyze(anomalies, yield_factors)
                evidence.append(f"RCA ranked {len(root_causes)} root-cause hypothesis(es).")

            elif step.tool == "forecast_yield":
                yield_forecast = self.registry.run_forecast()
                if yield_forecast.predicted_yield is not None:
                    evidence.append(
                        f"Yield forecast: {yield_forecast.current_yield}% → "
                        f"{yield_forecast.predicted_yield}% ({yield_forecast.trend})."
                    )

            elif step.tool == "recommend_maintenance":
                if not anomalies:
                    anomalies = self.registry.run_detect_anomalies()
                trend = yield_forecast.trend if yield_forecast else "unknown"
                log_df = self.registry.get_log_dataframe()
                maintenance = self.registry.maintenance_advisor.recommend(
                    anomalies, yield_forecast_trend=trend, log_df=log_df
                )
                evidence.append(f"Generated {len(maintenance)} PM recommendation(s).")

        # Determine process health
        process_health, health_summary = self._assess_health(anomalies, yield_forecast, yield_factors)

        # Preliminary confidence before review
        pre_confidence = self._preliminary_confidence(has_data, has_pdf, anomalies, yield_factors)

        result = AnalysisResult(
            process_health=process_health,
            health_summary=health_summary,
            anomalies=anomalies,
            yield_factors=yield_factors,
            root_causes=root_causes,
            yield_forecast=yield_forecast,
            maintenance_actions=maintenance,
            confidence_score=pre_confidence,
            evidence=evidence,
            tools_used=tools_used,
        )

        # Reviewer pass
        review = self.reviewer.review(result, tools_used, has_data, has_pdf, rag_hits)
        result.confidence_score = review.adjusted_confidence
        result.confidence_explanation = review.confidence_explanation
        result.reviewer_notes = review.reviewer_notes
        result.validation_passed = review.approved
        result.validation_issues = review.validation_issues

        # Build narrative (LLM-enhanced if available, else template)
        result.narrative = self._build_narrative(
            user_query, result, rag_context, chat_history or []
        )

        return result

    def _assess_health(
        self,
        anomalies: list[dict[str, Any]],
        yield_forecast,
        yield_factors: list[dict[str, Any]],
    ) -> tuple[str, str]:
        high_severity = sum(1 for a in anomalies if a.get("severity") == "high")

        if high_severity >= 3:
            return "critical", (
                f"Critical — {high_severity} high-severity anomalies detected. "
                "Immediate engineering review recommended."
            )
        if high_severity >= 1 or len(anomalies) >= 3:
            return "warning", (
                f"Warning — {len(anomalies)} anomaly signal(s) detected. "
                "Process may be drifting from target."
            )
        if yield_forecast and yield_forecast.trend == "degrading":
            return "warning", "Warning — yield forecast shows degrading trend."
        if yield_factors and any(f.get("yield_delta", 0) < -1 for f in yield_factors if "yield_delta" in f):
            return "warning", "Warning — recent yield decline detected vs baseline."
        if anomalies:
            return "warning", f"Minor deviations detected ({len(anomalies)} signal(s))."
        if yield_factors or (yield_forecast and yield_forecast.current_yield):
            return "healthy", "Process appears within normal operating parameters."
        return "unknown", "Insufficient process data to assess health. Upload Excel or log files."

    def _preliminary_confidence(
        self,
        has_data: bool,
        has_pdf: bool,
        anomalies: list,
        yield_factors: list,
    ) -> float:
        score = 25.0
        if has_data:
            score += 30.0
        if has_pdf:
            score += 10.0
        score += min(len(anomalies) * 4, 16.0)
        score += min(len(yield_factors) * 3, 12.0)
        return min(score, 85.0)

    def _build_narrative(
        self,
        user_query: str,
        result: AnalysisResult,
        rag_context: str,
        history: list[dict[str, str]],
    ) -> str:
        """Generate human-readable response using LLM or structured template."""
        if self.llm.is_available:
            context = self._result_to_context(result, rag_context)
            return self.llm.chat(
                user_message=user_query,
                history=history,
                system_prompt=SEMICONDUCTOR_SYSTEM_PROMPT,
                extra_context=context,
            )
        return self._template_narrative(user_query, result, rag_context)

    def _result_to_context(self, result: AnalysisResult, rag_context: str) -> str:
        lines = [
            f"Process Health: {result.process_health} — {result.health_summary}",
            f"Confidence: {result.confidence_score}%",
            f"Tools Used: {', '.join(result.tools_used)}",
        ]
        if result.anomalies:
            lines.append("\nAnomalies:")
            for a in result.anomalies[:5]:
                lines.append(f"  - [{a.get('severity')}] {a.get('message')}")
        if result.yield_factors:
            lines.append("\nYield Factors:")
            for f in result.yield_factors[:5]:
                lines.append(f"  - {f.get('interpretation', f.get('parameter'))}")
        if result.root_causes:
            lines.append("\nRoot Causes:")
            for rc in result.root_causes:
                lines.append(f"  {rc.rank}. {rc.factor} (score={rc.score})")
        if result.yield_forecast and result.yield_forecast.predicted_yield:
            yf = result.yield_forecast
            lines.append(
                f"\nYield Forecast: {yf.current_yield}% → {yf.predicted_yield}% ({yf.trend})"
            )
        if result.maintenance_actions:
            lines.append("\nPM Recommendations:")
            for m in result.maintenance_actions[:4]:
                lines.append(f"  - [{m.priority}] {m.equipment}: {m.action}")
        if rag_context:
            lines.append(f"\n{rag_context}")
        lines.append(f"\nReviewer: {result.reviewer_notes}")
        lines.append(f"Confidence Explanation: {result.confidence_explanation}")
        return "\n".join(lines)

    def _template_narrative(
        self, user_query: str, result: AnalysisResult, rag_context: str
    ) -> str:
        """Structured markdown response without LLM."""
        sections: list[str] = []

        health_emoji = {"healthy": "🟢", "warning": "🟡", "critical": "🔴", "unknown": "⚪"}
        emoji = health_emoji.get(result.process_health, "⚪")

        sections.append(f"## {emoji} Process Health: **{result.process_health.upper()}**")
        sections.append(result.health_summary)
        sections.append("")

        if result.anomalies:
            sections.append("### ⚠️ Anomaly Detection")
            for a in result.anomalies[:6]:
                sections.append(f"- **[{a.get('severity', '?').upper()}]** {a.get('message')}")
            sections.append("")

        if result.yield_factors:
            sections.append("### 📉 Yield Degradation Factors")
            for f in result.yield_factors[:5]:
                sections.append(f"- {f.get('interpretation', f.get('parameter'))}")
            sections.append("")

        if result.root_causes:
            sections.append("### 🔍 Root Cause Ranking")
            for rc in result.root_causes:
                sections.append(f"**{rc.rank}. {rc.factor}** (relative score: {rc.score:.0%})")
                for ev in rc.evidence[:2]:
                    sections.append(f"   - {ev}")
            sections.append("")

        if result.yield_forecast and result.yield_forecast.predicted_yield is not None:
            yf = result.yield_forecast
            sections.append("### 📈 Yield Forecast")
            sections.append(
                f"- Current: **{yf.current_yield}%** → Predicted: **{yf.predicted_yield}%** "
                f"({yf.trend}, method: {yf.method})"
            )
            sections.append("")

        if result.maintenance_actions:
            sections.append("### 🔧 Preventive Maintenance")
            for m in result.maintenance_actions:
                sections.append(
                    f"- **[{m.priority.upper()}]** {m.equipment}: {m.action}\n"
                    f"  _{m.rationale}_ (risk reduction: {m.estimated_risk_reduction:.0%})"
                )
            sections.append("")

        if rag_context:
            sections.append("### 📄 Manual Reference")
            # Show truncated RAG context
            excerpt = rag_context[:1200] + ("..." if len(rag_context) > 1200 else "")
            sections.append(excerpt)
            sections.append("")

        sections.append("---")
        sections.append(
            f"**Confidence: {result.confidence_score:.0f}%** — {result.confidence_explanation}"
        )
        sections.append(f"_{result.reviewer_notes}_")

        # General QA fallback when no analysis ran
        if result.tools_used == ["general_qa"] and not result.anomalies:
            sections.insert(1, self._general_qa_snippet(user_query))

        return "\n".join(sections)

    @staticmethod
    def _general_qa_snippet(query: str) -> str:
        q = query.lower()
        snippets = {
            "litho": "Lithography controls pattern transfer via photoresist exposure and development. Key metrics: CD uniformity, overlay, and dose latitude.",
            "etch": "Plasma etch removes material selectively using RF power, pressure, and chemistry. Monitor etch rate, selectivity, and profile.",
            "dep": "Deposition (CVD/PVD/ALD) builds film layers. Watch thickness uniformity, stress, and particle counts.",
            "yield": "Yield loss drivers include defects, parametric failures, and process drift. Use SPC and multivariate analysis for root cause isolation.",
        }
        for key, text in snippets.items():
            if key in q:
                return f"**Process Knowledge:** {text}\n"
        return (
            "**Tip:** Upload Excel process data or equipment logs for automated anomaly detection, "
            "RCA, yield forecasting, and PM recommendations. Upload PDF manuals for document Q&A.\n"
        )
