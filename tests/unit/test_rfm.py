from __future__ import annotations

import pandas as pd

from analytics.rfm import compute_rfm


def test_rfm_columns(synth_customer_orders):
    out = compute_rfm(synth_customer_orders, customer_col="customer_id", date_col="date", revenue_col="revenue")
    assert {"recency", "frequency", "monetary", "R", "F", "M", "RFM", "segment"} <= set(out.columns)
    assert len(out) == synth_customer_orders["customer_id"].nunique()


def test_rfm_scores_in_range(synth_customer_orders):
    out = compute_rfm(synth_customer_orders, customer_col="customer_id", date_col="date", revenue_col="revenue")
    for col in ("R", "F", "M"):
        assert out[col].between(1, 5).all()


def test_rfm_empty_input():
    empty = pd.DataFrame({"customer_id": [], "date": [], "revenue": []})
    out = compute_rfm(empty, customer_col="customer_id", date_col="date", revenue_col="revenue")
    assert out.empty
