"""Acquisition cohort retention.

Needs raw events keyed by customer_id + date. Project caveat in `rfm.py` applies.
"""
from __future__ import annotations

import pandas as pd


def cohort_retention(
    events: pd.DataFrame,
    *,
    customer_col: str,
    date_col: str,
    period: str = "M",
) -> pd.DataFrame:
    """Wide cohort × period matrix of retained customer counts."""
    if events.empty:
        return pd.DataFrame()

    work = events.copy()
    work[date_col] = pd.to_datetime(work[date_col])
    work["_period"] = work[date_col].dt.to_period(period)
    work["_cohort"] = work.groupby(customer_col)[date_col].transform("min").dt.to_period(period)
    work["_offset"] = (work["_period"] - work["_cohort"]).apply(lambda x: x.n)

    grid = (
        work.groupby(["_cohort", "_offset"])[customer_col]
        .nunique()
        .unstack(fill_value=0)
        .sort_index()
    )
    return grid


def cohort_retention_rates(grid: pd.DataFrame) -> pd.DataFrame:
    """Convert absolute counts to retention rate (% of cohort size)."""
    if grid.empty:
        return grid
    sizes = grid.iloc[:, 0].replace(0, pd.NA)
    return grid.div(sizes, axis=0).fillna(0.0)
