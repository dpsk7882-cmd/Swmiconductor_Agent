"""Navigation configuration for the industrial platform."""

from __future__ import annotations

NAV_ITEMS: list[tuple[str, str, str]] = [
    ("dashboard", "🏠", "Dashboard"),
    ("assistant", "💬", "AI Assistant"),
    ("pdf_kb", "📄", "PDF Knowledge Base"),
    ("data_analysis", "📊", "Data Analysis"),
    ("yield_prediction", "📈", "Yield Prediction"),
    ("rca", "🔍", "Root Cause Analysis"),
    ("risk", "⚠", "Process Risk Assessment"),
    ("actions", "🛠", "Recommended Actions"),
    ("settings", "⚙", "Settings"),
]

PAGE_TITLES: dict[str, tuple[str, str]] = {
    "dashboard": ("Operations Dashboard", "Real-time process intelligence for fab engineering"),
    "assistant": ("AI Assistant", "Engineering copilot with verified platform context"),
    "pdf_kb": ("PDF Knowledge Base", "Manuals, SOPs, and recipe documentation"),
    "data_analysis": ("Data Analysis", "Process parameter drift and abnormality detection"),
    "yield_prediction": ("Yield Prediction", "ML-powered yield and failure forecasting"),
    "rca": ("Root Cause Analysis", "Ranked yield degradation root causes"),
    "risk": ("Process Risk Assessment", "Stability, yield, and equipment risk scoring"),
    "actions": ("Recommended Actions", "Prioritized preventive maintenance"),
    "settings": ("Settings", "Platform configuration and agent pipeline"),
}
