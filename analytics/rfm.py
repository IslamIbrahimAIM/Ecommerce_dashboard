"""Recency / Frequency / Monetary scoring.

Operates on a per-customer order history. Caller passes a DataFrame and the
column names — no Streamlit, no I/O.

Note on this project's data: the existing pickles are pre-aggregated by
(date, user_type, category, brand) — there is no customer identifier. RFM
needs raw order events keyed by a stable customer/session id. If you only
have aggregates, RFM cannot run meaningfully. The function still works on
synthetic per-customer data; tests cover that path.
"""
from __future__ import annotations

import pandas as pd


def compute_rfm(
    orders: pd.DataFrame,
    *,
    customer_col: str,
    date_col: str,
    revenue_col: str,
    snapshot_date: pd.Timestamp | str | None = None,
    quintiles: int = 5,
) -> pd.DataFrame:
    """Return per-customer RFM scores 1..N (higher = better) plus a segment label."""
    if orders.empty:
        return pd.DataFrame(
            columns=[customer_col, "recency", "frequency", "monetary", "R", "F", "M", "RFM", "segment"]
        )

    work = orders.copy()
    work[date_col] = pd.to_datetime(work[date_col])
    snap = pd.Timestamp(snapshot_date) if snapshot_date else work[date_col].max()

    grouped = work.groupby(customer_col).agg(
        recency=(date_col, lambda s: (snap - s.max()).days),
        frequency=(customer_col, "size"),
        monetary=(revenue_col, "sum"),
    ).reset_index()

    grouped["R"] = _quantile_score(grouped["recency"], quintiles, ascending=False)
    grouped["F"] = _quantile_score(grouped["frequency"], quintiles, ascending=True)
    grouped["M"] = _quantile_score(grouped["monetary"], quintiles, ascending=True)
    grouped["RFM"] = grouped["R"] * 100 + grouped["F"] * 10 + grouped["M"]
    grouped["segment"] = grouped.apply(_segment_label, axis=1)
    return grouped


def _quantile_score(series: pd.Series, q: int, *, ascending: bool) -> pd.Series:
    """Score 1..q. ascending=True means higher value → higher score."""
    if series.nunique() <= 1:
        return pd.Series([q] * len(series), index=series.index, dtype=int)
    ranked = series.rank(method="first", ascending=ascending)
    binned = pd.qcut(ranked, q=q, labels=range(1, q + 1), duplicates="drop")
    return binned.astype(int)


def _segment_label(row: pd.Series) -> str:
    r, f, m = int(row["R"]), int(row["F"]), int(row["M"])
    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"
    if r >= 4 and f >= 3:
        return "Loyal"
    if r >= 4 and f <= 2:
        return "New / Promising"
    if r <= 2 and f >= 4:
        return "At Risk"
    if r <= 2 and f <= 2 and m >= 4:
        return "Big-Spender Lost"
    if r <= 2:
        return "Hibernating"
    return "Needs Attention"
