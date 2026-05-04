"""Basket tab — Apriori association rules on synthetic items."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from analytics.basket import apriori_rules, to_basket_matrix
from charts.palettes import CHART_CONFIG
from charts.port import ChartPort
from data.repository import DataRepository
from infra.config import AppConfig
from ui.tabs._synth_cache import synth_baskets_cached
from ui.tabs._window import default_window


@st.cache_data(show_spinner="Mining frequent itemsets…")
def _rules(
    _repo: DataRepository,
    start,
    end,
    *,
    min_support: float,
    min_conf: float,
    max_orders: int,
) -> pd.DataFrame:
    items = synth_baskets_cached(_repo, start, end, max_orders=max_orders)
    if items.empty:
        return pd.DataFrame()
    bm = to_basket_matrix(items, order_col="order_id", item_col="item")
    return apriori_rules(bm, min_support=min_support, min_confidence=min_conf, min_lift=1.0)


def _fmt_set(x: object) -> str:
    if isinstance(x, frozenset):
        return ", ".join(sorted(x))
    return str(x)


def render(repo: DataRepository, charts: ChartPort, _: AppConfig) -> None:
    st.title("Market Basket — Apriori")

    range_min, range_max = repo.date_range()
    d_start, d_end = default_window(range_min, range_max, days=7)
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
    with c1:
        start = st.date_input("Start", d_start, min_value=range_min, max_value=range_max, key="bk-start")
    with c2:
        end = st.date_input("End", d_end, min_value=range_min, max_value=range_max, key="bk-end")
    with c3:
        min_sup = st.slider("Min support", 0.001, 0.10, 0.005, step=0.001, format="%.3f")
    with c4:
        min_conf = st.slider("Min confidence", 0.05, 0.95, 0.30, step=0.05)
    max_orders = 30_000  # cap synth orders so Apriori stays sub-10s

    st.caption(
        "Items are synthesized as `category|brand` per order (seed=42). Affinity is biased toward "
        "same-category co-purchases."
    )

    rules = _rules(repo, start, end, min_support=min_sup, min_conf=min_conf, max_orders=max_orders)
    if rules.empty:
        st.info("No association rules found at these thresholds. Try lowering Min Support.")
        return

    # ─── KPIs ─────────────────────────────────────────────────────────────
    k1, k2, k3 = st.columns(3)
    k1.metric("Rules", f"{len(rules):,}")
    k2.metric("Median lift", f"{rules['lift'].median():.2f}")
    k3.metric("Median confidence", f"{rules['confidence'].median():.2f}")

    # ─── Support × Confidence scatter sized by Lift ──────────────────────
    df = rules.copy()
    df["antecedents"] = df["antecedents"].map(_fmt_set)
    df["consequents"] = df["consequents"].map(_fmt_set)

    fig = px.scatter(
        df.head(500),
        x="support", y="confidence", color="lift", size="lift",
        hover_data={
            "antecedents": True, "consequents": True,
            "lift": ":.2f", "support": ":.3f", "confidence": ":.2f",
        },
        color_continuous_scale="Blues",
        title="Rules: support × confidence (sized & colored by lift)",
    )
    fig.update_layout(height=440, margin={"l": 40, "r": 20, "t": 40, "b": 40})
    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    # ─── Rules table ──────────────────────────────────────────────────────
    st.subheader("Top rules by lift")
    st.dataframe(
        df[["antecedents", "consequents", "support", "confidence", "lift"]].head(50),
        hide_index=True,
        column_config={
            "support": st.column_config.NumberColumn(format="%.3f"),
            "confidence": st.column_config.NumberColumn(format="%.2f"),
            "lift": st.column_config.NumberColumn(format="%.2f"),
        },
        use_container_width=True,
    )
