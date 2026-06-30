"""Application configuration."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

APP_TITLE = "FabSense AI"
APP_ICON = "⚗️"
APP_TAGLINE = "Industrial decision-support for semiconductor process engineering"

# Legacy chat constants (used by utils/ui.py)
CHAT_INPUT_PLACEHOLDER = (
    "Ask about process conditions, drifts, yield, root cause, or maintenance..."
)
WELCOME_MESSAGE = (
    "Welcome to **FabSense AI**. Upload process data in the sidebar, "
    "run analysis from the Dashboard, then explore dedicated analysis pages."
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
