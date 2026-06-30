"""Tab 3 — Yield Prediction: ML forecast, failure probability, key variables."""

from __future__ import annotations

from typing import Any

import plotly.graph_objects as go
import streamlit as st

from utils.components import confidence_bar, empty_state, page_header, render_metric_row, section_title
from utils.session import get_engine
from utils.theme import COLORS

C = COLORS


def render_tab_prediction(snap: dict[str, Any]) -> None:
    page_header("🔮 Yield Prediction", "ML-based yield forecasting, trend analysis, and failure risk assessment")

    pred  = snap.get("prediction", {})
    expl  = snap.get("explainability", {})
    conf  = expl.get("confidence_score", 0)

    cur_yield  = snap.get("current_yield")
    pred_yield = snap.get("predicted_yield")
    fail_prob  = pred.get("failure_probability", 0)
    equip_risk = pred.get("equipment_failure_risk", "—")
    trend      = pred.get("yield_trend", "Unknown")

    # ── KPI row ────────────────────────────────────────────────────────────
    trend_icon  = {"Improving": "↑", "Stable": "→", "Degrading": "↓", "Unknown": "?"}.get(trend, "?")
    trend_color = {"Improving": C["success"], "Stable": C["text_muted"], "Degrading": C["danger"]}.get(trend, C["text_muted"])

    render_metric_row([
        ("📊", "Current Yield",      f"{cur_yield:.1f}%"  if cur_yield  else "—", "Measured",          ""),
        ("🔮", "Predicted Yield",    f"{pred_yield:.1f}%" if pred_yield else "—", f"Horizon: {pred.get('horizon_steps',5)} steps", C["accent"]),
        ("📉", "Failure Probability",f"{fail_prob:.0%}",  "ML estimate",           C["danger"] if fail_prob > 0.5 else C["warning"] if fail_prob > 0.3 else C["success"]),
        ("⚙️", "Equipment Risk",     equip_risk,          f"Trend: {trend_icon} {trend}", trend_color),
    ])

    st.markdown("<br>", unsafe_allow_html=True)

    col_chart, col_info = st.columns([3, 2])

    # ── Forecast line chart ────────────────────────────────────────────────
    with col_chart:
        section_title("📈", "Yield Trend & Forecast")
        engine = get_engine()
        forecast_df = None

        if engine.registry.combined_frames:
            df, _ = engine.registry.combined_frames[0]
            try:
                from models.prediction_model import get_prediction_model
                forecast_df = get_prediction_model().forecast_series(df)
            except Exception:
                pass

        if forecast_df is not None and not forecast_df.empty:
            hist = forecast_df[forecast_df["series"] == "historical"]
            fore = forecast_df[forecast_df["series"] == "forecast"]

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=hist["step"], y=hist["yield"],
                name="Historical",
                line=dict(color=C["accent"], width=2.5),
                mode="lines+markers",
                marker=dict(size=5),
            ))
            fig.add_trace(go.Scatter(
                x=fore["step"], y=fore["yield"],
                name="Forecast",
                line=dict(color=C["danger"], width=2.5, dash="dash"),
                mode="lines+markers",
                marker=dict(size=6, symbol="diamond"),
            ))
            # Shade the forecast region
            if not fore.empty:
                fig.add_vrect(
                    x0=fore["step"].iloc[0],
                    x1=fore["step"].iloc[-1],
                    fillcolor="rgba(220,38,38,0.05)",
                    line_width=0,
                    annotation_text="Forecast",
                    annotation_position="top left",
                )

            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="#FAFBFC",
                font=dict(family="Inter, sans-serif", size=12, color=C["text"]),
                margin=dict(l=0, r=0, t=20, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(title="Step", gridcolor=C["border"], zeroline=False),
                yaxis=dict(title="Yield (%)", gridcolor=C["border"], zeroline=False),
                height=320,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Add a yield column (e.g. `yield_pct`) to enable forecasting.")

    # ── Model info + variables ─────────────────────────────────────────────
    with col_info:
        section_title("🤖", "Model Information")
        st.markdown(
            f"""
            <div style="background:{C['surface']};border:1px solid {C['border']};border-radius:12px;padding:1rem 1.25rem;margin-bottom:1rem;">
                <div style="font-size:0.78rem;color:{C['text_muted']};margin-bottom:0.75rem;">
                    <strong style="color:{C['text']};">{pred.get('model_name','—')}</strong>
                    &nbsp; v{pred.get('model_version','—')}
                </div>
                {''.join(f'<div style="font-size:0.78rem;color:{C["text_muted"]};padding:0.2rem 0;">• {d}</div>' for d in pred.get('details',[]))}
            </div>
            """,
            unsafe_allow_html=True,
        )

        section_title("🎯", "Key Variables")
        vars_ = pred.get("top_variables") or expl.get("important_variables", [])
        if vars_:
            for i, v in enumerate(vars_, 1):
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:0.6rem;padding:0.45rem 0;border-bottom:1px solid {C["surface"]};">'
                    f'<span style="font-size:0.82rem;font-weight:700;color:{C["accent"]};width:1.2rem;">{i}.</span>'
                    f'<span style="font-size:0.875rem;color:{C["text"]};">{v}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.caption("Key variables will appear after data analysis.")

        confidence_bar(conf)

    # ── Failure probability gauge ──────────────────────────────────────────
    section_title("🚨", "Failure Probability Gauge")
    gauge_col, _ = st.columns([1, 2])
    with gauge_col:
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number",
            value=fail_prob * 100,
            number={"suffix": "%", "font": {"size": 28, "color": C["text"]}},
            title={"text": "Failure Probability", "font": {"size": 13, "color": C["text_muted"]}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": C["border"]},
                "bar": {"color": C["danger"] if fail_prob > 0.5 else C["warning"] if fail_prob > 0.25 else C["success"]},
                "bgcolor": C["surface"],
                "bordercolor": C["border"],
                "steps": [
                    {"range": [0, 30],  "color": "#DCFCE7"},
                    {"range": [30, 60], "color": "#FEF3C7"},
                    {"range": [60, 100],"color": "#FEE2E2"},
                ],
                "threshold": {"line": {"color": C["danger"], "width": 3}, "thickness": 0.8, "value": 70},
            },
        ))
        fig_g.update_layout(
            height=240,
            margin=dict(l=10, r=10, t=30, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif"),
        )
        st.plotly_chart(fig_g, use_container_width=True)
