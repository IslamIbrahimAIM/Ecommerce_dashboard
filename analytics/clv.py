"""Customer Lifetime Value.

Two flavors:
- `historical_clv`: pure sum of revenue per customer (no model).
- `simple_clv`: AOV × purchase-frequency × customer-lifespan (heuristic).

For Bayesian / probabilistic CLV (BG/NBD + Gamma-Gamma), use the `lifetimes`
package — out of v1 scope.
"""
from __future__ import annotations

import pandas as pd


def historical_clv(
    orders: pd.DataFrame,
    *,
    customer_col: str,
    revenue_col: str,
) -> pd.DataFrame:
    if orders.empty:
        return pd.DataFrame(columns=[customer_col, "clv"])
    out = orders.groupby(customer_col)[revenue_col].sum().reset_index()
    return out.rename(columns={revenue_col: "clv"})


def simple_clv(
    orders: pd.DataFrame,
    *,
    customer_col: str,
    date_col: str,
    revenue_col: str,
    horizon_months: int = 12,
) -> pd.DataFrame:
    """Simple CLV = AOV × purchase_frequency_per_month × horizon_months."""
    if orders.empty:
        return pd.DataFrame(columns=[customer_col, "aov", "freq_per_month", "lifetime_months", "clv_simple"])

    work = orders.copy()
    work[date_col] = pd.to_datetime(work[date_col])
    grouped = work.groupby(customer_col).agg(
        order_count=(revenue_col, "size"),
        revenue=(revenue_col, "sum"),
        first=(date_col, "min"),
        last=(date_col, "max"),
    ).reset_index()

    grouped["aov"] = grouped["revenue"] / grouped["order_count"]
    months_active = ((grouped["last"] - grouped["first"]).dt.days / 30.0).clip(lower=1.0)
    grouped["lifetime_months"] = months_active
    grouped["freq_per_month"] = grouped["order_count"] / months_active
    grouped["clv_simple"] = grouped["aov"] * grouped["freq_per_month"] * horizon_months
    return grouped[[customer_col, "aov", "freq_per_month", "lifetime_months", "clv_simple"]]
