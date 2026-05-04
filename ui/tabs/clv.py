"""CLV tab — historical + simple predictive lifetime value (synthetic events)."""
from __future__ import annotations

import plotly.express as px
import streamlit as st

from analytics.clv import historical_clv, simple_clv
from charts.palettes import CHART_CONFIG, PRIMARY
from charts.port import ChartPort
from data.repository import DataRepository
from infra.config import AppConfig
from ui.tabs._synth_cache import synth_orders_cached
from ui.tabs._window import default_window


def render(repo: DataRepository, charts: ChartPort, _: AppConfig) -> None:
    st.title("Customer Lifetime Value")

    range_min, range_max = repo.date_range()
    d_start, d_end = default_window(range_min, range_max, days=14)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        start = st.date_input("Start", d_start, min_value=range_min, max_value=range_max, key="clv-start")
    with c2:
        end = st.date_input("End", d_end, min_value=range_min, max_value=range_max, key="clv-end")
    with c3:
        horizon = st.slider("Predictive horizon (months)", 1, 36, 12)

    st.caption("Synthetic per-customer events (seed=42). Historical CLV is exact; "
               "Simple CLV = AOV × purchase_frequency × horizon.")

    orders = synth_orders_cached(repo, start, end)
    if orders.empty:
        st.info("No orders in the selected range.")
        return

    historical = historical_clv(orders, customer_col="customer_id", revenue_col="revenue")
    predicted = simple_clv(
        orders, customer_col="customer_id", date_col="date",
        revenue_col="revenue", horizon_months=horizon,
    )

    # ─── KPI strip ────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Customers", f"{len(historical):,}")
    k2.metric("Total revenue", f"${historical['clv'].sum():,.0f}")
    k3.metric("Mean historical CLV", f"${historical['clv'].mean():,.2f}")
    k4.metric(f"Mean simple CLV ({horizon}mo)",
              f"${predicted['clv_simple'].mean():,.2f}" if not predicted.empty else "—")

    # ─── Distribution histograms ──────────────────────────────────────────
    h1, h2 = st.columns(2)
    with h1:
        fig = px.histogram(
            historical, x="clv", nbins=40,
            color_discrete_sequence=[PRIMARY],
            title="Historical CLV distribution",
        )
        fig.update_layout(height=330, margin={"l": 30, "r": 20, "t": 40, "b": 30}, showlegend=False)
        fig.update_xaxes(title="$ per customer")
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
    with h2:
        if predicted.empty:
            st.info("Not enough data to project.")
        else:
            fig = px.histogram(
                predicted, x="clv_simple", nbins=40,
                color_discrete_sequence=["#0891b2"],
                title=f"Simple predictive CLV ({horizon}-month horizon)",
            )
            fig.update_layout(height=330, margin={"l": 30, "r": 20, "t": 40, "b": 30}, showlegend=False)
            fig.update_xaxes(title="$ per customer")
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    # ─── Top 30 customers by predicted CLV ────────────────────────────────
    if not predicted.empty:
        top = predicted.merge(historical, on="customer_id").sort_values("clv_simple", ascending=False).head(30)
        st.subheader("Top customers by predicted CLV")
        st.dataframe(
            top,
            hide_index=True,
            column_order=["customer_id", "aov", "freq_per_month", "lifetime_months", "clv", "clv_simple"],
            column_config={
                "aov": st.column_config.NumberColumn(format="$%.2f"),
                "freq_per_month": st.column_config.NumberColumn(format="%.2f"),
                "lifetime_months": st.column_config.NumberColumn(format="%.1f"),
                "clv": st.column_config.NumberColumn("Historical CLV", format="$%.2f"),
                "clv_simple": st.column_config.NumberColumn("Simple CLV", format="$%.2f"),
            },
            use_container_width=True,
        )
