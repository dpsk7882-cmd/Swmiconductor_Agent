"""White professional SaaS theme for the Semiconductor AI Platform."""

from __future__ import annotations

import streamlit as st

# ── Design tokens ────────────────────────────────────────────────────────────
COLORS = {
    "bg":           "#FFFFFF",
    "surface":      "#F8F9FB",
    "surface_alt":  "#EFF6FF",
    "border":       "#E6EAF0",
    "text":         "#1A1D23",
    "text_muted":   "#6B7280",
    "text_light":   "#9CA3AF",
    "accent":       "#2563EB",
    "accent_hover": "#1D4ED8",
    "accent_light": "#EFF6FF",
    "success":      "#16A34A",
    "success_bg":   "#DCFCE7",
    "warning":      "#D97706",
    "warning_bg":   "#FEF3C7",
    "danger":       "#DC2626",
    "danger_bg":    "#FEE2E2",
    "info":         "#0891B2",
    "info_bg":      "#E0F2FE",
}

RISK_COLORS   = {"Low": "#16A34A", "Medium": "#D97706", "High": "#DC2626"}
STATUS_COLORS = {"Normal": "#16A34A", "Watch": "#D97706", "Alert": "#DC2626", "Unknown": "#6B7280"}


def inject_theme() -> None:
    """Inject the complete white SaaS theme CSS."""
    c = COLORS
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        /* ── Global ──────────────────────────────────────────────────────── */
        * {{ box-sizing: border-box; }}

        .stApp {{
            background: {c['bg']} !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        }}

        .main .block-container {{
            padding-top: 0 !important;
            padding-bottom: 2rem !important;
            max-width: 1400px;
        }}

        /* ── Hide Streamlit chrome ───────────────────────────────────────── */
        #MainMenu {{ visibility: hidden !important; }}
        footer    {{ visibility: hidden !important; }}
        [data-testid="stHeader"] {{ display: none !important; }}
        [data-testid="stToolbar"] {{ display: none !important; }}
        [data-testid="stDecoration"] {{ display: none !important; }}

        /* ── Sidebar ─────────────────────────────────────────────────────── */
        [data-testid="stSidebar"] {{
            background: {c['bg']} !important;
            border-right: 1px solid {c['border']} !important;
            padding-top: 0 !important;
        }}
        [data-testid="stSidebar"] .stMarkdown,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span {{ color: {c['text']} !important; }}
        [data-testid="stSidebarContent"] {{ padding: 0 0.5rem !important; }}

        /* ── Typography ──────────────────────────────────────────────────── */
        h1, h2, h3, h4, h5, h6 {{
            color: {c['text']} !important;
            font-family: 'Inter', sans-serif !important;
            letter-spacing: -0.02em;
        }}
        p, span, li {{ color: {c['text']}; font-family: 'Inter', sans-serif !important; }}

        /* ── Streamlit tabs ──────────────────────────────────────────────── */
        .stTabs [data-baseweb="tab-list"] {{
            background: {c['bg']} !important;
            border-bottom: 2px solid {c['border']} !important;
            gap: 0 !important;
            padding: 0 !important;
        }}
        .stTabs [data-baseweb="tab"] {{
            background: transparent !important;
            border: none !important;
            color: {c['text_muted']} !important;
            font-size: 0.875rem !important;
            font-weight: 500 !important;
            padding: 0.85rem 1.4rem !important;
            border-radius: 0 !important;
            transition: color 0.15s, background 0.15s !important;
        }}
        .stTabs [data-baseweb="tab"]:hover {{
            color: {c['accent']} !important;
            background: {c['accent_light']} !important;
        }}
        .stTabs [aria-selected="true"] {{
            color: {c['accent']} !important;
            border-bottom: 2px solid {c['accent']} !important;
            font-weight: 600 !important;
            background: transparent !important;
        }}
        .stTabs [data-baseweb="tab-panel"] {{
            padding: 1.5rem 0 0 0 !important;
        }}

        /* ── Buttons ─────────────────────────────────────────────────────── */
        .stButton > button {{
            border-radius: 8px !important;
            font-weight: 500 !important;
            font-size: 0.875rem !important;
            transition: all 0.15s ease !important;
            border: 1px solid {c['border']} !important;
            background: {c['bg']} !important;
            color: {c['text']} !important;
            padding: 0.5rem 1rem !important;
        }}
        .stButton > button:hover {{
            border-color: {c['accent']} !important;
            color: {c['accent']} !important;
            background: {c['accent_light']} !important;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(37,99,235,0.12) !important;
        }}
        .stButton > button[kind="primary"] {{
            background: {c['accent']} !important;
            color: #fff !important;
            border-color: {c['accent']} !important;
            box-shadow: 0 2px 8px rgba(37,99,235,0.25) !important;
        }}
        .stButton > button[kind="primary"]:hover {{
            background: {c['accent_hover']} !important;
            border-color: {c['accent_hover']} !important;
            box-shadow: 0 4px 16px rgba(37,99,235,0.35) !important;
        }}

        /* ── Inputs ──────────────────────────────────────────────────────── */
        .stTextInput input, .stTextArea textarea, .stSelectbox select {{
            border-radius: 8px !important;
            border: 1px solid {c['border']} !important;
            background: {c['bg']} !important;
            color: {c['text']} !important;
            font-size: 0.875rem !important;
        }}
        .stTextInput input:focus, .stTextArea textarea:focus {{
            border-color: {c['accent']} !important;
            box-shadow: 0 0 0 3px rgba(37,99,235,0.1) !important;
        }}

        /* ── Expanders ───────────────────────────────────────────────────── */
        [data-testid="stExpander"] {{
            background: {c['bg']} !important;
            border: 1px solid {c['border']} !important;
            border-radius: 10px !important;
            overflow: hidden !important;
        }}
        [data-testid="stExpander"] summary {{
            color: {c['text']} !important;
            font-weight: 500 !important;
            font-size: 0.9rem !important;
            background: {c['surface']} !important;
            padding: 0.85rem 1rem !important;
        }}

        /* ── Dataframe ───────────────────────────────────────────────────── */
        .stDataFrame {{ border: 1px solid {c['border']} !important; border-radius: 10px !important; overflow: hidden; }}
        .stDataFrame th {{ background: {c['surface']} !important; color: {c['text']} !important; font-weight: 600 !important; font-size: 0.8rem !important; }}
        .stDataFrame td {{ color: {c['text']} !important; font-size: 0.82rem !important; }}

        /* ── Dividers ────────────────────────────────────────────────────── */
        hr {{ border: none !important; border-top: 1px solid {c['border']} !important; margin: 1.25rem 0 !important; }}

        /* ── Metrics ─────────────────────────────────────────────────────── */
        [data-testid="stMetricValue"] {{
            font-size: 1.85rem !important;
            font-weight: 800 !important;
            color: {c['text']} !important;
        }}
        [data-testid="stMetricLabel"] {{
            font-size: 0.72rem !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.06em !important;
            color: {c['text_muted']} !important;
        }}
        [data-testid="stMetricDelta"] {{ font-size: 0.82rem !important; }}

        /* ── Progress bar ────────────────────────────────────────────────── */
        .stProgress > div > div > div > div {{
            background: linear-gradient(90deg, {c['accent']}, #7C3AED) !important;
            border-radius: 999px !important;
        }}
        .stProgress > div > div {{
            background: {c['surface']} !important;
            border-radius: 999px !important;
        }}

        /* ── File uploader ───────────────────────────────────────────────── */
        [data-testid="stFileUploadDropzone"] {{
            border: 2px dashed {c['border']} !important;
            border-radius: 16px !important;
            background: {c['surface']} !important;
            transition: border-color 0.2s, background 0.2s !important;
            padding: 2rem !important;
        }}
        [data-testid="stFileUploadDropzone"]:hover {{
            border-color: {c['accent']} !important;
            background: {c['accent_light']} !important;
        }}

        /* ── Alerts ──────────────────────────────────────────────────────── */
        .stAlert {{ border-radius: 10px !important; border: none !important; }}

        /* ── Scrollbar ───────────────────────────────────────────────────── */
        ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{ background: {c['border']}; border-radius: 3px; }}

        /* ═══════════════════════════════════════════════════════════════════
           CUSTOM COMPONENTS
        ═══════════════════════════════════════════════════════════════════ */

        /* ── Top navbar ──────────────────────────────────────────────────── */
        .fab-navbar {{
            background: {c['bg']};
            border-bottom: 1px solid {c['border']};
            padding: 0 1.75rem;
            height: 56px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 999;
            margin: -1rem -4rem 1.5rem -4rem;
        }}
        .fab-navbar-logo {{
            font-size: 1.1rem;
            font-weight: 800;
            color: {c['text']};
            letter-spacing: -0.03em;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .fab-navbar-logo .logo-accent {{ color: {c['accent']}; }}
        .fab-navbar-right {{
            display: flex;
            align-items: center;
            gap: 1.5rem;
        }}
        .fab-navbar-status {{
            display: flex;
            align-items: center;
            gap: 0.4rem;
            font-size: 0.8rem;
            color: {c['text_muted']};
            font-weight: 500;
        }}
        .status-dot {{
            width: 8px; height: 8px;
            border-radius: 50%;
            background: {c['success']};
            display: inline-block;
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50%        {{ opacity: 0.6; transform: scale(0.9); }}
        }}
        .fab-navbar-timestamp {{
            font-size: 0.78rem;
            color: {c['text_muted']};
        }}

        /* ── Metric cards ────────────────────────────────────────────────── */
        .fab-metric {{
            background: {c['bg']};
            border: 1px solid {c['border']};
            border-radius: 14px;
            padding: 1.25rem 1.5rem;
            box-shadow: 0 1px 4px rgba(0,0,0,0.04);
            transition: box-shadow 0.2s, transform 0.2s, border-color 0.2s;
            height: 100%;
            cursor: default;
        }}
        .fab-metric:hover {{
            box-shadow: 0 8px 24px rgba(0,0,0,0.09);
            transform: translateY(-2px);
            border-color: rgba(37,99,235,0.25);
        }}
        .fab-metric-icon {{ font-size: 1.4rem; margin-bottom: 0.6rem; }}
        .fab-metric-label {{
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            color: {c['text_muted']};
            margin-bottom: 0.4rem;
        }}
        .fab-metric-value {{
            font-size: 1.8rem;
            font-weight: 800;
            color: {c['text']};
            line-height: 1.1;
            margin-bottom: 0.25rem;
            letter-spacing: -0.03em;
        }}
        .fab-metric-sub {{ font-size: 0.78rem; color: {c['text_muted']}; }}

        /* ── Status / risk pills ─────────────────────────────────────────── */
        .fab-pill {{
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            padding: 0.2rem 0.75rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.01em;
        }}
        .fab-pill-normal, .fab-pill-low    {{ background: {c['success_bg']}; color: {c['success']}; }}
        .fab-pill-watch, .fab-pill-medium  {{ background: {c['warning_bg']}; color: {c['warning']}; }}
        .fab-pill-alert, .fab-pill-high, .fab-pill-critical {{ background: {c['danger_bg']}; color: {c['danger']}; }}
        .fab-pill-unknown                  {{ background: {c['surface']};  color: {c['text_muted']}; }}

        /* ── Section header ──────────────────────────────────────────────── */
        .fab-section {{
            font-size: 1rem;
            font-weight: 700;
            color: {c['text']};
            margin: 1.5rem 0 0.85rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid {c['border']};
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        /* ── Content card ────────────────────────────────────────────────── */
        .fab-card {{
            background: {c['bg']};
            border: 1px solid {c['border']};
            border-radius: 14px;
            padding: 1.5rem;
            box-shadow: 0 1px 4px rgba(0,0,0,0.04);
            transition: box-shadow 0.2s, transform 0.2s;
            margin-bottom: 0.75rem;
        }}
        .fab-card:hover {{
            box-shadow: 0 6px 20px rgba(0,0,0,0.08);
            transform: translateY(-1px);
        }}

        /* ── RCA cards ───────────────────────────────────────────────────── */
        .rca-card {{
            background: {c['bg']};
            border: 1px solid {c['border']};
            border-left: 4px solid {c['accent']};
            border-radius: 0 12px 12px 0;
            padding: 1rem 1.25rem;
            margin-bottom: 0.65rem;
            transition: box-shadow 0.2s, transform 0.2s;
        }}
        .rca-card:hover {{ box-shadow: 0 4px 16px rgba(0,0,0,0.08); transform: translateX(2px); }}
        .rca-card-high    {{ border-left-color: {c['danger']}; }}
        .rca-card-medium  {{ border-left-color: {c['warning']}; }}
        .rca-card-low     {{ border-left-color: {c['success']}; }}
        .rca-rank  {{ font-size: 1.35rem; font-weight: 800; color: {c['accent']}; }}
        .rca-name  {{ font-size: 1rem; font-weight: 700; color: {c['text']}; }}
        .rca-expl  {{ font-size: 0.82rem; color: {c['text_muted']}; margin-top: 0.3rem; }}
        .imp-bar   {{ height: 6px; background: {c['border']}; border-radius: 999px; margin-top: 0.5rem; overflow: hidden; }}
        .imp-fill  {{ height: 6px; background: linear-gradient(90deg, {c['accent']}, #7C3AED); border-radius: 999px; transition: width 0.6s ease; }}

        /* ── Maintenance action cards ─────────────────────────────────────── */
        .maint-card {{
            background: {c['bg']};
            border: 1px solid {c['border']};
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            margin-bottom: 0.75rem;
            transition: box-shadow 0.2s, transform 0.2s;
        }}
        .maint-card:hover {{ box-shadow: 0 6px 20px rgba(0,0,0,0.08); transform: translateY(-1px); }}
        .maint-high   {{ border-top: 3px solid {c['danger']}; }}
        .maint-medium {{ border-top: 3px solid {c['warning']}; }}
        .maint-low    {{ border-top: 3px solid {c['success']}; }}
        .maint-title  {{ font-size: 1.05rem; font-weight: 700; color: {c['text']}; margin-bottom: 0.25rem; }}
        .maint-sub    {{ font-size: 0.82rem; color: {c['text_muted']}; }}

        /* ── Analysis progress (analyzing page) ──────────────────────────── */
        .analysis-wrap {{
            max-width: 560px;
            margin: 0 auto;
            padding: 3rem 2rem;
            text-align: center;
        }}
        .analysis-title {{
            font-size: 1.5rem;
            font-weight: 800;
            color: {c['text']};
            margin-bottom: 0.5rem;
            letter-spacing: -0.03em;
        }}
        .analysis-sub {{
            font-size: 0.9rem;
            color: {c['text_muted']};
            margin-bottom: 2.5rem;
        }}
        .step-list {{ text-align: left; margin-top: 1.75rem; }}
        .step-row {{
            display: flex;
            align-items: center;
            gap: 0.85rem;
            padding: 0.55rem 0;
            font-size: 0.9rem;
            color: {c['text_muted']};
            transition: color 0.3s;
        }}
        .step-row.done   {{ color: {c['success']}; font-weight: 500; }}
        .step-row.active {{ color: {c['accent']};  font-weight: 600; }}
        .step-row.wait   {{ color: {c['text_light']}; }}
        .step-dot {{
            width: 22px; height: 22px;
            border-radius: 50%;
            flex-shrink: 0;
            display: flex; align-items: center; justify-content: center;
            font-size: 0.75rem;
            font-weight: 700;
        }}
        .dot-done   {{ background: {c['success_bg']}; color: {c['success']}; }}
        .dot-active {{ background: {c['accent_light']}; color: {c['accent']}; }}
        .dot-wait   {{ background: {c['surface']};  color: {c['text_light']}; }}

        /* ── Landing page ────────────────────────────────────────────────── */
        .landing-outer {{
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            min-height: 80vh;
            padding: 2rem 1rem;
        }}
        .landing-badge {{
            display: inline-block;
            background: {c['accent_light']};
            color: {c['accent']};
            font-size: 0.78rem;
            font-weight: 600;
            padding: 0.3rem 0.9rem;
            border-radius: 999px;
            border: 1px solid rgba(37,99,235,0.2);
            margin-bottom: 1.25rem;
            letter-spacing: 0.04em;
        }}
        .landing-title {{
            font-size: clamp(1.8rem, 4vw, 2.75rem);
            font-weight: 800;
            color: {c['text']};
            text-align: center;
            line-height: 1.15;
            letter-spacing: -0.04em;
            margin-bottom: 1rem;
        }}
        .landing-title .hi {{ color: {c['accent']}; }}
        .landing-sub {{
            font-size: 1.05rem;
            color: {c['text_muted']};
            text-align: center;
            line-height: 1.65;
            max-width: 560px;
            margin: 0 auto 2.5rem auto;
        }}
        .landing-trust {{
            display: flex;
            justify-content: center;
            gap: 2.5rem;
            margin-top: 1.25rem;
            flex-wrap: wrap;
        }}
        .trust-item {{
            display: flex;
            align-items: center;
            gap: 0.4rem;
            font-size: 0.82rem;
            color: {c['text_muted']};
            font-weight: 500;
        }}
        .trust-check {{ color: {c['success']}; font-size: 0.95rem; }}

        /* ── AI Report sections ──────────────────────────────────────────── */
        .report-section {{
            background: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
        }}
        .report-section-title {{
            font-size: 0.9rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: {c['text_muted']};
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }}

        /* ── Confidence bar ──────────────────────────────────────────────── */
        .conf-track {{
            background: {c['border']};
            border-radius: 999px;
            height: 8px;
            overflow: hidden;
            margin: 0.35rem 0;
        }}
        .conf-fill {{
            height: 8px;
            border-radius: 999px;
            background: linear-gradient(90deg, {c['accent']}, #7C3AED);
            transition: width 0.5s ease;
        }}

        /* ── Sidebar nav ─────────────────────────────────────────────────── */
        .nav-brand {{
            font-size: 1.05rem;
            font-weight: 800;
            color: {c['text']};
            letter-spacing: -0.03em;
            padding: 1rem 0 0.25rem 0;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }}
        .nav-brand .nb-accent {{ color: {c['accent']}; }}
        .nav-tagline {{
            font-size: 0.72rem;
            color: {c['text_muted']};
            margin-bottom: 1.25rem;
            font-weight: 400;
        }}
        .nav-section-label {{
            font-size: 0.65rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: {c['text_light']};
            padding: 0.75rem 0 0.3rem 0.25rem;
        }}
        .nav-item {{
            display: flex;
            align-items: center;
            gap: 0.65rem;
            padding: 0.6rem 0.75rem;
            border-radius: 8px;
            font-size: 0.875rem;
            font-weight: 500;
            color: {c['text_muted']};
            transition: background 0.15s, color 0.15s;
            margin-bottom: 0.1rem;
            cursor: pointer;
        }}
        .nav-item:hover  {{ background: {c['accent_light']}; color: {c['accent']}; }}
        .nav-item.active {{ background: {c['accent_light']}; color: {c['accent']}; font-weight: 600; }}
        .nav-icon {{ width: 1.2rem; text-align: center; font-size: 1rem; }}

        /* ── Empty state ─────────────────────────────────────────────────── */
        .empty-state {{
            background: {c['surface']};
            border: 1px dashed {c['border']};
            border-radius: 14px;
            padding: 3.5rem 2rem;
            text-align: center;
        }}
        .empty-icon  {{ font-size: 2.75rem; margin-bottom: 0.75rem; }}
        .empty-title {{ font-size: 1.1rem; font-weight: 700; color: {c['text']}; margin-bottom: 0.4rem; }}
        .empty-sub   {{ font-size: 0.875rem; color: {c['text_muted']}; }}

        /* ── Executive report (white version) ───────────────────────────── */
        .executive-report {{
            background: {c['bg']};
            border: 1px solid {c['border']};
            border-radius: 16px;
            padding: 1.5rem 1.75rem;
            margin: 0.5rem 0 1.5rem 0;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        }}
        .exec-divider {{
            border: none;
            border-top: 1px solid {c['border']};
            margin: 1rem 0;
        }}
        .exec-section-title {{
            font-size: 0.8rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            color: {c['text_muted']};
            margin-bottom: 0.85rem;
            margin-top: 0.5rem;
        }}
        .exec-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.45rem 0;
            border-bottom: 1px solid {c['surface']};
        }}
        .exec-label {{ color: {c['text_muted']}; font-size: 0.875rem; }}
        .exec-value {{ color: {c['text']}; font-size: 1rem; font-weight: 700; }}
        .exec-value.accent {{ color: {c['accent']}; font-size: 1.35rem; }}
        .exec-cause-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.6rem 0.85rem;
            margin: 0.35rem 0;
            background: {c['surface']};
            border-radius: 10px;
            border: 1px solid {c['border']};
            transition: background 0.15s;
        }}
        .exec-cause-row:hover {{ background: {c['accent_light']}; }}
        .exec-cause-name {{ font-size: 0.875rem; font-weight: 600; color: {c['text']}; }}
        .exec-cause-pct  {{ font-size: 0.82rem; font-weight: 700; color: {c['accent']}; }}
        .exec-check {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.875rem;
            font-weight: 500;
            color: {c['success']};
            padding: 0.3rem 0;
        }}
        .exec-check-fail {{ color: {c['danger']}; }}
        .exec-evidence-label {{
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: {c['text_muted']};
            margin-top: 0.65rem;
        }}
        .exec-evidence-value {{
            font-size: 2rem;
            font-weight: 800;
            color: {c['text']};
            letter-spacing: -0.04em;
        }}
        .exec-action {{
            display: flex;
            align-items: center;
            gap: 0.65rem;
            padding: 0.55rem 0.85rem;
            margin: 0.35rem 0;
            border-radius: 8px;
            border-left: 3px solid {c['accent']};
            font-size: 0.875rem;
            font-weight: 600;
            color: {c['text']};
            background: {c['surface']};
            transition: background 0.15s, padding-left 0.15s;
        }}
        .exec-action:hover {{ background: {c['accent_light']}; color: {c['accent']}; padding-left: 1.1rem; }}
        .exec-muted {{ color: {c['text_light']}; font-size: 0.875rem; padding: 0.5rem 0; }}

        /* ── Animations ──────────────────────────────────────────────────── */
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(16px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to   {{ opacity: 1; }}
        }}
        .animate-fadeup  {{ animation: fadeInUp 0.4s ease both; }}
        .animate-fadein  {{ animation: fadeIn 0.3s ease both; }}

        </style>
        """,
        unsafe_allow_html=True,
    )
