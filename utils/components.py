"""Reusable UI components — white SaaS theme."""

from __future__ import annotations

import streamlit as st

from utils.theme import COLORS, RISK_COLORS, STATUS_COLORS

C = COLORS

# ── Top navbar ────────────────────────────────────────────────────────────────

def render_navbar(status: str = "Normal", timestamp: str = "", files: int = 0) -> None:
    status_color = STATUS_COLORS.get(status, "#6B7280")
    dot_color = {"Normal": "#16A34A", "Watch": "#D97706", "Alert": "#DC2626"}.get(status, "#9CA3AF")
    ts_text = f"Last analysis: {timestamp}" if timestamp else "No analysis yet"
    st.markdown(
        f"""
        <div class="fab-navbar">
            <div class="fab-navbar-logo">
                ⚗️&nbsp;<span>FabSense&nbsp;<span class="logo-accent">AI</span></span>
            </div>
            <div class="fab-navbar-right">
                <div class="fab-navbar-status">
                    <span class="status-dot" style="background:{dot_color};"></span>
                    &nbsp;{status}
                </div>
                <div class="fab-navbar-timestamp">{ts_text}</div>
                {f'<div class="fab-navbar-timestamp">{files} file(s)</div>' if files else ''}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Metric cards ──────────────────────────────────────────────────────────────

def metric_card_html(icon: str, label: str, value: str, sub: str = "", color: str = "") -> str:
    val_style = f"color:{color};" if color else ""
    sub_html  = f'<div class="fab-metric-sub">{sub}</div>' if sub else ""
    return f"""
    <div class="fab-metric animate-fadeup">
        <div class="fab-metric-icon">{icon}</div>
        <div class="fab-metric-label">{label}</div>
        <div class="fab-metric-value" style="{val_style}">{value}</div>
        {sub_html}
    </div>"""


def render_metric_row(cards: list[tuple]) -> None:
    """Render a row of metric cards. Each card: (icon, label, value, sub) or (icon, label, value, sub, color)."""
    cols = st.columns(len(cards))
    for col, card in zip(cols, cards):
        icon, label, value = card[0], card[1], card[2]
        sub   = card[3] if len(card) > 3 else ""
        color = card[4] if len(card) > 4 else ""
        with col:
            st.markdown(metric_card_html(icon, label, value, sub, color), unsafe_allow_html=True)


# ── Pills ─────────────────────────────────────────────────────────────────────

def risk_pill_html(level: str) -> str:
    cls   = {"Low": "fab-pill-low", "Medium": "fab-pill-medium", "High": "fab-pill-high"}.get(level, "fab-pill-unknown")
    icons = {"Low": "🟢", "Medium": "🟠", "High": "🔴"}
    icon  = icons.get(level, "⚪")
    return f'<span class="fab-pill {cls}">{icon} {level}</span>'


# Backward-compatible alias
risk_pill = risk_pill_html


def status_pill_html(status: str) -> str:
    cls   = {"Normal": "fab-pill-normal", "Watch": "fab-pill-watch", "Alert": "fab-pill-alert"}.get(status, "fab-pill-unknown")
    icons = {"Normal": "🟢", "Watch": "🟡", "Alert": "🔴"}
    icon  = icons.get(status, "⚪")
    return f'<span class="fab-pill {cls}">{icon} {status}</span>'


# ── Section title ─────────────────────────────────────────────────────────────

def section_title(icon: str, title: str) -> None:
    st.markdown(f'<div class="fab-section">{icon}&nbsp; {title}</div>', unsafe_allow_html=True)


# ── Confidence bar ────────────────────────────────────────────────────────────

def confidence_bar(score: float, label: str = "Confidence Score") -> None:
    fill  = min(max(score, 0), 100)
    color = C["success"] if score >= 75 else C["warning"] if score >= 45 else C["danger"]
    tier  = "High" if score >= 75 else "Moderate" if score >= 45 else "Low"
    st.markdown(
        f"""
        <div style="margin:0.5rem 0 1rem 0;">
            <div style="display:flex;justify-content:space-between;margin-bottom:0.3rem;">
                <span style="font-size:0.78rem;font-weight:600;color:{C['text_muted']};text-transform:uppercase;letter-spacing:0.05em;">{label}</span>
                <span style="font-size:0.9rem;font-weight:700;color:{color};">{score:.0f}% — {tier}</span>
            </div>
            <div class="conf-track">
                <div class="conf-fill" style="width:{fill}%;background:{color};"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Empty state ───────────────────────────────────────────────────────────────

def empty_state(icon: str, title: str, message: str) -> None:
    st.markdown(
        f"""
        <div class="empty-state animate-fadein">
            <div class="empty-icon">{icon}</div>
            <div class="empty-title">{title}</div>
            <div class="empty-sub">{message}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Analysis-step progress ────────────────────────────────────────────────────

ANALYSIS_STEPS = [
    ("📂", "File uploaded"),
    ("🔍", "Reading process data"),
    ("📊", "Detecting abnormal parameters"),
    ("🧠", "Running AI yield analysis"),
    ("📉", "Predicting future yield"),
    ("⚠️", "Evaluating process risk"),
    ("🤖", "Reviewer AI verification"),
    ("✅", "Analysis complete"),
]


def render_analysis_progress(completed: int, active: int) -> None:
    """Render the animated step-by-step progress list."""
    rows = []
    for i, (icon, text) in enumerate(ANALYSIS_STEPS):
        if i < completed:
            rows.append(
                f'<div class="step-row done">'
                f'<span class="step-dot dot-done">✓</span>'
                f'<span>{icon} {text}</span>'
                f'</div>'
            )
        elif i == active:
            rows.append(
                f'<div class="step-row active">'
                f'<span class="step-dot dot-active">⋯</span>'
                f'<span>{icon} {text}…</span>'
                f'</div>'
            )
        else:
            rows.append(
                f'<div class="step-row wait">'
                f'<span class="step-dot dot-wait">{i+1}</span>'
                f'<span>{icon} {text}</span>'
                f'</div>'
            )
    st.markdown(
        f'<div class="step-list">{"".join(rows)}</div>',
        unsafe_allow_html=True,
    )


# ── Backward-compatible shims ─────────────────────────────────────────────────

def platform_header(title: str, subtitle: str = "", badge: str = "") -> None:
    """Backward-compatible header used by legacy page modules."""
    page_header(title, subtitle)


def panel(title: str, icon: str = "") -> None:
    """Backward-compatible section panel header."""
    section_title(icon, title)


# ── Page header ───────────────────────────────────────────────────────────────

def page_header(title: str, subtitle: str = "") -> None:
    sub_html = f'<p style="color:{C["text_muted"]};font-size:0.875rem;margin:0.25rem 0 0 0;">{subtitle}</p>' if subtitle else ""
    st.markdown(
        f"""
        <div style="margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:1px solid {C['border']};">
            <h2 style="margin:0;font-size:1.35rem;font-weight:800;letter-spacing:-0.03em;">{title}</h2>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
