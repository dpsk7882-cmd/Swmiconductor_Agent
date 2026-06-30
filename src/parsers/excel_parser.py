from io import BytesIO

import pandas as pd


class ExcelParser:
    """Load and summarize Excel workbooks for analysis."""

    def parse(self, file_bytes: bytes, filename: str = "data.xlsx") -> dict:
        workbook = pd.read_excel(BytesIO(file_bytes), sheet_name=None, engine="openpyxl")

        sheets: dict[str, dict] = {}
        dataframes: dict[str, pd.DataFrame] = {}
        for sheet_name, dataframe in workbook.items():
            dataframes[sheet_name] = dataframe
            sheets[sheet_name] = self._summarize_sheet(dataframe)

        primary_sheet = next(iter(workbook.keys()))

        return {
            "filename": filename,
            "sheet_names": list(workbook.keys()),
            "primary_sheet": primary_sheet,
            "dataframe": dataframes[primary_sheet],
            "dataframes": dataframes,
            "sheets": sheets,
        }

    def _summarize_sheet(self, df: pd.DataFrame) -> dict:
        preview_rows = min(len(df), 100)
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        categorical_cols = df.select_dtypes(include=["object", "string", "category"]).columns.tolist()

        describe_text = ""
        if numeric_cols:
            describe_text = df[numeric_cols].describe().to_string()

        return {
            "rows": len(df),
            "columns": list(df.columns),
            "numeric_columns": numeric_cols,
            "categorical_columns": categorical_cols,
            "preview": df.head(preview_rows),
            "describe": describe_text,
            "null_counts": df.isnull().sum().to_dict(),
        }

    @staticmethod
    def to_context_block(parsed: dict) -> str:
        lines = [
            f"--- Excel Workbook: {parsed['filename']} ---",
            f"Sheets: {', '.join(parsed['sheet_names'])}",
            f"Primary sheet for charts: {parsed['primary_sheet']}",
        ]

        for sheet_name, summary in parsed["sheets"].items():
            lines.append(f"\n[Sheet: {sheet_name}]")
            lines.append(f"Rows: {summary['rows']}, Columns: {summary['columns']}")
            lines.append(f"Numeric columns: {summary['numeric_columns']}")
            lines.append(f"Categorical columns: {summary['categorical_columns']}")

            if summary["describe"]:
                lines.append("\nNumeric summary statistics:")
                lines.append(summary["describe"])

            nulls = {k: v for k, v in summary["null_counts"].items() if v > 0}
            if nulls:
                lines.append(f"\nNull counts: {nulls}")

            lines.append("\nPreview (first rows):")
            lines.append(summary["preview"].to_string(index=False))

        lines.append("--- End Excel ---")
        return "\n".join(lines)
