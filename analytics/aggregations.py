from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from data.repository import DATE


def aggregate(
    df: pd.DataFrame,
    *,
    by: list[str],
    metrics: Iterable[str] | None = None,
    prefix: str = "",
) -> pd.DataFrame:
    """Sum-aggregate `metrics` (or every numeric column) over `by` keys."""
    if metrics is None:
        metrics = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    metrics = list(metrics)
    out = df.groupby(by, observed=False)[metrics].sum().reset_index()
    if prefix:
        out = out.rename(columns={m: f"{prefix}{m}" for m in metrics})
    return out


def filter_by_date(
    df: pd.DataFrame,
    start: pd.Timestamp | str,
    end: pd.Timestamp | str,
    *,
    date_col: str = DATE,
) -> pd.DataFrame:
    """Inclusive date-range filter; coerces `date_col` to datetime if needed."""
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    out = df.copy()
    out[date_col] = pd.to_datetime(out[date_col])
    if start_ts == end_ts:
        return out[out[date_col] == start_ts].copy()
    return out[(out[date_col] >= start_ts) & (out[date_col] <= end_ts)].copy()


def by_period(
    df: pd.DataFrame,
    *,
    period: str = "D",
    extra_keys: Iterable[str] = (),
    metrics: Iterable[str] | None = None,
    date_col: str = DATE,
    prefix: str = "Total_",
) -> pd.DataFrame:
    """Group by date-period bucket + extra keys; sum metrics; restore date column."""
    work = df.copy()
    work[date_col] = pd.to_datetime(work[date_col])
    keys: list = [work[date_col].dt.to_period(period), *extra_keys]
    metrics = list(metrics) if metrics is not None else [
        c for c in work.columns
        if pd.api.types.is_numeric_dtype(work[c]) and c not in extra_keys
    ]
    grouped = work.groupby(keys, observed=False)[metrics].sum().reset_index()
    grouped = grouped.rename(columns={metrics[i]: f"{prefix}{m}" for i, m in enumerate(metrics)})
    grouped[date_col] = grouped[date_col].dt.to_timestamp().dt.date
    return grouped


def auto_period(num_days: int) -> str:
    if num_days < 7:
        return "D"
    if num_days < 30:
        return "W"
    return "M"


def previous_period_bounds(
    start: pd.Timestamp | str,
    num_days: int,
    *,
    period: str,
) -> tuple[pd.Timestamp, pd.Timestamp]:
    start_ts = pd.Timestamp(start)
    if period == "D":
        prev_start = start_ts - pd.DateOffset(days=num_days + 1)
    elif period == "W":
        prev_start = start_ts - pd.DateOffset(weeks=num_days // 7 + 1)
    else:
        prev_start = start_ts - pd.DateOffset(months=num_days // 30 + 1)
    prev_end = start_ts - pd.DateOffset(days=1)
    return prev_start, prev_end
