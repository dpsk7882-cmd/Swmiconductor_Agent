"""Executive AI report panel — structured fab decision-support layout."""

from __future__ import annotations

import streamlit as st

# Circled number prefixes for ranked lists
RANK_NUMS = ("①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧")

# Drift category → display label
CAUSE_LABELS: dict[str, str] = {
    "ARC Count Increase": "ARC Count ↑",
    "Pressure Drift": "Pressure Drift",
    "Particle Increase": "Particle Increase",
    "Equipment Instability": "RF Instability",
    "RF Power Drift": "RF Instability",
    "Temperature Drift": "Temperature Drift",
    "Gas Flow Abnormality": "Gas Flow Abnormality",
    "High-Z Events": "High-Z Events",
    "Chamber Temp C": "Temperature Drift",
    "Chamber Temp": "Temperature Drift",
    "Rf Power W": "RF Instability",
    "Particle Count": "Particle Increase",
    "Defect Density Cm2": "Particle Increase",
}

SEVERITY_WEIGHT = {"critical": 4.0, "high": 3.0, "medium": 2.0, "low": 1.0}

RISK_EMOJI = {"Low": "🟢", "Medium": "🟠", "High": "🔴"}


def _divider() -> str:
    return '<hr class="exec-divider" />'


def _section_title(title: str) -> str:
    return f'<div class="exec-section-title">{title}</div>'


def _normalize_importance(items: list[tuple[str, float]]) -> list[tuple[str, int]]:
    """Convert raw weights to integer percentages summing to ~100."""
    if not items:
        return []
    total = sum(w for _, w in items) or 1.0
    raw = [(name, (w / total) * 100) for name, w in items]
    rounded = [(name, int(round(pct))) for name, pct in raw]
    # Fix rounding drift on largest item
    diff = 100 - sum(p for _, p in rounded)
    if rounded and diff != 0:
        idx = max(range(len(rounded)), key=lambda i: rounded[i][1])
        name, pct = rounded[idx]
        rounded[idx] = (name, pct + diff)
    return rounded


def extract_top_root_causes(snap: dict, limit: int = 5) -> list[tuple[str, int]]:
    """Build top-N root causes with importance % from drifts and RCA."""
    weights: dict[str, float] = {}

    def _label(raw: str) -> str:
        if raw in CAUSE_LABELS:
            return CAUSE_LABELS[raw]
        norm = raw.lower().replace("_", " ")
        for key, disp in CAUSE_LABELS.items():
            if key.lower() in norm or norm in key.lower():
                return disp
        return raw

    for drift in snap.get("drifts", []):
        label = _label(drift.get("category", ""))
        w = SEVERITY_WEIGHT.get(drift.get("severity", "medium"), 2.0)
        weights[label] = weights.get(label, 0) + w

    for rc in snap.get("root_causes", []):
        label = _label(rc.get("factor", ""))
        score = rc.get("score", 0.5)
        weights[label] = weights.get(label, 0) + score * 3.0

    ranked = sorted(weights.items(), key=lambda x: -x[1])[:limit]
    return _normalize_importance(ranked)


def extract_recommended_actions(snap: dict, limit: int = 4) -> list[str]:
    """Standardized PM action labels for the report."""
    standard = {
        "chamber cleaning": "Chamber Cleaning",
        "chamber clean": "Chamber Cleaning",
        "esc inspection": "ESC Inspection",
        "electrostatic": "ESC Inspection",
        "recipe verification": "Verify Recipe",
        "recipe verify": "Verify Recipe",
        "verify recipe": "Verify Recipe",
        "mfc calibration": "MFC Calibration",
        "gas delivery": "MFC Calibration",
        "preventive maintenance": "Preventive Maintenance",
        "alarm": "Preventive Maintenance",
        "review alarm": "Preventive Maintenance",
    }

    seen: set[str] = set()
    actions: list[str] = []

    for rec in snap.get("recommendations", []):
        action = rec.get("action") or rec.get("detail") or ""
        detail = (action + " " + rec.get("detail", "") + " " + rec.get("rationale", "")).lower()
        label = action
        for key, name in standard.items():
            if key in detail or key in action.lower():
                label = name
                break
        # Skip raw log-message actions unless mapped
        if label == action and len(label) > 40:
            label = "Preventive Maintenance"
        if label not in seen:
            seen.add(label)
            actions.append(label)

    # Enrich from top root causes if fewer than 4 actions
    cause_to_action = {
        "ARC Count ↑": "ESC Inspection",
        "RF Instability": "ESC Inspection",
        "Particle Increase": "Chamber Cleaning",
        "Temperature Drift": "Chamber Cleaning",
        "Pressure Drift": "Verify Recipe",
        "Gas Flow Abnormality": "MFC Calibration",
    }
    for cause, _ in extract_top_root_causes(snap, limit=5):
        suggestion = cause_to_action.get(cause)
        if suggestion and suggestion not in seen and len(actions) < 4:
            seen.add(suggestion)
            actions.append(suggestion)

    if actions:
        return actions[:limit]

    return ["Chamber Cleaning", "ESC Inspection", "Verify Recipe", "MFC Calibration"][:limit]


def render_executive_report(snap: dict) -> None:
    """Render the structured executive report matching the fab UI spec."""
    risk = snap.get("risk", {})
    expl = snap.get("explainability", {})
    verdict = snap.get("agent_verdict") or {}

    predicted = snap.get("predicted_yield")
    predicted_str = f"{predicted:.1f}%" if predicted is not None else "—"
    confidence = expl.get("confidence_score", 0)
    risk_level = risk.get("risk_level", "Medium")
    risk_emoji = RISK_EMOJI.get(risk_level, "🟠")

    top_causes = extract_top_root_causes(snap, limit=5)
    actions = extract_recommended_actions(snap, limit=4)

    verified = verdict.get("analysis_verified", verdict.get("approved", False))
    contradiction = verdict.get("contradiction_found", False)
    evidence_strength = verdict.get("evidence_strength", confidence * 0.95)

    verify_icon = "✔" if verified else "✗"
    verify_text = "Analysis verified" if verified else "Analysis not verified"
    contra_icon = "✔" if not contradiction else "✗"
    contra_text = "No contradiction found" if not contradiction else "Contradiction detected"

    # --- Yield Prediction block ---
    blocks: list[str] = [
        _divider(),
        _section_title("Yield Prediction"),
        f'<div class="exec-row"><span class="exec-label">Predicted Yield</span>'
        f'<span class="exec-value accent">{predicted_str}</span></div>',
        f'<div class="exec-row"><span class="exec-label">Confidence</span>'
        f'<span class="exec-value">{confidence:.0f}%</span></div>',
        f'<div class="exec-row"><span class="exec-label">Risk Level</span>'
        f'<span class="exec-value">{risk_emoji} {risk_level}</span></div>',
        _divider(),
        _section_title("Top 5 Root Causes"),
    ]

    if top_causes:
        for i, (name, pct) in enumerate(top_causes):
            num = RANK_NUMS[i] if i < len(RANK_NUMS) else f"{i + 1}."
            blocks.append(
                f'<div class="exec-cause-row">'
                f'<span class="exec-cause-name">{num} {name}</span>'
                f'<span class="exec-cause-pct">Importance {pct}%</span>'
                f'</div>'
            )
    else:
        blocks.append('<div class="exec-muted">No root causes identified — upload process data.</div>')

    blocks.extend([
        _divider(),
        _section_title("Reviewer AI"),
        f'<div class="exec-check">{verify_icon} {verify_text}</div>',
        f'<div class="exec-check">{contra_icon} {contra_text}</div>',
        '<div class="exec-evidence-label">Evidence Strength</div>',
        f'<div class="exec-evidence-value">{evidence_strength:.0f}%</div>',
        _divider(),
        _section_title("Recommended Actions"),
    ])

    for i, action in enumerate(actions):
        num = RANK_NUMS[i] if i < len(RANK_NUMS) else f"{i + 1}."
        blocks.append(f'<div class="exec-action">{num} {action}</div>')

    blocks.append(_divider())

    st.markdown(
        f'<div class="executive-report">{"".join(blocks)}</div>',
        unsafe_allow_html=True,
    )
