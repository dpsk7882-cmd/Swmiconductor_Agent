"""Tab 2 — Yield Loss Analysis: root cause ranking with importance bars."""

from __future__ import annotations

from typing import Any

import streamlit as st

from utils.components import confidence_bar, empty_state, page_header, risk_pill_html, section_title
from utils.executive_report import extract_top_root_causes
from utils.theme import COLORS

C = COLORS

RANK_MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}


def render_tab_yield_loss(snap: dict[str, Any]) -> None:
    page_header("📉 Yield Loss Analysis", "Root cause ranking and yield degradation factor identification")

    drifts       = snap.get("drifts", [])
    root_causes  = snap.get("root_causes", [])
    yield_factors = snap.get("yield_factors", [])
    expl         = snap.get("explainability", {})
    conf         = expl.get("confidence_score", 0)

    if not drifts and not root_causes:
        empty_state("📉", "No Yield Loss Data", "Upload process data with a yield column to enable yield loss analysis.")
        return

    top_causes = extract_top_root_causes(snap, limit=5)

    # ── Confidence ────────────────────────────────────────────────────────
    conf_col, _ = st.columns([2, 3])
    with conf_col:
        confidence_bar(conf)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([3, 2])

    # ── Root cause ranking ────────────────────────────────────────────────
    with col_left:
        section_title("🏆", "Top Root Cause Ranking")

        for i, (name, pct) in enumerate(top_causes, 1):
            medal = RANK_MEDALS.get(i, f"#{i}")
            sev   = _pct_to_sev(pct)
            bar_color  = {"high": C["danger"], "medium": C["warning"], "low": C["success"]}.get(sev, C["accent"])
            card_class = f"rca-card-{sev}"

            # Find matching root cause for evidence
            rc_match = next((rc for rc in root_causes if name.lower() in rc.get("factor","").lower()), None)
            evidence  = rc_match.get("explanation", "") if rc_match else ""
            ev_list   = (rc_match.get("evidence", []) or []) if rc_match else []

            st.markdown(
                f"""
                <div class="rca-card {card_class}">
                    <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.4rem;">
                        <span class="rca-rank">{medal}</span>
                        <div>
                            <div class="rca-name">{name}</div>
                            <div class="rca-expl">{evidence}</div>
                        </div>
                        <div style="margin-left:auto;text-align:right;">
                            <div style="font-size:1.25rem;font-weight:800;color:{bar_color};">{pct}%</div>
                            <div style="font-size:0.7rem;color:{C['text_muted']};font-weight:500;">Importance</div>
                        </div>
                    </div>
                    <div class="imp-bar"><div class="imp-fill" style="width:{pct}%;background:{bar_color};"></div></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if ev_list:
                with st.expander(f"Evidence for {name}", expanded=False):
                    for ev in ev_list[:3]:
                        st.markdown(f"- {ev}")

    # ── Yield factors & risk summary ──────────────────────────────────────
    with col_right:
        section_title("📊", "Yield Degradation Factors")

        if yield_factors:
            for f in yield_factors[:6]:
                param  = f.get("parameter", "")
                interp = f.get("interpretation", f.get("parameter", ""))
                imp    = f.get("impact_score", 0)
                direction = f.get("direction", "")
                dir_icon  = "↓" if direction == "negative" else "↑"

                st.markdown(
                    f"""
                    <div style="
                        background:{C['surface']};border:1px solid {C['border']};
                        border-radius:10px;padding:0.85rem 1rem;margin-bottom:0.5rem;
                    ">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <span style="font-size:0.875rem;font-weight:600;color:{C['text']};">{param} {dir_icon}</span>
                            <span style="font-size:0.82rem;font-weight:700;color:{C['accent']};">{imp:.0%}</span>
                        </div>
                        <div style="font-size:0.75rem;color:{C['text_muted']};margin-top:0.2rem;">{interp}</div>
                        <div style="height:4px;background:{C['border']};border-radius:999px;margin-top:0.4rem;overflow:hidden;">
                            <div style="height:4px;width:{imp*100:.0f}%;background:{C['accent']};border-radius:999px;"></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("Upload data with a yield column to calculate degradation factors.")

        section_title("🎯", "Risk Summary")
        risk = snap.get("risk", {})
        for label, key in [("Process Stability", "process_stability"), ("Yield Risk", "yield_risk"), ("Equipment Risk", "equipment_risk")]:
            level = risk.get(key, "—")
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;padding:0.4rem 0;border-bottom:1px solid {C["surface"]};">'
                f'<span style="font-size:0.85rem;color:{C["text_muted"]};">{label}</span>'
                f'{risk_pill_html(level)}</div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            f'<div style="margin-top:0.75rem;font-size:0.82rem;color:{C["text_muted"]};">{risk.get("summary","")}</div>',
            unsafe_allow_html=True,
        )


def _pct_to_sev(pct: int) -> str:
    if pct >= 30:
        return "high"
    if pct >= 15:
        return "medium"
    return "low"
