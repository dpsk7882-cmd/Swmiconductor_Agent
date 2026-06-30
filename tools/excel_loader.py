"""Excel process data loader and summarizer."""

from __future__ import annotations

from io import BytesIO
from typing import Any

import pandas as pd


class ExcelLoader:
    """Load and summarize semiconductor process Excel workbooks."""

    def load(self, file_bytes: bytes, filename: str = "process_data.xlsx") -> dict[str, Any]:
        workbook = pd.read_excel(BytesIO(file_bytes), sheet_name=None, engine="openpyxl")

        dataframes: dict[str, pd.DataFrame] = {}
        summaries: dict[str, dict[str, Any]] = {}

        for sheet_name, df in workbook.items():
            df = self._normalize_dataframe(df)
            dataframes[sheet_name] = df
            summaries[sheet_name] = self._summarize(df)

        primary = next(iter(workbook.keys()))
        return {
            "filename": filename,
            "sheet_names": list(workbook.keys()),
            "primary_sheet": primary,
            "dataframe": dataframes[primary],
            "dataframes": dataframes,
            "summaries": summaries,
        }

    def _normalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Coerce date columns and clean column names."""
        df = df.copy()
        df.columns = [str(c).strip() for c in df.columns]

        for col in df.columns:
            if df[col].dtype == object:
                parsed = pd.to_datetime(df[col], errors="coerce", utc=False)
                if parsed.notna().sum() >= len(df) * 0.5:
                    df[col] = parsed
        return df

    def _summarize(self, df: pd.DataFrame) -> dict[str, Any]:
        numeric = df.select_dtypes(include="number").columns.tolist()
        categorical = df.select_dtypes(include=["object", "string", "category"]).columns.tolist()
        datetime_cols = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()

        column_stats: dict[str, dict[str, float]] = {}
        for col in numeric:
            series = df[col].dropna()
            if series.empty:
                continue
            column_stats[col] = {
                "min": float(series.min()),
                "max": float(series.max()),
                "mean": float(series.mean()),
                "std": float(series.std()) if len(series) > 1 else 0.0,
            }

        return {
            "rows": len(df),
            "columns": list(df.columns),
            "numeric_columns": numeric,
            "categorical_columns": categorical,
            "datetime_columns": datetime_cols,
            "column_stats": column_stats,
            "null_counts": {k: int(v) for k, v in df.isnull().sum().items() if v > 0},
            "preview": df.head(5),
        }

    @staticmethod
    def to_context_block(parsed: dict[str, Any]) -> str:
        lines = [
            f"Excel: {parsed['filename']}",
            f"Sheets: {', '.join(parsed['sheet_names'])}",
            f"Primary: {parsed['primary_sheet']}",
        ]
        for sheet, summary in parsed["summaries"].items():
            lines.append(f"\n[{sheet}] rows={summary['rows']}, numeric={summary['numeric_columns']}")
        return "\n".join(lines)
