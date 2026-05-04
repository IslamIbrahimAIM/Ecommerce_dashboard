"""Brand performance scoring.

Replaces the original `BrandEvaluator` class. Pure function; injected
thresholds; non-overlapping bucket bounds (the original had `score >= 5 and
score <= 5` collisions and an unmapped `score == 7`).
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

DEFAULT_QUANTILES = (0.3, 0.6, 0.9)


@dataclass(frozen=True)
class BucketingPolicy:
    """Maps total score (sum of three 1-4 metric scores) → label.

    Bounds are inclusive and non-overlapping. Total score range is 3..12.
    Lower score = top performer (a value above the 0.9 quantile gets a 1).
    """

    bounds: tuple[tuple[int, int, str], ...] = (
        (3, 4, "Star"),
        (5, 7, "High Performance"),
        (8, 10, "Low Performance"),
        (11, 12, "Weak Performance"),
    )

    def label(self, score: int) -> str:
        for lo, hi, name in self.bounds:
            if lo <= score <= hi:
                return name
        return "Weak Performance"


DEFAULT_BUCKETS = BucketingPolicy()


def _classify(value: float, thresholds: pd.Series) -> int:
    if value <= thresholds.iloc[0]:
        return 4
    if value <= thresholds.iloc[1]:
        return 3
    if value <= thresholds.iloc[2]:
        return 2
    return 1


def score_brands(
    df: pd.DataFrame,
    *,
    views_col: str,
    orders_col: str,
    sales_col: str,
    quantiles: tuple[float, float, float] = DEFAULT_QUANTILES,
    buckets: BucketingPolicy = DEFAULT_BUCKETS,
) -> pd.DataFrame:
    """Add Views_class / Orders_class / Sales_class / Score / Score_Bucket columns.

    Returns a NEW DataFrame; does not mutate `df`.
    """
    out = df.copy()
    quartiles = {
        "views": out[views_col].quantile(q=list(quantiles)),
        "orders": out.loc[out[orders_col] > 0, orders_col].quantile(q=list(quantiles)),
        "sales": out.loc[out[sales_col] > 0, sales_col].quantile(q=list(quantiles)),
    }

    out["Views_class"] = out[views_col].apply(lambda v: _classify(v, quartiles["views"]))
    out["Orders_class"] = out[orders_col].apply(lambda v: _classify(v, quartiles["orders"]))
    out["Sales_class"] = out[sales_col].apply(lambda v: _classify(v, quartiles["sales"]))
    out["Score"] = out["Views_class"] + out["Orders_class"] + out["Sales_class"]
    out["Score_Bucket"] = out["Score"].apply(buckets.label)
    return out
