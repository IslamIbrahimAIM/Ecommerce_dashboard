"""Cohort retention tab — acquisition cohort × period grid (synthetic events)."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from analytics.cohort import cohort_retention, cohort_retention_rates
from charts.palettes import CHART_CONFIG
from charts.port import ChartPort
from data.repository import DataRepository
from infra.config import AppConfig
from ui.tabs._synth_cache import synth_orders_cached
from ui.tabs._window import default_window


def render(repo: DataRepository, charts: ChartPort, _: AppConfig) -> None:
    st.title("Cohort Retention")

    range_min, range_max = repo.date_range()
    # Cohort needs a longer window to show useful periods
    d_start, d_end = default_window(range_min, range_max, days=21)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        start = st.date_input("Start", d_start, min_value=range_min, max_value=range_max, key="coh-start")
    with c2:
        end = st.date_input("End", d_end, min_value=range_min, max_value=range_max, key="coh-end")
    with c3:
        period = st.selectbox("Cohort period", ["W", "M"], index=0, format_func=lambda p: {"W": "Weekly", "M": "Monthly"}[p])

    st.caption(
        "Synthetic per-customer events (seed=42). The data spans a single month, so weekly cohorts "
        "expose more structure than monthly."
    )

    orders = synth_orders_cached(repo, start, end)
    if orders.empty:
        st.info("No orders in the selected range.")
        return

    counts = cohort_retention(orders, customer_col="customer_id", date_col="date", period=period)
    if counts.empty or counts.shape[1] < 2:
        st.info(f"Not enough variation across the period for {period} cohorts.")
        return
    rates = cohort_retention_rates(counts) * 100

    # ─── Heatmap: cohorts × periods, retention % ─────────────────────────
    z = rates.values
    fig = go.Figure(go.Heatmap(
        z=z,
        x=[f"+{c}" for c in rates.columns],
        y=[str(idx) for idx in rates.index],
        colorscale="Blues",
        zmin=0, zmax=100,
        colorbar={"title": "% retained"},
        text=[[f"{v:.0f}%" if v > 0 else "" for v in row] for row in z],
        texttemplate="%{text}",
        hovertemplate="cohort %{y} · offset %{x}<br>retention=%{z:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        height=420, margin={"l": 90, "r": 20, "t": 40, "b": 30},
        title={"text": "Retention rate by cohort", "x": 0.0, "xanchor": "left", "font": {"size": 14}},
        xaxis={"title": "Periods since first purchase"},
        yaxis={"title": "Cohort"},
    )
    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    # ─── Tables ───────────────────────────────────────────────────────────
    a, b = st.columns(2)
    with a:
        st.subheader("Customer counts")
        st.dataframe(counts, use_container_width=True)
    with b:
        st.subheader("Retention rate (%)")
        st.dataframe(rates.round(1), use_container_width=True)
