"""Streamlit-cached synthetic events for RFM / Cohort / CLV / Basket tabs."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from data.repository import DataRepository
from data.synthetic import synth_basket_items, synth_orders


@st.cache_data(show_spinner="Synthesizing customer events…")
def synth_orders_cached(
    _repo: DataRepository,
    start,
    end,
    *,
    customer_pool_size: int = 5_000,
    max_orders: int | None = 100_000,
) -> pd.DataFrame:
    daily_brand = _repo.daily_by_brand(start, end)
    return synth_orders(
        daily_brand,
        customer_pool_size=customer_pool_size,
        max_orders=max_orders,
    )


@st.cache_data(show_spinner="Synthesizing baskets…")
def synth_baskets_cached(
    _repo: DataRepository,
    start,
    end,
    *,
    customer_pool_size: int = 5_000,
    max_orders: int | None = 50_000,
) -> pd.DataFrame:
    orders = synth_orders_cached(
        _repo, start, end,
        customer_pool_size=customer_pool_size,
        max_orders=max_orders,
    )
    if orders.empty:
        return pd.DataFrame(columns=["order_id", "item", "customer_id"])
    daily_cb = _repo.daily_by_category(start, end)
    merged = _repo.merged(start, end)[["category", "brand"]].drop_duplicates()
    daily_cb = daily_cb.merge(merged, on="category", how="left")
    return synth_basket_items(orders, daily_cb)
