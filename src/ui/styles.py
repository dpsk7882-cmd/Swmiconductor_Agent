import streamlit as st


def inject_custom_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .main-header {
            background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #2563eb 100%);
            padding: 1.75rem 2rem;
            border-radius: 16px;
            margin-bottom: 1.5rem;
            color: white;
            box-shadow: 0 10px 40px rgba(37, 99, 235, 0.25);
        }

        .main-header h1 {
            font-size: 1.75rem;
            font-weight: 700;
            margin: 0 0 0.35rem 0;
            color: white !important;
        }

        .main-header p {
            margin: 0;
            opacity: 0.9;
            font-size: 0.95rem;
        }

        .stat-card {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1rem 1.25rem;
            margin-bottom: 0.75rem;
        }

        .stat-card strong {
            color: #0f172a;
            display: block;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 0.25rem;
        }

        .stat-card span {
            color: #475569;
            font-size: 0.9rem;
        }

        div[data-testid="stChatMessage"] {
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            padding: 0.5rem;
            margin-bottom: 0.5rem;
        }

        section[data-testid="stSidebar"] {
            background: #f8fafc;
        }

        section[data-testid="stSidebar"] .stMarkdown h2 {
            font-size: 1rem;
            color: #0f172a;
        }

        .upload-badge {
            display: inline-block;
            background: #dbeafe;
            color: #1d4ed8;
            padding: 0.2rem 0.6rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-right: 0.35rem;
        }

        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        """
        <div class="main-header">
            <h1>Semiconductor Process AI Agent</h1>
            <p>Ask process questions, analyze PDFs, and visualize Excel fab data.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stat_card(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="stat-card">
            <strong>{label}</strong>
            <span>{value}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
