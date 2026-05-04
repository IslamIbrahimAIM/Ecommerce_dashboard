"""Time-series tab — observed line + 7d MA + STL decomposition (trend/seasonal/resid)."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from analytics.kpi import rolling_mean
from analytics.timeseries import decompose
from charts.palettes import CHART_CONFIG, PRIMARY
from charts.port import ChartPort
from data.repository import DATE, DataRepository
from infra.config import AppConfig

METRICS = ["Sales", "Orders", "Sessions", "Cart"]


def _line_with_overlay(series: pd.Series, title: str, *, overlay: pd.Series | None = None) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=series.index, y=series.values, mode="lines",
        name=title, line={"color": PRIMARY, "width": 2},
    ))
    if overlay is not None:
        fig.add_trace(go.Scatter(
            x=overlay.index, y=overlay.values, mode="lines",
            name="7d rolling avg", line={"color": "#8b5cf6", "width": 2, "dash": "dot"},
        ))
    fig.update_layout(
        height=260, margin={"l": 40, "r": 20, "t": 36, "b": 30},
        title={"text": title, "x": 0.0, "xanchor": "left", "font": {"size": 14}},
        xaxis={"showgrid": False},
        yaxis={"showgrid": True, "gridcolor": "rgba(0,0,0,0.06)", "zeroline": False},
        hovermode="x unified", showlegend=overlay is not None,
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
    )
    return fig


def render(repo: DataRepository, charts: ChartPort, _: AppConfig) -> None:
    st.title("Time-Series Decomposition")

    range_min, range_max = repo.date_range()
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        start = st.date_input(
            "Start", range_min,
            min_value=range_min, max_value=range_max, key="ts-start",
        )
    with c2:
        end = st.date_input(
            "End", range_max,
            min_value=range_min, max_value=range_max, key="ts-end",
        )
    with c3:
        metric = st.selectbox("Metric", METRICS, index=METRICS.index("Sales"))

    if end < start:
        st.error("End date must be on or after start date.")
        return

    daily = repo.daily_overall(start, end)
    if daily.empty:
        st.info("No data in the selected range.")
        return

    series = daily.groupby(DATE, observed=False)[metric].sum().sort_index()
    series.index = pd.to_datetime(series.index)
    if len(series) < 14:
        st.info(f"Need at least 14 days for a meaningful decomposition; you selected {len(series)}.")
        st.plotly_chart(_line_with_overlay(series, f"{metric} (daily)"), use_container_width=True, config=CHART_CONFIG)
        return

    # ─── Observed + 7d MA ─────────────────────────────────────────────────
    ma = rolling_mean(series, window=7)
    st.plotly_chart(
        _line_with_overlay(series, f"{metric} — observed", overlay=ma),
        use_container_width=True, config=CHART_CONFIG,
    )

    # ─── STL decomposition ────────────────────────────────────────────────
    parts = decompose(series, period=7)
    cols = st.columns(3)
    for col, (name, color) in zip(
        cols,
        [("trend", "#2563eb"), ("seasonal", "#0891b2"), ("resid", "#dc2626")],
        strict=False,
    ):
        with col:
            comp = parts.get(name)
            if comp is None or comp.dropna().empty:
                st.info(f"{name}: insufficient data.")
                continue
            comp = comp.dropna()
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=comp.index, y=comp.values, mode="lines",
                                     line={"color": color, "width": 1.6}))
            fig.update_layout(
                height=220, margin={"l": 30, "r": 10, "t": 30, "b": 26},
                title={"text": name.title(), "x": 0.0, "xanchor": "left", "font": {"size": 13}},
                xaxis={"showgrid": False},
                yaxis={"showgrid": True, "gridcolor": "rgba(0,0,0,0.06)", "zeroline": False},
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    st.caption(
        "Seasonal decomposition (`statsmodels.seasonal_decompose`, period=7). "
        "**Trend** removes weekly cycles, **Seasonal** is the repeating pattern, "
        "**Resid** is what neither captures — large residuals indicate anomalies."
    )
