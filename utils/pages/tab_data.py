"""Tab 1 — Data Analysis: summary cards, interactive dataframe, statistics."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import streamlit as st

from utils.components import empty_state, page_header, render_metric_row, section_title
from utils.session import get_engine
from utils.theme import COLORS

C = COLORS


def render_tab_data(snap: dict[str, Any]) -> None:
    page_header("📊 Data Analysis", "Process parameter summary, statistics, and outlier detection")

    engine = get_engine()
    frames = engine.registry.combined_frames

    if not frames:
        empty_state("📊", "No Process Data", "Upload an Excel or CSV file to view data analysis.")
        return

    df, source = frames[0]

    # ── Dataset overview cards ─────────────────────────────────────────────
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols     = df.select_dtypes(include=["object", "string", "category"]).columns.tolist()
    date_cols    = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()

    # Lots / wafers
    lot_col = next((c for c in df.columns if "lot" in c.lower()), None)
    lot_cnt = df[lot_col].nunique() if lot_col else len(df)

    wafer_col = next((c for c in df.columns if "wafer" in c.lower()), None)
    wafer_cnt = df[wafer_col].nunique() if wafer_col else lot_cnt * 25

    # Date range
    date_range = "—"
    if date_cols:
        dc = df[date_cols[0]].dropna()
        if not dc.empty:
            date_range = f"{dc.min().date()} → {dc.max().date()}"

    # Equipment
    equip_col = next((c for c in df.columns if "equip" in c.lower() or "tool" in c.lower()), None)
    equip_val = df[equip_col].nunique() if equip_col else "—"
    if equip_val != "—":
        equip_val = f"{equip_val} tools"

    render_metric_row([
        ("📦", "Total Lots",        str(lot_cnt),        f"Unique lot IDs"),
        ("🟠", "Wafers (est.)",     str(wafer_cnt),      "Estimated from lots"),
        ("🔢", "Parameters",        str(len(numeric_cols)), f"{len(cat_cols)} categorical"),
        ("📅", "Date Range",        date_range[:16] if date_range != "—" else "—", ""),
        ("⚙️", "Equipment",         str(equip_val),      ""),
        ("⚠️", "Drift Signals",     str(len(snap.get("drifts", []))), "Detected anomalies"),
    ])

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Interactive dataframe ──────────────────────────────────────────────
    section_title("📋", "Process Data Preview")
    display_df = df.copy()
    for col in date_cols:
        display_df[col] = display_df[col].astype(str)

    st.dataframe(
        display_df.head(200),
        use_container_width=True,
        height=320,
    )
    st.caption(f"Showing up to 200 rows from **{source}** ({len(df)} total rows)")

    # ── Statistics ─────────────────────────────────────────────────────────
    col_left, col_right = st.columns(2)

    with col_left:
        section_title("📐", "Descriptive Statistics")
        if numeric_cols:
            st.dataframe(
                df[numeric_cols].describe().round(3),
                use_container_width=True,
                height=260,
            )
        else:
            st.info("No numeric columns found.")

    with col_right:
        section_title("🚫", "Missing Values")
        null_counts = df.isnull().sum()
        null_pct    = (df.isnull().mean() * 100).round(1)
        null_df = pd.DataFrame({
            "Column":  null_counts.index,
            "Missing": null_counts.values,
            "% Missing": null_pct.values,
        })
        null_df = null_df[null_df["Missing"] > 0].reset_index(drop=True)
        if null_df.empty:
            st.success("✅ No missing values detected.")
        else:
            st.dataframe(null_df, use_container_width=True, height=260)

    # ── Outlier / drift summary ────────────────────────────────────────────
    drifts = snap.get("drifts", [])
    if drifts:
        section_title("⚠️", "Detected Outliers & Drift")
        sev_color = {"critical": C["danger"], "high": C["danger"], "medium": C["warning"], "low": C["success"]}
        for d in drifts:
            sev   = d.get("severity", "medium")
            color = sev_color.get(sev, C["text_muted"])
            drift = d.get("drift_pct")
            drift_str = f" | Drift: {drift:+.1f}%" if drift is not None else ""
            st.markdown(
                f"""
                <div style="
                    background:{C['bg']};
                    border:1px solid {C['border']};
                    border-left:4px solid {color};
                    border-radius:0 10px 10px 0;
                    padding:0.75rem 1rem;
                    margin-bottom:0.5rem;
                ">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            <span style="font-size:0.85rem;font-weight:700;color:{C['text']};">{d.get('category','Drift')}</span>
                            <span style="font-size:0.78rem;color:{C['text_muted']};"> — {d.get('parameter','')}</span>
                        </div>
                        <span style="background:{color}20;color:{color};font-size:0.75rem;font-weight:700;padding:0.15rem 0.6rem;border-radius:999px;">{sev.upper()}{drift_str}</span>
                    </div>
                    <div style="font-size:0.78rem;color:{C['text_muted']};margin-top:0.35rem;">{d.get('message','')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
