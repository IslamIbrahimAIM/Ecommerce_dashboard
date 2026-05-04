"""Market basket analysis via Apriori (mlxtend).

Needs order_id + product item rows. Project caveat in `rfm.py` applies — the
existing pickles do not have item-level data.
"""
from __future__ import annotations

import pandas as pd


def to_basket_matrix(
    df: pd.DataFrame,
    *,
    order_col: str,
    item_col: str,
) -> pd.DataFrame:
    """One-hot order × item boolean matrix expected by mlxtend.apriori."""
    if df.empty:
        return pd.DataFrame()
    crossed = (
        df.assign(_count=1)
        .pivot_table(index=order_col, columns=item_col, values="_count", aggfunc="sum", fill_value=0)
    )
    return (crossed > 0).astype(bool)


def apriori_rules(
    basket: pd.DataFrame,
    *,
    min_support: float = 0.01,
    min_confidence: float = 0.3,
    min_lift: float = 1.0,
) -> pd.DataFrame:
    """Run mlxtend Apriori → association rules. Returns sorted rules DataFrame."""
    from mlxtend.frequent_patterns import apriori, association_rules

    if basket.empty:
        return pd.DataFrame()

    freq = apriori(basket, min_support=min_support, use_colnames=True)
    if freq.empty:
        return pd.DataFrame()

    rules = association_rules(freq, metric="confidence", min_threshold=min_confidence)
    rules = rules[rules["lift"] >= min_lift]
    return rules.sort_values(by=["lift", "confidence"], ascending=False).reset_index(drop=True)
