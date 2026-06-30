"""Tab 4 — Preventive Maintenance: prioritized action cards."""

from __future__ import annotations

from typing import Any

import streamlit as st

from utils.components import empty_state, page_header, render_metric_row, section_title
from utils.executive_report import extract_recommended_actions
from utils.theme import COLORS

C = COLORS

PRIORITY_META = {
    "high":   {"label": "HIGH",   "color": C["danger"],  "bg": C["danger_bg"],  "icon": "🔴", "border": "#DC2626"},
    "medium": {"label": "MEDIUM", "color": C["warning"], "bg": C["warning_bg"], "icon": "🟠", "border": "#D97706"},
    "low":    {"label": "LOW",    "color": C["success"], "bg": C["success_bg"], "icon": "🟢", "border": "#16A34A"},
}

ACTION_ICONS = {
    "Chamber Cleaning":      "🧹",
    "ESC Inspection":        "🔌",
    "MFC Calibration":       "💨",
    "Verify Recipe":         "📋",
    "Preventive Maintenance":"🔧",
}


def render_tab_maintenance(snap: dict[str, Any]) -> None:
    page_header("🛠 Preventive Maintenance", "AI-generated prioritized maintenance recommendations to prevent yield loss")

    recs   = snap.get("recommendations", [])
    verdict = snap.get("agent_verdict") or {}

    if not recs:
        empty_state("🛠", "No Recommendations", "Run analysis with process data to generate maintenance recommendations.")
        return

    # ── Summary KPIs ──────────────────────────────────────────────────────
    high_count = sum(1 for r in recs if r.get("priority") == "high")
    med_count  = sum(1 for r in recs if r.get("priority") == "medium")
    avg_reduce = sum(r.get("risk_reduction", 0) for r in recs) / max(len(recs), 1)

    render_metric_row([
        ("🔴", "High Priority",   str(high_count),     "Requires immediate action"),
        ("🟠", "Medium Priority", str(med_count),       "Schedule within 1 week"),
        ("📉", "Avg. Risk Reduction", f"{avg_reduce:.0%}", "Across all actions"),
        ("📋", "Total Actions",   str(len(recs)),       "Prioritized recommendations"),
    ])

    st.markdown("<br>", unsafe_allow_html=True)

    # Reviewer note
    if verdict.get("needs_more_data"):
        st.warning("⚠️ Reviewer: " + "; ".join(verdict.get("data_requests", [])))

    col_cards, col_order = st.columns([3, 2])

    # ── Action cards ──────────────────────────────────────────────────────
    with col_cards:
        section_title("📋", "Action Cards")

        for rec in recs:
            pri    = rec.get("priority", "medium").lower()
            meta   = PRIORITY_META.get(pri, PRIORITY_META["medium"])
            action = rec.get("action", "Maintenance Action")
            icon   = ACTION_ICONS.get(action, "🔧")
            equip  = rec.get("equipment", "")
            detail = rec.get("detail", "")
            reason = rec.get("rationale", "")
            reduce = rec.get("risk_reduction", 0)
            rank   = rec.get("rank", 0)

            st.markdown(
                f"""
                <div class="maint-card maint-{pri}">
                    <div style="display:flex;align-items:flex-start;gap:1rem;">
                        <div style="
                            background:{meta['bg']};
                            width:44px;height:44px;border-radius:12px;
                            display:flex;align-items:center;justify-content:center;
                            font-size:1.35rem;flex-shrink:0;
                        ">{icon}</div>
                        <div style="flex:1;">
                            <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.25rem;">
                                <span class="maint-title">#{rank} {action}</span>
                                <span style="
                                    background:{meta['bg']};color:{meta['color']};
                                    font-size:0.68rem;font-weight:700;
                                    padding:0.15rem 0.55rem;border-radius:999px;
                                    text-transform:uppercase;letter-spacing:0.05em;
                                ">{meta['label']}</span>
                            </div>
                            <div class="maint-sub" style="margin-bottom:0.35rem;">
                                🔧 {equip}{f" — {detail[:80]}" if detail and detail != action else ""}
                            </div>
                            <div style="font-size:0.82rem;color:{C['text_muted']};font-style:italic;">
                                {reason}
                            </div>
                        </div>
                        <div style="text-align:right;flex-shrink:0;">
                            <div style="font-size:1.1rem;font-weight:800;color:{meta['color']};">{reduce:.0%}</div>
                            <div style="font-size:0.68rem;color:{C['text_muted']};font-weight:500;">Risk ↓</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ── Execution order ────────────────────────────────────────────────────
    with col_order:
        section_title("📋", "Recommended Execution Order")

        action_names = extract_recommended_actions(snap, limit=6)
        action_icons_all = {
            "Chamber Cleaning":      "🧹",
            "ESC Inspection":        "🔌",
            "MFC Calibration":       "💨",
            "Verify Recipe":         "📋",
            "Preventive Maintenance":"🔧",
        }

        for i, name in enumerate(action_names, 1):
            icon = action_icons_all.get(name, "🔧")
            st.markdown(
                f"""
                <div style="
                    display:flex;align-items:center;gap:0.75rem;
                    padding:0.75rem 1rem;
                    background:{C['surface']};border:1px solid {C['border']};
                    border-radius:10px;margin-bottom:0.5rem;
                    transition:background 0.15s;
                ">
                    <div style="
                        background:{C['accent']};color:white;
                        width:26px;height:26px;border-radius:50%;
                        display:flex;align-items:center;justify-content:center;
                        font-size:0.78rem;font-weight:700;flex-shrink:0;
                    ">{i}</div>
                    <span style="font-size:1rem;">{icon}</span>
                    <span style="font-size:0.875rem;font-weight:600;color:{C['text']};">{name}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        section_title("📊", "Expected Improvement")
        st.markdown(
            f"""
            <div style="background:{C['surface_alt']};border:1px solid rgba(37,99,235,0.2);border-radius:12px;padding:1.25rem;">
                <div style="font-size:0.78rem;color:{C['text_muted']};margin-bottom:0.35rem;">Est. Risk Reduction</div>
                <div style="font-size:2rem;font-weight:800;color:{C['accent']};letter-spacing:-0.04em;">{avg_reduce:.0%}</div>
                <div style="font-size:0.78rem;color:{C['text_muted']};margin-top:0.25rem;">
                    Based on {len(recs)} prioritized action(s)
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
