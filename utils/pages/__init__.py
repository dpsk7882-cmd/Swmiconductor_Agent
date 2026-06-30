"""Page renderers for the Semiconductor AI Platform.

Imports are lazy to avoid circular dependencies and speed up startup.
All renderers are re-exported here for backward compatibility.
"""

from __future__ import annotations

# ── Primary flow (new white UI) ───────────────────────────────────────────────
from utils.pages.landing        import render_landing_page
from utils.pages.analyzing      import render_analyzing_page
from utils.pages.main_dashboard import render_main_dashboard

# ── Tab renderers ─────────────────────────────────────────────────────────────
from utils.pages.tab_data           import render_tab_data
from utils.pages.tab_yield_loss     import render_tab_yield_loss
from utils.pages.tab_prediction     import render_tab_prediction
from utils.pages.tab_maintenance    import render_tab_maintenance
from utils.pages.tab_visualization  import render_tab_visualization
from utils.pages.tab_ai_report      import render_tab_ai_report

# ── Legacy page renderers (kept for backward compatibility) ───────────────────
from utils.pages.actions          import render_actions_page
from utils.pages.assistant        import render_assistant_page
from utils.pages.dashboard        import render_dashboard_page
from utils.pages.data_analysis    import render_data_analysis_page
from utils.pages.pdf_kb           import render_pdf_kb_page
from utils.pages.rca              import render_rca_page
from utils.pages.risk             import render_risk_page
from utils.pages.settings         import render_settings_page
from utils.pages.yield_prediction import render_yield_prediction_page

__all__ = [
    "render_landing_page",
    "render_analyzing_page",
    "render_main_dashboard",
    "render_tab_data",
    "render_tab_yield_loss",
    "render_tab_prediction",
    "render_tab_maintenance",
    "render_tab_visualization",
    "render_tab_ai_report",
    "render_actions_page",
    "render_assistant_page",
    "render_dashboard_page",
    "render_data_analysis_page",
    "render_pdf_kb_page",
    "render_rca_page",
    "render_risk_page",
    "render_settings_page",
    "render_yield_prediction_page",
]
