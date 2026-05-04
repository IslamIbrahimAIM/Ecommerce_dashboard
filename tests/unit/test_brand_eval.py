from __future__ import annotations

import pandas as pd

from analytics.brand_eval import DEFAULT_BUCKETS, BucketingPolicy, score_brands


def test_buckets_cover_full_range_no_overlap():
    seen: dict[int, str] = {}
    for s in range(3, 13):
        seen[s] = DEFAULT_BUCKETS.label(s)
    assert seen[3] == "Star"
    assert seen[5] == "High Performance"
    assert seen[7] == "High Performance"  # was unmapped in old code
    assert seen[8] == "Low Performance"
    assert seen[12] == "Weak Performance"


def test_buckets_custom_policy():
    policy = BucketingPolicy(bounds=((3, 6, "Top"), (7, 12, "Bottom")))
    assert policy.label(3) == "Top"
    assert policy.label(12) == "Bottom"


def test_score_brands_adds_columns():
    df = pd.DataFrame({
        "brand": ["a", "b", "c", "d", "e"],
        "Views": [10, 20, 30, 40, 50],
        "Orders": [1, 2, 3, 4, 5],
        "Sales": [100, 200, 300, 400, 500],
    })
    out = score_brands(df, views_col="Views", orders_col="Orders", sales_col="Sales")
    for col in ["Views_class", "Orders_class", "Sales_class", "Score", "Score_Bucket"]:
        assert col in out.columns
    assert out["Score"].between(3, 12).all()


def test_score_brands_does_not_mutate_input():
    df = pd.DataFrame({
        "Views": [10, 20], "Orders": [1, 2], "Sales": [100, 200],
    })
    snapshot = df.copy()
    _ = score_brands(df, views_col="Views", orders_col="Orders", sales_col="Sales")
    pd.testing.assert_frame_equal(df, snapshot)
