from __future__ import annotations

import pandas as pd

from analytics.funnel import funnel_summary, is_empty, split_by_user_type


def test_funnel_summary_extracts_stages():
    df = pd.DataFrame({
        "Total_Sessions": [100, 50],
        "Total_Views": [80, 40],
        "Total_Cart": [30, 15],
        "Total_Orders": [10, 5],
    })
    out = funnel_summary(df)
    assert out["stage"] == ["Total Sessions", "Total Views", "Total Cart", "Total Orders"]
    assert out["number"] == [150, 120, 45, 15]


def test_funnel_summary_missing_columns_yield_zero():
    df = pd.DataFrame({"Total_Sessions": [10]})
    out = funnel_summary(df)
    assert out["number"] == [10, 0, 0, 0]


def test_is_empty():
    assert is_empty({"number": [0, 0, 0, 0]})
    assert not is_empty({"number": [0, 1, 0, 0]})


def test_split_by_user_type():
    df = pd.DataFrame({"user_type": ["A", "B", "A"], "x": [1, 2, 3]})
    parts = split_by_user_type(df)
    assert set(parts) == {"A", "B"}
    assert len(parts["A"]) == 2
