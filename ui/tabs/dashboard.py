"""Ecom Dashboard — Tier 1 (KPI hero) + Tier 2 (trend) + Tier 3 (composition) + Tier 4 (drilldown).

All data flows through pre-aggregated parquet files via the repository — no
3M-row loads at request time. Charts are built via the ChartPort abstraction.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from analytics.brand_eval import score_brands
from analytics.funnel import funnel_summary
from analytics.kpi import abandonment_rate, pareto_cumulative, rolling_mean
from charts.palettes import CHART_CONFIG, USER_TYPE_PALETTE
from charts.port import ChartPort
from data.repository import DATE, DataRepository
from infra.config import AppConfig
from ui.components import kpi_scorecard

_TREND_METRICS = ["Sales", "Orders", "Sessions", "Cart"]


def _default_window(range_min: pd.Timestamp, range_max: pd.Timestamp) -> tuple:
    """Default to the last 7 days of available data."""
    end = pd.Timestamp(range_max)
    span = end - pd.Timestamp(range_min)
    days = min(7, max(span.days, 0))
    start = end - pd.Timedelta(days=days)
    return start.date(), end.date()


@st.cache_data(show_spinner=False)
def _daily_overall(_repo: DataRepository, start, end) -> pd.DataFrame:
    return _repo.daily_overall(start, end)


@st.cache_data(show_spinner=False)
def _daily_by_category(_repo: DataRepository, start, end) -> pd.DataFrame:
    return _repo.daily_by_category(start, end)


@st.cache_data(show_spinner=False)
def _daily_by_brand(_repo: DataRepository, start, end) -> pd.DataFrame:
    return _repo.daily_by_brand(start, end)


def _trend_chart(daily: pd.DataFrame, metric: str) -> object:
    import plotly.graph_objects as go
    series = daily.groupby(DATE, observed=False)[metric].sum().sort_index()
    series.index = pd.to_datetime(series.index)
    ma = rolling_mean(series, window=7)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=series.index, y=series.values, mode="lines+markers",
        name=metric, line={"color": "#3b82f6", "width": 2},
        marker={"size": 5},
    ))
    fig.add_trace(go.Scatter(
        x=ma.index, y=ma.values, mode="lines",
        name="7d rolling avg", line={"color": "#8b5cf6", "width": 2, "dash": "dot"},
    ))
    fig.update_layout(
        height=320, margin={"l": 40, "r": 20, "t": 30, "b": 30},
        title={"text": f"Daily {metric}", "x": 0.0, "xanchor": "left", "font": {"size": 15}},
        xaxis={"showgrid": False},
        yaxis={"showgrid": True, "gridcolor": "rgba(0,0,0,0.06)", "zeroline": False},
        hovermode="x unified", showlegend=True,
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
    )
    return fig


def render(repo: DataRepository, charts: ChartPort, _: AppConfig) -> None:
    range_min, range_max = repo.date_range()
    default_start, default_end = _default_window(range_min, range_max)

    # ─── Date selector (compact, single line) ─────────────────────────────
    sel = st.columns([1, 1, 4])
    with sel[0]:
        date1 = st.date_input("Start", default_start, min_value=range_min, max_value=range_max)
    with sel[1]:
        date2 = st.date_input("End", default_end, min_value=range_min, max_value=range_max)

    if date2 < date1:
        st.error("End date must be on or after start date.")
        return

    # ─── Tier 1: KPI scorecard ────────────────────────────────────────────
    kpi_scorecard.render(repo, start=date1, end=date2)
    st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)

    # ─── Tier 2: trend chart ──────────────────────────────────────────────
    daily = _daily_overall(repo, date1, date2)
    if daily.empty:
        st.info("No daily data in the selected range.")
        return

    metric_col, _ = st.columns([1, 5])
    with metric_col:
        metric = st.selectbox("Trend metric", _TREND_METRICS, index=0, label_visibility="collapsed")
    st.plotly_chart(_trend_chart(daily, metric), use_container_width=True, config=CHART_CONFIG)

    # ─── Tier 3: composition (funnel + category contribution) ────────────
    comp_left, comp_right = st.columns(2)

    with comp_left:
        # One faceted funnel — by user_type stacked
        funnel_overall = funnel_summary(
            daily.rename(columns={
                "Sessions": "Total_Sessions", "Views": "Total_Views",
                "Cart": "Total_Cart", "Orders": "Total_Orders",
            })
        )
        # Add retention % per stage to the labels
        nums = funnel_overall["number"]
        retentions = []
        for i, n in enumerate(nums):
            if i == 0 or nums[0] == 0:
                retentions.append(100.0)
            else:
                retentions.append(n / nums[0] * 100)
        labelled = {
            "stage": [f"{s} · {r:.0f}%" for s, r in zip(funnel_overall["stage"], retentions, strict=False)],
            "number": funnel_overall["number"],
        }
        charts.funnel(labelled, title="Conversion funnel", palette=["#3b82f6"]).render(st)

    with comp_right:
        cat = _daily_by_category(repo, date1, date2)
        cat_totals = (
            cat.groupby("category", observed=False)["Sales"]
            .sum().reset_index().sort_values("Sales", ascending=False)
        )
        cat_pareto = pareto_cumulative(cat_totals, value_col="Sales")
        charts.pareto(
            cat_pareto.head(10),
            x="category", bar_y="Sales", line_y="Cum_perc",
            title="Top categories — sales contribution",
        ).render(st)

    # ─── Tier 4: brand drilldown ──────────────────────────────────────────
    st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)
    st.subheader("Brand performance")

    brand_df = _daily_by_brand(repo, date1, date2)
    if brand_df.empty:
        st.info("No brand data in the selected range.")
        return

    brand_period = brand_df.groupby("brand", observed=False).agg(
        Sessions=("Sessions", "sum"), Views=("Views", "sum"),
        Cart=("Cart", "sum"), Orders=("Orders", "sum"),
        Sales=("Sales", "sum"), Buyers=("Buyers", "sum"),
    ).reset_index()

    scored = score_brands(brand_period, views_col="Views", orders_col="Orders", sales_col="Sales")
    scored = abandonment_rate(scored)

    bucket_order = ["Star", "High Performance", "Low Performance", "Weak Performance"]
    sel_col, count_col = st.columns([3, 1])
    with sel_col:
        selected_bucket = st.radio(
            "Performance tier",
            options=bucket_order,
            horizontal=True,
            label_visibility="collapsed",
        )
    with count_col:
        n = int((scored["Score_Bucket"] == selected_bucket).sum())
        st.markdown(f"<div style='text-align:right; color:#6b7280;'>{n} brands</div>", unsafe_allow_html=True)

    tier = scored[scored["Score_Bucket"] == selected_bucket].copy()
    tier = tier.sort_values("Sales", ascending=False)

    # Quadrant scatter — Orders × Sales, sized by Views, colored by score
    if not tier.empty:
        charts.scatter(
            tier.head(120),
            x="Orders", y="Sales",
            size="Views", color="Score",
            hover=["brand", "Views", "Orders", "Sales", "Abandonment Rate"],
            title=f"{selected_bucket} brands — Orders vs Sales (size = Views)",
        ).render(st)
    else:
        st.info(f"No brands in tier '{selected_bucket}' for this period.")

    st.dataframe(
        tier,
        hide_index=True,
        column_order=["brand", "Sales", "Orders", "Buyers", "Views", "Cart", "Abandonment Rate"],
        column_config={
            "Sales": st.column_config.NumberColumn(format="$%.0f"),
            "Abandonment Rate": st.column_config.NumberColumn(format="%.1f%%"),
        },
        use_container_width=True,
    )
