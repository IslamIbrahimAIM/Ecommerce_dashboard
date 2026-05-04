"""Univariate analysis tab — distribution + box plots for any metric, sliced by category or brand."""
from __future__ import annotations

import plotly.express as px
import streamlit as st

from charts.palettes import CHART_CONFIG, PRIMARY
from charts.port import ChartPort
from data.repository import DATE, DataRepository
from infra.config import AppConfig

METRICS = ["Sales", "Orders", "Sessions", "Cart", "Views", "Buyers"]
DIMENSIONS = ["category", "brand"]


def render(repo: DataRepository, charts: ChartPort, _: AppConfig) -> None:
    st.title("Univariate Analysis")

    range_min, range_max = repo.date_range()
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
    with c1:
        start = st.date_input("Start", range_min, min_value=range_min, max_value=range_max, key="uv-start")
    with c2:
        end = st.date_input("End", range_max, min_value=range_min, max_value=range_max, key="uv-end")
    with c3:
        metric = st.selectbox("Metric", METRICS, index=0)
    with c4:
        dimension = st.selectbox("Group by", DIMENSIONS, index=0)

    if dimension == "category":
        df = repo.daily_by_category(start, end)
    else:
        df = repo.daily_by_brand(start, end)

    if df.empty:
        st.info("No data in the selected range.")
        return

    # Roll up to dimension × date so each "observation" is one day per dim value.
    daily = df.groupby([DATE, dimension], observed=False)[metric].sum().reset_index()

    # ─── Top-row KPIs ─────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Observations", f"{len(daily):,}")
    k2.metric("Mean", f"{daily[metric].mean():,.2f}")
    k3.metric("Median", f"{daily[metric].median():,.2f}")
    k4.metric("Std", f"{daily[metric].std():,.2f}")

    # ─── Histogram of all daily observations ──────────────────────────────
    fig_h = px.histogram(
        daily, x=metric, nbins=50, color_discrete_sequence=[PRIMARY],
        title=f"Distribution of daily {metric}",
    )
    fig_h.update_layout(height=320, margin={"l": 40, "r": 20, "t": 40, "b": 40}, showlegend=False)

    # Top-N to keep boxplot readable
    top_n = 12
    top_dim_values = (
        daily.groupby(dimension, observed=False)[metric].sum()
        .sort_values(ascending=False).head(top_n).index.tolist()
    )
    sub = daily[daily[dimension].isin(top_dim_values)]
    fig_b = px.box(
        sub, x=dimension, y=metric, color=dimension,
        category_orders={dimension: top_dim_values},
        color_discrete_sequence=px.colors.qualitative.Set2,
        title=f"{metric} per day by {dimension} (top {top_n} by total)",
    )
    fig_b.update_layout(height=420, margin={"l": 40, "r": 20, "t": 40, "b": 60}, showlegend=False)
    fig_b.update_xaxes(tickangle=-30)

    # Two-up
    a, b = st.columns(2)
    with a:
        st.plotly_chart(fig_h, use_container_width=True, config=CHART_CONFIG)
    with b:
        st.plotly_chart(fig_b, use_container_width=True, config=CHART_CONFIG)

    # ─── Per-dimension summary table ──────────────────────────────────────
    summary = daily.groupby(dimension, observed=False)[metric].agg(
        ["count", "mean", "median", "std", "min", "max", "sum"]
    ).reset_index().sort_values("sum", ascending=False).head(50)

    st.subheader(f"Summary by {dimension}")
    st.dataframe(
        summary,
        hide_index=True,
        column_config={
            "mean":   st.column_config.NumberColumn(format="%.2f"),
            "median": st.column_config.NumberColumn(format="%.2f"),
            "std":    st.column_config.NumberColumn(format="%.2f"),
            "min":    st.column_config.NumberColumn(format="%.2f"),
            "max":    st.column_config.NumberColumn(format="%.2f"),
            "sum":    st.column_config.NumberColumn(format="%.2f"),
        },
        use_container_width=True,
    )
