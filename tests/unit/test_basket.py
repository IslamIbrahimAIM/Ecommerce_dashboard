from __future__ import annotations

import pandas as pd

from analytics.basket import apriori_rules, to_basket_matrix


def _transactions() -> pd.DataFrame:
    return pd.DataFrame({
        "order_id": ["o1", "o1", "o2", "o2", "o3", "o3", "o4", "o4", "o4", "o5"],
        "product": ["bread", "milk", "bread", "milk", "bread", "milk", "bread", "milk", "butter", "bread"],
    })


def test_to_basket_matrix_one_hot():
    bm = to_basket_matrix(_transactions(), order_col="order_id", item_col="product")
    assert bm.dtypes.eq(bool).all()
    assert bm.loc["o1", "bread"]
    assert not bm.loc["o5", "milk"]


def test_apriori_rules_returns_pairs():
    bm = to_basket_matrix(_transactions(), order_col="order_id", item_col="product")
    rules = apriori_rules(bm, min_support=0.4, min_confidence=0.5, min_lift=1.0)
    if not rules.empty:
        assert "lift" in rules.columns and "confidence" in rules.columns
        assert (rules["lift"] >= 1.0).all()


def test_apriori_empty_basket():
    out = apriori_rules(pd.DataFrame(), min_support=0.5)
    assert out.empty
