import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def build_excel_charts(dataframe: pd.DataFrame, sheet_name: str = "Sheet1") -> list[dict]:
    """Generate Plotly figures from numeric and categorical columns."""
    charts: list[dict] = []
    numeric_cols = dataframe.select_dtypes(include="number").columns.tolist()
    categorical_cols = dataframe.select_dtypes(include=["object", "string", "category"]).columns.tolist()

    if not numeric_cols:
        return charts

    # Histogram for each numeric column
    for col in numeric_cols[:4]:
        fig = px.histogram(
            dataframe,
            x=col,
            nbins=30,
            title=f"Distribution: {col}",
            color_discrete_sequence=["#2563eb"],
        )
        _apply_chart_theme(fig)
        charts.append({"title": f"Histogram — {col}", "figure": fig})

    # Correlation heatmap when multiple numeric columns exist
    if len(numeric_cols) >= 2:
        corr = dataframe[numeric_cols].corr()
        fig = go.Figure(
            data=go.Heatmap(
                z=corr.values,
                x=corr.columns,
                y=corr.columns,
                colorscale="Blues",
                zmin=-1,
                zmax=1,
            )
        )
        fig.update_layout(title=f"Correlation Matrix — {sheet_name}")
        _apply_chart_theme(fig)
        charts.append({"title": "Correlation Matrix", "figure": fig})

    # Bar chart: categorical vs first numeric column
    if categorical_cols and numeric_cols:
        cat_col = categorical_cols[0]
        num_col = numeric_cols[0]
        grouped = (
            dataframe.groupby(cat_col, dropna=False)[num_col]
            .mean()
            .reset_index()
            .sort_values(num_col, ascending=False)
            .head(15)
        )
        fig = px.bar(
            grouped,
            x=cat_col,
            y=num_col,
            title=f"Average {num_col} by {cat_col}",
            color_discrete_sequence=["#7c3aed"],
        )
        fig.update_layout(xaxis_tickangle=-45)
        _apply_chart_theme(fig)
        charts.append({"title": f"Avg {num_col} by {cat_col}", "figure": fig})

    # Line chart when an index-like or date column exists
    datetime_cols = dataframe.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()
    if datetime_cols and numeric_cols:
        date_col = datetime_cols[0]
        num_col = numeric_cols[0]
        sorted_df = dataframe.sort_values(date_col).dropna(subset=[date_col, num_col])
        if not sorted_df.empty:
            fig = px.line(
                sorted_df,
                x=date_col,
                y=num_col,
                title=f"{num_col} over {date_col}",
                color_discrete_sequence=["#059669"],
            )
            _apply_chart_theme(fig)
            charts.append({"title": f"Trend — {num_col}", "figure": fig})

    return charts


def _apply_chart_theme(fig: go.Figure) -> None:
    fig.update_layout(
        template="plotly_white",
        font=dict(family="Inter, Segoe UI, sans-serif", size=13),
        margin=dict(l=40, r=40, t=60, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
