"""Equipment log file loader (.csv, .txt)."""

from __future__ import annotations

from io import BytesIO, StringIO
from typing import Any

import pandas as pd


class LogLoader:
    """Parse equipment log files in CSV or delimited text format."""

    def load(self, file_bytes: bytes, filename: str) -> dict[str, Any]:
        text = file_bytes.decode("utf-8", errors="replace")
        ext = filename.rsplit(".", 1)[-1].lower()

        if ext == "csv":
            df = pd.read_csv(StringIO(text))
        else:
            df = self._parse_delimited_text(text)

        df = self._normalize(df)
        return {
            "filename": filename,
            "rows": len(df),
            "columns": list(df.columns),
            "dataframe": df,
            "summary": self._summarize(df),
        }

    def _parse_delimited_text(self, text: str) -> pd.DataFrame:
        """Try common delimiters for fab equipment logs."""
        for sep in (",", "\t", "|", ";"):
            try:
                df = pd.read_csv(StringIO(text), sep=sep)
                if len(df.columns) > 1:
                    return df
            except Exception:
                continue
        # Fallback: treat each line as a raw log entry
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        return pd.DataFrame({"log_line": lines})

    def _normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df.columns = [str(c).strip() for c in df.columns]
        for col in df.columns:
            if df[col].dtype == object:
                parsed = pd.to_datetime(df[col], errors="coerce")
                if parsed.notna().sum() >= len(df) * 0.4:
                    df[col] = parsed
        return df

    def _summarize(self, df: pd.DataFrame) -> dict[str, Any]:
        numeric = df.select_dtypes(include="number").columns.tolist()
        stats: dict[str, dict[str, float]] = {}
        for col in numeric:
            s = df[col].dropna()
            if s.empty:
                continue
            stats[col] = {
                "min": float(s.min()),
                "max": float(s.max()),
                "mean": float(s.mean()),
                "std": float(s.std()) if len(s) > 1 else 0.0,
            }
        return {"numeric_columns": numeric, "column_stats": stats, "rows": len(df)}
