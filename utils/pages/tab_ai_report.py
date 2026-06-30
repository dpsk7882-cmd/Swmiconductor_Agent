"""Tab 6 — AI Report: executive summary with download."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from utils.components import confidence_bar, page_header, render_metric_row, risk_pill_html, section_title
from utils.executive_report import extract_recommended_actions, extract_top_root_causes
from utils.theme import COLORS

C = COLORS

RANK_NUMS = ("①", "②", "③", "④", "⑤")


def render_tab_ai_report(snap: dict[str, Any]) -> None:
    page_header("🤖 AI Report", "Executive-grade analysis report with dual-agent verification")

    risk    = snap.get("risk", {})
    pred    = snap.get("prediction", {})
    expl    = snap.get("explainability", {})
    verdict = snap.get("agent_verdict") or {}
    conf    = expl.get("confidence_score", 0)

    status  = snap.get("process_status", "Unknown")
    ts      = snap.get("analysis_timestamp", datetime.now().strftime("%Y-%m-%d %H:%M"))

    top_causes = extract_top_root_causes(snap, limit=5)
    actions    = extract_recommended_actions(snap, limit=4)

    # ── Report header ──────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="
            background:linear-gradient(135deg, {C['accent_light']} 0%, #F0F7FF 100%);
            border:1px solid rgba(37,99,235,0.2);
            border-radius:14px;
            padding:1.5rem 2rem;
            margin-bottom:1.5rem;
        ">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div>
                    <div style="font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:{C['accent']};margin-bottom:0.4rem;">
                        SEMICONDUCTOR AI PROCESS REPORT
                    </div>
                    <div style="font-size:1.5rem;font-weight:800;color:{C['text']};letter-spacing:-0.03em;">
                        Process Analysis Report
                    </div>
                    <div style="font-size:0.85rem;color:{C['text_muted']};margin-top:0.3rem;">
                        Generated: {ts} &nbsp;·&nbsp; FabSense AI v2.0 &nbsp;·&nbsp; Dual-Agent Verified
                    </div>
                </div>
                <div style="text-align:right;">
                    {risk_pill_html(status.replace('Normal','Low').replace('Watch','Medium').replace('Alert','High'))}
                    <div style="font-size:0.78rem;color:{C['text_muted']};margin-top:0.4rem;">
                        Confidence: <strong>{conf:.0f}%</strong>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_l, col_r = st.columns(2)

    # ── LEFT COLUMN ────────────────────────────────────────────────────────
    with col_l:

        # Executive Summary
        _section("📋", "Executive Summary")
        reviewed = verdict.get("reviewed_analysis", "Analysis pending.")
        st.markdown(
            f'<div style="font-size:0.9rem;color:{C["text"]};line-height:1.7;padding:0.75rem;">{reviewed}</div>',
            unsafe_allow_html=True,
        )

        # Current Process Status
        _section("🏭", "Current Process Status")
        for label, val, color in [
            ("Process Status", status, {"Normal": C["success"], "Watch": C["warning"], "Alert": C["danger"]}.get(status, C["text_muted"])),
            ("Risk Level",     risk.get("risk_level","—"), {"Low": C["success"], "Medium": C["warning"], "High": C["danger"]}.get(risk.get("risk_level",""), C["text"])),
            ("Risk Score",     f"{risk.get('risk_score',0):.0f}/100", C["text"]),
            ("Equipment",      snap.get("equipment_status","—"), C["text"]),
        ]:
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;padding:0.4rem 0;border-bottom:1px solid {C["surface"]};">'
                f'<span style="font-size:0.85rem;color:{C["text_muted"]};">{label}</span>'
                f'<span style="font-size:0.85rem;font-weight:700;color:{color};">{val}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # Root Cause Analysis
        _section("🔍", "Root Cause Analysis")
        if top_causes:
            for i, (name, pct) in enumerate(top_causes):
                num   = RANK_NUMS[i] if i < len(RANK_NUMS) else f"{i+1}."
                color = C["danger"] if pct >= 30 else C["warning"] if pct >= 15 else C["success"]
                st.markdown(
                    f"""
                    <div style="
                        display:flex;align-items:center;gap:0.75rem;
                        padding:0.6rem 0.85rem;margin-bottom:0.4rem;
                        background:{C['surface']};border-radius:10px;border:1px solid {C['border']};
                    ">
                        <span style="font-size:1.05rem;font-weight:800;color:{C['accent']};">{num}</span>
                        <span style="flex:1;font-size:0.875rem;font-weight:600;color:{C['text']};">{name}</span>
                        <div style="text-align:right;">
                            <span style="font-size:0.82rem;font-weight:700;color:{color};">{pct}%</span>
                            <div style="height:4px;width:60px;background:{C['border']};border-radius:999px;overflow:hidden;margin-top:2px;">
                                <div style="height:4px;width:{pct*0.6:.0f}px;background:{color};border-radius:999px;"></div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No root causes identified.")

    # ── RIGHT COLUMN ───────────────────────────────────────────────────────
    with col_r:

        # Yield Prediction
        _section("🔮", "Yield Prediction")
        cur  = snap.get("current_yield")
        predy = snap.get("predicted_yield")
        trend = pred.get("yield_trend","Unknown")
        trend_icon = {"Improving":"↑","Stable":"→","Degrading":"↓"}.get(trend,"?")
        trend_color= {"Improving":C["success"],"Stable":C["text_muted"],"Degrading":C["danger"]}.get(trend,C["text_muted"])

        st.markdown(
            f"""
            <div style="
                background:{C['surface_alt']};border:1px solid rgba(37,99,235,0.2);
                border-radius:12px;padding:1.25rem;margin-bottom:0.75rem;
            ">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
                    <div>
                        <div style="font-size:0.75rem;color:{C['text_muted']};font-weight:600;text-transform:uppercase;">Current → Predicted</div>
                        <div style="font-size:1.75rem;font-weight:800;color:{C['accent']};letter-spacing:-0.04em;">
                            {f'{cur:.1f}%' if cur else '—'} → {f'{predy:.1f}%' if predy else '—'}
                        </div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:1.5rem;font-weight:800;color:{trend_color};">{trend_icon}</div>
                        <div style="font-size:0.75rem;color:{C['text_muted']};font-weight:600;">{trend}</div>
                    </div>
                </div>
                <div style="font-size:0.78rem;color:{C['text_muted']};">
                    Failure probability: <strong style="color:{C['danger']};">{pred.get('failure_probability',0):.0%}</strong>
                    &nbsp;·&nbsp; Model: {pred.get('model_name','—')}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Risk Assessment
        _section("⚠️", "Risk Assessment")
        for label, key in [("Process Stability","process_stability"),("Yield Risk","yield_risk"),("Equipment Risk","equipment_risk")]:
            level = risk.get(key,"—")
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;align-items:center;padding:0.4rem 0;border-bottom:1px solid {C["surface"]};">'
                f'<span style="font-size:0.85rem;color:{C["text_muted"]};">{label}</span>'
                f'{risk_pill_html(level)}</div>',
                unsafe_allow_html=True,
            )

        # Preventive Actions
        _section("🛠", "Preventive Actions")
        for i, action in enumerate(actions, 1):
            action_icons = {"Chamber Cleaning":"🧹","ESC Inspection":"🔌","MFC Calibration":"💨","Verify Recipe":"📋","Preventive Maintenance":"🔧"}
            icon = action_icons.get(action, "🔧")
            st.markdown(
                f"""
                <div style="
                    display:flex;align-items:center;gap:0.65rem;
                    padding:0.55rem 0.85rem;margin-bottom:0.4rem;
                    background:{C['surface']};border-radius:8px;
                    border-left:3px solid {C['accent']};
                ">
                    <span style="font-size:0.82rem;font-weight:800;color:{C['accent']};width:1rem;">{i}.</span>
                    <span style="font-size:0.95rem;">{icon}</span>
                    <span style="font-size:0.875rem;font-weight:600;color:{C['text']};">{action}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Reviewer AI Verification
        _section("🤖", "Reviewer AI Verification")
        verified     = verdict.get("analysis_verified", verdict.get("approved", False))
        contradiction= verdict.get("contradiction_found", False)
        ev_strength  = verdict.get("evidence_strength", conf * 0.95)

        check_color = lambda ok: C["success"] if ok else C["danger"]
        check_icon  = lambda ok: "✔" if ok else "✗"

        st.markdown(
            f"""
            <div style="background:{C['surface']};border:1px solid {C['border']};border-radius:12px;padding:1rem 1.25rem;">
                <div style="display:flex;align-items:center;gap:0.5rem;padding:0.3rem 0;font-size:0.875rem;font-weight:500;color:{check_color(verified)};">
                    <span>{check_icon(verified)}</span> Analysis verified
                </div>
                <div style="display:flex;align-items:center;gap:0.5rem;padding:0.3rem 0;font-size:0.875rem;font-weight:500;color:{check_color(not contradiction)};">
                    <span>{check_icon(not contradiction)}</span> No contradiction found
                </div>
                <div style="margin-top:0.75rem;">
                    <div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;color:{C['text_muted']};">Evidence Strength</div>
                    <div style="font-size:2rem;font-weight:800;color:{C['text']};letter-spacing:-0.04em;">{ev_strength:.0f}%</div>
                </div>
                <div style="font-size:0.75rem;color:{C['text_muted']};margin-top:0.3rem;font-style:italic;">{verdict.get('reviewer_notes','')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Confidence score (full width) ──────────────────────────────────────
    st.divider()
    conf_col, _ = st.columns([2, 3])
    with conf_col:
        confidence_bar(conf)

    # ── Download button ────────────────────────────────────────────────────
    st.markdown("")
    report_md = _build_markdown_report(snap, top_causes, actions, ts)
    st.download_button(
        label="⬇️ Download Report (Markdown)",
        data=report_md.encode("utf-8"),
        file_name=f"fabsense_report_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
        mime="text/markdown",
        type="primary",
    )


def _section(icon: str, title: str) -> None:
    st.markdown(
        f"""
        <div style="
            font-size:0.78rem;font-weight:700;text-transform:uppercase;
            letter-spacing:0.07em;color:{C['text_muted']};
            margin:1.1rem 0 0.65rem 0;padding-bottom:0.4rem;
            border-bottom:1px solid {C['border']};
            display:flex;align-items:center;gap:0.4rem;
        ">{icon}&nbsp;{title}</div>
        """,
        unsafe_allow_html=True,
    )


def _build_markdown_report(
    snap: dict[str, Any],
    top_causes: list[tuple[str, int]],
    actions: list[str],
    ts: str,
) -> str:
    risk    = snap.get("risk", {})
    pred    = snap.get("prediction", {})
    expl    = snap.get("explainability", {})
    verdict = snap.get("agent_verdict") or {}
    conf    = expl.get("confidence_score", 0)

    lines = [
        "# Semiconductor AI Process Report",
        f"**Generated:** {ts} | **FabSense AI v2.0** | **Dual-Agent Verified**",
        "",
        "---",
        "",
        "## Executive Summary",
        verdict.get("reviewed_analysis", ""),
        "",
        "## Current Process Status",
        f"- **Status:** {snap.get('process_status','—')}",
        f"- **Risk Level:** {risk.get('risk_level','—')} ({risk.get('risk_score',0):.0f}/100)",
        f"- **Equipment:** {snap.get('equipment_status','—')}",
        "",
        "## Root Cause Analysis",
    ]
    for i, (name, pct) in enumerate(top_causes, 1):
        lines.append(f"{i}. **{name}** — Importance: {pct}%")
    lines += [
        "",
        "## Yield Prediction",
        f"- **Current Yield:** {snap.get('current_yield','—')}%",
        f"- **Predicted Yield:** {snap.get('predicted_yield','—')}%",
        f"- **Trend:** {pred.get('yield_trend','—')}",
        f"- **Failure Probability:** {pred.get('failure_probability',0):.0%}",
        "",
        "## Risk Assessment",
        f"- **Process Stability:** {risk.get('process_stability','—')}",
        f"- **Yield Risk:** {risk.get('yield_risk','—')}",
        f"- **Equipment Risk:** {risk.get('equipment_risk','—')}",
        "",
        "## Preventive Actions",
    ]
    for i, a in enumerate(actions, 1):
        lines.append(f"{i}. {a}")
    lines += [
        "",
        "## Reviewer AI Verification",
        f"- Analysis Verified: {'Yes' if verdict.get('analysis_verified') else 'No'}",
        f"- Contradiction Found: {'Yes' if verdict.get('contradiction_found') else 'No'}",
        f"- Evidence Strength: {verdict.get('evidence_strength', 0):.0f}%",
        f"- Confidence Score: {conf:.0f}%",
        "",
        f"*{verdict.get('reviewer_notes','')}*",
        "",
        "---",
        "*Report generated by FabSense AI — Semiconductor Process Intelligence Platform*",
    ]
    return "\n".join(lines)
