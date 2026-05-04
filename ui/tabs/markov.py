"""Funnel-state Markov chain — transition heatmap, Sankey, removal-effect bar."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from analytics.markov import funnel_transition_matrix, removal_effect
from charts.palettes import CHART_CONFIG, PRIMARY
from charts.port import ChartPort
from data.repository import DataRepository
from infra.config import AppConfig

_STAGES = ("Total_Sessions", "Total_Views", "Total_Cart", "Total_Orders")
_STAGE_LABELS = {
    "Total_Sessions": "Sessions",
    "Total_Views":    "Views",
    "Total_Cart":     "Cart",
    "Total_Orders":   "Orders",
    "drop":           "Drop",
}


def _sankey(counts: dict[str, int]) -> go.Figure:
    """Sessions → Views → Cart → Orders flow with explicit drop-off branches."""
    nodes = ["Sessions", "Views", "Cart", "Orders", "Drop @ Views", "Drop @ Cart", "Drop @ Orders"]
    node_colors = [PRIMARY, PRIMARY, PRIMARY, "#16a34a", "#dc2626", "#dc2626", "#dc2626"]
    sources, targets, values = [], [], []

    raw = [
        counts.get("Total_Sessions", 0),
        counts.get("Total_Views", 0),
        counts.get("Total_Cart", 0),
        counts.get("Total_Orders", 0),
    ]
    # Sessions → Views (or drop)
    if raw[0] > 0:
        sources += [0, 0]
        targets += [1, 4]
        values += [min(raw[1], raw[0]), max(raw[0] - raw[1], 0)]
    # Views → Cart (or drop)
    if raw[1] > 0:
        sources += [1, 1]
        targets += [2, 5]
        values += [min(raw[2], raw[1]), max(raw[1] - raw[2], 0)]
    # Cart → Orders (or drop)
    if raw[2] > 0:
        sources += [2, 2]
        targets += [3, 6]
        values += [min(raw[3], raw[2]), max(raw[2] - raw[3], 0)]

    fig = go.Figure(go.Sankey(
        node={
            "label": nodes, "color": node_colors, "pad": 18, "thickness": 18,
            "line": {"color": "rgba(0,0,0,0.1)", "width": 0.5},
        },
        link={"source": sources, "target": targets, "value": values,
              "color": ["rgba(29,78,216,0.25)" if t < 4 else "rgba(220,38,38,0.18)" for t in targets]},
    ))
    fig.update_layout(
        height=360, margin={"l": 0, "r": 0, "t": 30, "b": 0},
        title={"text": "Conversion flow (count of events)", "x": 0.0, "xanchor": "left", "font": {"size": 14}},
    )
    return fig


def _retention_bars(counts: dict[str, int]) -> go.Figure:
    """Stage-by-stage retention rate."""
    labels, rates = [], []
    nums = [counts.get(s, 0) for s in _STAGES]
    for i in range(1, len(_STAGES)):
        if nums[i - 1] == 0:
            continue
        rate = min(nums[i] / nums[i - 1], 1.0) * 100
        labels.append(f"{_STAGE_LABELS[_STAGES[i-1]]} → {_STAGE_LABELS[_STAGES[i]]}")
        rates.append(rate)
    fig = go.Figure(go.Bar(
        x=rates, y=labels, orientation="h",
        marker={"color": PRIMARY},
        text=[f"{r:.1f}%" for r in rates], textposition="outside",
    ))
    fig.update_layout(
        height=240, margin={"l": 130, "r": 40, "t": 30, "b": 30},
        title={"text": "Step retention (%)", "x": 0.0, "xanchor": "left", "font": {"size": 14}},
        xaxis={"range": [0, 110], "showgrid": True, "gridcolor": "rgba(0,0,0,0.06)"},
        yaxis={"autorange": "reversed"},
    )
    return fig


def render(repo: DataRepository, charts: ChartPort, _: AppConfig) -> None:
    st.title("Funnel Markov Chain")

    range_min, range_max = repo.date_range()
    c1, c2 = st.columns(2)
    with c1:
        start = st.date_input(
            "Start", range_min, min_value=range_min, max_value=range_max, key="markov-start",
        )
    with c2:
        end = st.date_input(
            "End", range_max, min_value=range_min, max_value=range_max, key="markov-end",
        )
    if end < start:
        st.error("End date must be on or after start date.")
        return

    daily = repo.daily_overall(start, end)
    if daily.empty:
        st.info("No data in the selected range.")
        return

    counts = {
        "Total_Sessions": int(daily["Sessions"].sum()),
        "Total_Views":    int(daily["Views"].sum()),
        "Total_Cart":     int(daily["Cart"].sum()),
        "Total_Orders":   int(daily["Orders"].sum()),
    }

    top_l, top_r = st.columns([3, 2])
    with top_l:
        st.plotly_chart(_sankey(counts), use_container_width=True, config=CHART_CONFIG)
    with top_r:
        st.plotly_chart(_retention_bars(counts), use_container_width=True, config=CHART_CONFIG)

    # ─── Markov transition matrix + removal-effect attribution ───────────
    matrix = funnel_transition_matrix(counts)
    matrix.index = [_STAGE_LABELS.get(s, s) for s in matrix.index]
    matrix.columns = [_STAGE_LABELS.get(s, s) for s in matrix.columns]

    bot_l, bot_r = st.columns([3, 2])
    with bot_l:
        st.subheader("Transition probabilities")
        charts.heatmap(matrix, title="P(next | current)").render(st)
        st.caption(
            "Each cell = probability the cohort moves from row → column in one step. "
            "'Drop' is absorbing; values are derived from aggregate stage counts, "
            "not per-user sequences."
        )
    with bot_r:
        st.subheader("Removal-effect attribution")
        eff = removal_effect(matrix, conversion_state=_STAGE_LABELS["Total_Orders"])
        eff_df = eff.rename("removal_effect").rename_axis("state").reset_index()
        # As a chart: which stages, when removed, drop conversion the most?
        fig = go.Figure(go.Bar(
            x=eff_df["removal_effect"].astype(float),
            y=eff_df["state"], orientation="h",
            marker={"color": "#0891b2"},
            text=[f"{v:+.3f}" for v in eff_df["removal_effect"]], textposition="outside",
        ))
        fig.update_layout(
            height=240, margin={"l": 90, "r": 40, "t": 24, "b": 30},
            title={"text": "Δ conversion if removed", "x": 0.0, "xanchor": "left", "font": {"size": 13}},
            yaxis={"autorange": "reversed"},
            xaxis={"showgrid": True, "gridcolor": "rgba(0,0,0,0.06)"},
        )
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
        st.caption("Higher value = stage is more pivotal for conversion.")
