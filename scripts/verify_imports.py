"""Verify all project modules import without ImportError."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODULES = [
    "app",
    "agents",
    "agents.analysis_agent",
    "agents.platform_engine",
    "agents.planner",
    "agents.reviewer_agent",
    "agents.orchestrator",
    "models",
    "models.platform_snapshot",
    "models.prediction_model",
    "models.risk_model",
    "models.root_cause_model",
    "tools.registry",
    "tools.drift_detector",
    "tools.file_router",
    "utils.session",
    "utils.uploads",
    "utils.data_sync",
    "utils.ui",
    "utils.pages",
    "utils.pages.dashboard",
    "utils.executive_report",
    "scripts.generate_sample_data",
]


def main() -> int:
    sys.path.insert(0, str(PROJECT_ROOT))
    failed: list[str] = []

    for name in MODULES:
        try:
            importlib.import_module(name)
            print(f"OK   {name}")
        except Exception as exc:
            print(f"FAIL {name}: {exc}")
            failed.append(name)

    if failed:
        print(f"\n{len(failed)} module(s) failed.")
        return 1
    print(f"\nAll {len(MODULES)} modules imported successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
