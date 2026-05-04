from __future__ import annotations

import pandas as pd

from analytics.clv import historical_clv, simple_clv


def test_historical_clv_sums_revenue(synth_customer_orders):
    out = historical_clv(synth_customer_orders, customer_col="customer_id", revenue_col="revenue")
    assert out.loc[out["customer_id"] == "c1", "clv"].iloc[0] == 80.0
    assert out.loc[out["customer_id"] == "c4", "clv"].iloc[0] == 105.0


def test_simple_clv_columns(synth_customer_orders):
    out = simple_clv(
        synth_customer_orders,
        customer_col="customer_id",
        date_col="date",
        revenue_col="revenue",
        horizon_months=12,
    )
    assert {"aov", "freq_per_month", "lifetime_months", "clv_simple"} <= set(out.columns)
    assert (out["clv_simple"] >= 0).all()


def test_simple_clv_empty():
    empty = pd.DataFrame({"customer_id": [], "date": [], "revenue": []})
    out = simple_clv(empty, customer_col="customer_id", date_col="date", revenue_col="revenue")
    assert out.empty
