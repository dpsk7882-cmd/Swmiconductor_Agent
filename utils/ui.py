"""UI helpers: custom styling, dashboard layout, and page renderers."""

from __future__ import annotations

import streamlit as st

from models.upload import UploadedFileRecord
from utils.charts import build_health_gauge, build_process_charts
from utils.config import (
    APP_TAGLINE,
    APP_TITLE,
    CHAT_INPUT_PLACEHOLDER,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    WELCOME_MESSAGE,
)
from utils.data_sync import sync_registry
from utils.session import (
    append_message,
    clear_messages,
    get_engine,
    get_last_analysis,
    get_messages,
    get_orchestrator,
    run_platform_analysis,
)
from utils.uploads import (
    UPLOADERS,
    clear_uploads,
    get_uploads,
    get_uploads_by_type,
    register_upload,
    remove_upload,
)


def inject_custom_css() -> None:
    """Inject global CSS for a modern industrial dashboard."""
    st.markdown(
        """
        <style>
            .app-header { padding: 0.25rem 0 0.75rem 0; }
            .app-header h1 {
                font-size: 1.75rem; font-weight: 700;
                margin-bottom: 0.15rem; letter-spacing: -0.02em;
            }
            .app-header p { color: #64748b; font-size: 0.95rem; margin: 0; }
            .sidebar-brand { font-size: 1.05rem; font-weight: 600; margin-bottom: 0.15rem; }
            .sidebar-caption { color: #94a3b8; font-size: 0.82rem; margin-bottom: 0.75rem; }
            .metric-grid {
                display: grid; grid-template-columns: repeat(4, 1fr);
                gap: 0.75rem; margin-bottom: 1.25rem;
            }
            .metric-card {
                background: #ffffff; border: 1px solid #e2e8f0;
                border-radius: 12px; padding: 1rem 1.1rem;
                box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
            }
            .metric-card .label {
                color: #64748b; font-size: 0.78rem; font-weight: 500;
                text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 0.35rem;
            }
            .metric-card .value {
                color: #0f172a; font-size: 1.5rem; font-weight: 700; line-height: 1.2;
            }
            .chat-panel {
                background: #ffffff; border: 1px solid #e2e8f0;
                border-radius: 14px; padding: 1rem 1.25rem 0.5rem;
                min-height: 420px; box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
            }
            .chat-panel-title {
                font-size: 1rem; font-weight: 600; color: #0f172a;
                margin-bottom: 0.75rem; padding-bottom: 0.65rem;
                border-bottom: 1px solid #f1f5f9;
            }
            .welcome-card {
                background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
                border: 1px solid #bfdbfe; border-radius: 10px;
                padding: 1rem 1.15rem; margin-bottom: 0.75rem;
                color: #1e3a5f; font-size: 0.92rem; line-height: 1.55;
            }
            .confidence-bar {
                background: #f1f5f9; border-radius: 8px; height: 8px; margin: 0.5rem 0;
            }
            .confidence-fill {
                height: 8px; border-radius: 8px;
                background: linear-gradient(90deg, #3b82f6, #6366f1);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        f'<div class="app-header"><h1>{APP_TITLE}</h1><p>{APP_TAGLINE}</p></div>',
        unsafe_allow_html=True,
    )


def render_dashboard_metrics() -> None:
    uploads = get_uploads()
    messages = get_messages()
    analysis = get_last_analysis()

    health = analysis.get("process_status", "—") if analysis else "—"
    conf_val = (analysis.get("explainability") or {}).get("confidence_score", 0) if analysis else 0
    confidence = f"{conf_val:.0f}%" if analysis else "—"

    st.markdown(
        f"""
        <div class="metric-grid">
            <div class="metric-card">
                <div class="label">Process Health</div>
                <div class="value">{health.upper() if health != "—" else "—"}</div>
            </div>
            <div class="metric-card">
                <div class="label">Confidence</div>
                <div class="value">{confidence}</div>
            </div>
            <div class="metric-card">
                <div class="label">Files Loaded</div>
                <div class="value">{len(uploads)}</div>
            </div>
            <div class="metric-card">
                <div class="label">Messages</div>
                <div class="value">{len(messages)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_branding() -> None:
    st.markdown('<p class="sidebar-brand">Semiconductor Agent</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sidebar-caption">Process analysis · RAG · RCA · Forecasting</p>',
        unsafe_allow_html=True,
    )


def render_sidebar_navigation(pages: tuple[str, ...]) -> str:
    st.markdown("### Navigation")
    selected = st.radio("Go to", pages, label_visibility="collapsed", key="nav_radio")
    st.session_state.current_page = selected
    return selected


def render_sidebar_uploads() -> None:
    st.divider()
    st.markdown("### Upload Data")

    for file_type, config in UPLOADERS.items():
        icon = config["icon"]
        label = config["label"]
        types = config["types"]

        uploaded = st.file_uploader(
            f"{icon} {label}",
            type=types,
            key=f"uploader_{file_type}",
            help=f"Upload {label.lower()} for analysis.",
        )

        if uploaded is not None:
            already = any(
                r["file_type"] == file_type and r["filename"] == uploaded.name
                for r in get_uploads()
            )
            record = register_upload(uploaded, file_type)
            st.session_state.registry_initialized = False
            if not already:
                st.success(f"Loaded: {record['filename']}")


def render_sidebar_upload_list() -> None:
    uploads = get_uploads()
    if not uploads:
        st.caption("No files uploaded yet.")
        return

    st.divider()
    st.markdown("### Loaded Files")

    for raw in uploads:
        # Support both legacy (file_type) and current (file_kind) upload records
        if "file_type" not in raw and "file_kind" in raw:
            raw = {**raw, "file_type": raw["file_kind"]}
        record = UploadedFileRecord(**raw)
        icon = UPLOADERS.get(record.file_type, {}).get("icon", "📄")
        with st.container(border=True):
            st.markdown(f"**{icon} {record.filename}**")
            st.caption(f"{record.file_type.upper()} · {record.size_label}")
            if st.button("Remove", key=f"remove_{record.upload_id}", use_container_width=True):
                remove_upload(record.upload_id)
                st.rerun()


def render_sidebar_actions() -> None:
    st.divider()
    st.markdown("### Actions")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear chat", use_container_width=True):
            clear_messages()
            st.rerun()
    with col2:
        if st.button("Clear files", use_container_width=True):
            clear_uploads()
            get_orchestrator().registry.clear()
            st.rerun()

    st.markdown("##### Quick Analysis")
    quick_prompts = [
        "Analyze current process health",
        "Root cause of yield degradation",
        "Forecast yield trend",
        "Recommend preventive maintenance",
    ]
    for qp in quick_prompts:
        if st.button(qp, key=f"quick_{qp[:20]}", use_container_width=True):
            st.session_state.pending_prompt = qp
            st.rerun()


def _run_agent(prompt: str) -> None:
    """Execute platform analysis and assistant reply (legacy chat UI)."""
    from utils.uploads import get_filenames

    sync_registry()
    run_platform_analysis(get_filenames())
    engine = get_engine()
    history = [m for m in get_messages() if m["role"] in ("user", "assistant")]

    with st.spinner("Running analysis pipeline (Analysis Agent → Reviewer Agent)..."):
        reply = engine.query_assistant(prompt, snapshot_dict=get_last_analysis(), history=history)

    append_message("assistant", reply)


def render_chat_panel() -> None:
    messages = get_messages()

    st.markdown(
        '<div class="chat-panel"><div class="chat-panel-title">AI Process Analysis Chat</div></div>',
        unsafe_allow_html=True,
    )

    if not messages:
        st.markdown(f'<div class="welcome-card">{WELCOME_MESSAGE}</div>', unsafe_allow_html=True)

    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle quick-action prompts from sidebar
    prompt = st.session_state.pop("pending_prompt", None)
    if prompt:
        append_message("user", prompt)
        _run_agent(prompt)
        st.rerun()

    prompt = st.chat_input(CHAT_INPUT_PLACEHOLDER)
    if prompt:
        append_message("user", prompt)
        _run_agent(prompt)
        st.rerun()


def render_analysis_summary() -> None:
    """Compact summary card below chat when analysis exists."""
    analysis = get_last_analysis()
    if not analysis:
        return

    st.divider()
    col1, col2 = st.columns([1, 2])
    with col1:
        status = analysis.get("process_status", "Unknown")
        conf = (analysis.get("explainability") or {}).get("confidence_score", 0)
        fig = build_health_gauge(status.lower(), conf)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        risk = analysis.get("risk") or {}
        st.markdown(f"**Status:** {analysis.get('process_status', '')}")
        st.markdown(f"**Risk:** {risk.get('risk_level', '—')} ({risk.get('risk_score', 0)}/100)")
        st.markdown(f"**Confidence:** {conf:.0f}%")
        st.progress(min(conf / 100, 1.0))
        expl = analysis.get("explainability") or {}
        st.caption(expl.get("confidence_explanation", ""))


def render_chat_page() -> None:
    render_dashboard_metrics()
    render_chat_panel()
    render_analysis_summary()


def render_dashboard_page() -> None:
    """Interactive charts and analysis dashboard."""
    st.markdown("### Process Dashboard")
    sync_registry()
    registry = get_orchestrator().registry
    analysis = get_last_analysis()

    if not registry.combined_frames:
        st.info("Upload Excel process data or equipment logs to view interactive charts.")
        return

    df, source = registry.combined_frames[0]
    st.caption(f"Primary dataset: **{source}** ({len(df)} rows)")

    forecast_df = None
    anomalies = analysis.get("drifts", []) if analysis else []
    if registry.combined_frames:
        forecast_df = registry.forecaster.forecast_series(registry.combined_frames[0][0])

    charts = build_process_charts(df, sheet_name=source, forecast_df=forecast_df, anomalies=anomalies)

    if not charts:
        st.warning("No numeric columns found for charting.")
        return

    # Display charts in a 2-column grid
    for i in range(0, len(charts), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(charts):
                with col:
                    st.plotly_chart(charts[idx]["figure"], use_container_width=True)

    if analysis:
        st.divider()
        st.markdown("#### Latest Analysis Snapshot")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Drift Signals", len(analysis.get("drifts", [])))
        with c2:
            st.metric("Yield Factors", len(analysis.get("yield_factors", [])))
        with c3:
            pred = analysis.get("predicted_yield")
            st.metric("Predicted Yield", f"{pred}%" if pred else "N/A")


def render_settings_page() -> None:
    st.markdown("### Settings")
    llm_configured = bool(OPENAI_API_KEY and OPENAI_API_KEY != "sk-your-key-here")

    st.markdown(
        f"""
        **LLM Status:** {'✅ Configured' if llm_configured else '⚪ Not configured (template responses active)'}

        Set `OPENAI_API_KEY` in a `.env` file for enhanced narrative generation.
        All analysis tools work without an API key.
        """
    )
    st.text_input("OpenAI Model", value=OPENAI_MODEL, disabled=True)
    st.markdown("---")
    st.markdown("**Agent Pipeline**")
    st.markdown(
        """
        1. **Planner Agent** — selects tools based on query intent
        2. **Tool Execution** — anomaly detection, yield analysis, RCA, forecasting, PM
        3. **Rule Engine** — validates against semiconductor process knowledge
        4. **Reviewer Agent** — verifies reasoning and assigns confidence score
        """
    )


def render_about_page() -> None:
    st.markdown("### About")
    st.markdown(
        """
        **Semiconductor AI Agent** — industrial-grade process analysis assistant.

        | Capability | Description |
        |------------|-------------|
        | PDF RAG | Upload manuals, ask document-based questions |
        | Excel Analysis | Process parameter anomaly & yield analysis |
        | Log Analysis | Equipment log parsing (.csv, .txt) |
        | RCA | Ranked root-cause hypotheses with evidence |
        | Forecasting | Yield trend prediction (exp. smoothing / linear) |
        | PM Advisor | Preventive maintenance recommendations |
        | Confidence | 0–100% score with reviewer explanation |

        **Architecture**

        | Folder | Purpose |
        |--------|---------|
        | `agents/` | Planner, Reviewer, Orchestrator |
        | `tools/` | RAG, loaders, analyzers, forecaster |
        | `models/` | Data schemas, process rules |
        | `utils/` | UI, session, charts, LLM client |
        """
    )


def render_sidebar_branding_and_nav(pages: tuple[str, ...]) -> str:
    render_sidebar_branding()
    return render_sidebar_navigation(pages)
