from __future__ import annotations

import pandas as pd

from data.synthetic import synth_basket_items, synth_orders


def _daily_brand() -> pd.DataFrame:
    return pd.DataFrame({
        "date": pd.to_datetime(["2024-01-01", "2024-01-01", "2024-01-02"]),
        "user_type": ["New_User", "Returning_User", "New_User"],
        "brand": ["BrandA", "BrandB", "BrandA"],
        "Orders": [10, 5, 8],
        "Buyers": [7, 4, 6],
        "Sales": [200.0, 90.0, 160.0],
    })


def test_synth_orders_count_matches_total_orders():
    out = synth_orders(_daily_brand())
    assert len(out) == 23  # 10 + 5 + 8


def test_synth_orders_revenue_total_close_to_input():
    df = _daily_brand()
    out = synth_orders(df)
    assert abs(out["revenue"].sum() - df["Sales"].sum()) < 1.0


def test_synth_orders_deterministic():
    df = _daily_brand()
    a = synth_orders(df, seed=7)
    b = synth_orders(df, seed=7)
    pd.testing.assert_frame_equal(a, b)


def test_synth_orders_different_seeds_diverge():
    df = _daily_brand()
    a = synth_orders(df, seed=1)
    b = synth_orders(df, seed=2)
    # Same shape but different customer assignment → row-wise different
    assert not a.equals(b)


def test_synth_orders_empty_input():
    out = synth_orders(pd.DataFrame(columns=["date", "user_type", "brand", "Orders", "Buyers", "Sales"]))
    assert out.empty
    assert list(out.columns) == ["customer_id", "order_id", "date", "brand", "user_type", "revenue"]


def test_synth_basket_items_includes_anchor_brand():
    orders = synth_orders(_daily_brand(), seed=0)
    daily_cb = pd.DataFrame({
        "date": pd.to_datetime(["2024-01-01", "2024-01-01"]),
        "category": ["electronics", "electronics"],
        "brand": ["BrandA", "BrandB"],
    })
    items = synth_basket_items(orders, daily_cb)
    assert not items.empty
    assert {"order_id", "item", "customer_id"} <= set(items.columns)
    # Each order has at least its anchor brand among items
    for _oid, group in items.groupby("order_id"):
        assert any(item in {"BrandA", "BrandB"} for item in group["item"])
