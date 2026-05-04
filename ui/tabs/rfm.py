"""RFM tab — Recency / Frequency / Monetary segmentation.

Operates on synthetic per-customer events (no customer_id in source data).
"""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from analytics.rfm import compute_rfm
from charts.palettes import CHART_CONFIG
from charts.port import ChartPort
from data.repository import DataRepository
from infra.config import AppConfig
from ui.tabs._synth_cache import synth_orders_cached
from ui.tabs._window import default_window


def render(repo: DataRepository, charts: ChartPort, _: AppConfig) -> None:
    st.title("RFM — Recency · Frequency · Monetary")

    range_min, range_max = repo.date_range()
    d_start, d_end = default_window(range_min, range_max, days=14)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        start = st.date_input("Start", d_start, min_value=range_min, max_value=range_max, key="rfm-start")
    with c2:
        end = st.date_input("End", d_end, min_value=range_min, max_value=range_max, key="rfm-end")
    with c3:
        pool = st.number_input("Customer pool size", min_value=500, max_value=50_000, value=5_000, step=500)

    st.caption(
        "Source data is event-aggregate; per-customer events are **synthesized deterministically** "
        "(seed=42) so RFM can compute. Same inputs → same output across reruns."
    )

    orders = synth_orders_cached(repo, start, end, customer_pool_size=int(pool))
    if orders.empty:
        st.info("No orders in the selected range.")
        return

    rfm = compute_rfm(orders, customer_col="customer_id", date_col="date", revenue_col="revenue")
    if rfm.empty:
        st.info("Not enough customers to score.")
        return

    # ─── Top KPIs ─────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Customers", f"{len(rfm):,}")
    k2.metric("Avg recency (d)", f"{rfm['recency'].mean():.1f}")
    k3.metric("Median frequency", f"{rfm['frequency'].median():.0f}")
    k4.metric("Avg monetary", f"${rfm['monetary'].mean():,.0f}")

    # ─── Segment distribution ─────────────────────────────────────────────
    seg = (
        rfm["segment"].value_counts().rename_axis("segment").reset_index(name="customers")
        .sort_values("customers", ascending=False)
    )
    fig_seg = px.bar(
        seg, x="segment", y="customers", text="customers",
        color="segment", color_discrete_sequence=px.colors.qualitative.Set2,
        title="Customers per RFM segment",
    )
    fig_seg.update_layout(height=320, showlegend=False, margin={"l": 30, "r": 20, "t": 40, "b": 60})
    fig_seg.update_traces(texttemplate="%{text}", textposition="outside")
    st.plotly_chart(fig_seg, use_container_width=True, config=CHART_CONFIG)

    # ─── R/F scatter colored by Monetary ──────────────────────────────────
    fig_scatter = px.scatter(
        rfm.sample(n=min(2000, len(rfm)), random_state=0),
        x="recency", y="frequency", color="monetary",
        size="monetary",
        hover_data=["customer_id", "segment", "RFM"],
        color_continuous_scale="Blues",
        title="Recency vs Frequency (sized & colored by Monetary)",
    )
    fig_scatter.update_layout(height=420, margin={"l": 40, "r": 20, "t": 40, "b": 40})
    st.plotly_chart(fig_scatter, use_container_width=True, config=CHART_CONFIG)

    # ─── Per-segment summary ──────────────────────────────────────────────
    seg_summary = rfm.groupby("segment", observed=False).agg(
        customers=("customer_id", "size"),
        avg_recency=("recency", "mean"),
        avg_frequency=("frequency", "mean"),
        total_monetary=("monetary", "sum"),
    ).reset_index().sort_values("total_monetary", ascending=False)

    st.subheader("Segment summary")
    st.dataframe(
        seg_summary,
        hide_index=True,
        column_config={
            "avg_recency": st.column_config.NumberColumn(format="%.1f d"),
            "avg_frequency": st.column_config.NumberColumn(format="%.2f"),
            "total_monetary": st.column_config.NumberColumn(format="$%.0f"),
        },
        use_container_width=True,
    )
