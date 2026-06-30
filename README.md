# FabSense AI

**Industrial AI decision-support platform** for semiconductor process monitoring, yield analysis, and predictive maintenance.

Built for fab engineers — not a chatbot. A structured intelligence platform with verified analysis, risk scoring, and explainable predictions.

![Platform](https://img.shields.io/badge/Python-3.10+-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red)

## Platform Pages

| Page | Purpose |
|------|---------|
| 🏠 **Dashboard** | Operations overview — status, yield, risk, confidence |
| 💬 **AI Assistant** | Secondary engineering copilot (grounded in platform data) |
| 📄 **PDF Knowledge Base** | Manual/SOP search via RAG |
| 📊 **Data Analysis** | Drift detection charts & abnormality signals |
| 📈 **Yield Prediction** | ML yield forecast & failure probability |
| 🔍 **Root Cause Analysis** | Ranked RCA with explanations |
| ⚠ **Process Risk Assessment** | Stability, yield, equipment risk scoring |
| 🛠 **Recommended Actions** | Prioritized PM (chamber clean, ESC, MFC, etc.) |
| ⚙ **Settings** | Agent pipeline & model configuration |

## Architecture

```
agents/
  analysis_agent.py    # Agent 1 — analyzes data, generates conclusions
  reviewer_agent.py    # Agent 2 — verifies evidence, assigns confidence
  planner_agent.py     # Routes assistant queries
  platform_engine.py   # Orchestrates the full pipeline

tools/
  drift_detector.py    # Pressure/temp/RF/gas/particle/ARC/High-Z drifts
  file_router.py       # Auto file type detection
  pdf_rag.py           # PDF knowledge base
  excel_loader.py      # Excel process data
  log_loader.py        # CSV/TXT equipment logs

models/
  platform_snapshot.py # Dashboard state schema
  prediction_model.py  # Pluggable ML yield model (swap via registry)
  risk_model.py        # Process/yield/equipment risk scoring
  root_cause_model.py  # RCA ranking model

utils/
  theme.py             # Industrial dark UI theme
  components.py        # Metric cards, risk pills, confidence bars
  pages/               # One module per platform page
  sidebar.py           # Navigation & unified upload
```

## Dual-Agent Verification

1. **Analysis Agent** — runs drift detection, yield analysis, ML prediction, RCA, PM recommendations
2. **Reviewer Agent** — checks evidence consistency, detects contradictions, assigns confidence (0–100%), requests more data when insufficient

Every response includes:
- Original analysis (Agent 1)
- Reviewed analysis (Agent 2)
- Evidence list
- Important variables
- Reasoning chain
- Confidence score + explanation

## Setup

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
python scripts/generate_sample_data.py
streamlit run app.py
```

Optional — set `OPENAI_API_KEY` in `.env` for enhanced AI Assistant narratives. All analytics work without it.

## Quick Demo

1. Start the app → open **Dashboard**
2. Upload `data/sample_process_data.xlsx` via sidebar
3. Upload `data/sample_equipment_log.txt`
4. Click **Run Full Platform Analysis**
5. Explore **Data Analysis**, **Yield Prediction**, **RCA**, **Risk**, **Actions**

## Drift Detection

Automatically detects:
- Pressure Drift
- Temperature Drift
- RF Power Drift
- Gas Flow Abnormality
- Particle Increase
- ARC Count Increase
- High-Z Events
- Equipment Instability

## ML Models (Swappable)

Replace models via `models/prediction_model.py`:

```python
from models.prediction_model import PREDICTION_MODELS, get_prediction_model

model = get_prediction_model("ensemble")  # default
result = model.predict(dataframe)
```

Register custom models in `PREDICTION_MODELS` dict.

## License

MIT
