from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

DEFAULT_FUNNEL_STAGES: tuple[str, ...] = (
    "Total_Sessions",
    "Total_Views",
    "Total_Cart",
    "Total_Orders",
)

STAGE_LABELS = {
    "Total_Sessions": "Total Sessions",
    "Total_Views": "Total Views",
    "Total_Cart": "Total Cart",
    "Total_Orders": "Total Orders",
}


def funnel_summary(
    df: pd.DataFrame,
    *,
    stages: Iterable[str] = DEFAULT_FUNNEL_STAGES,
    labels: dict[str, str] | None = None,
) -> dict[str, list]:
    """Return {'stage': [...], 'number': [...]} ready for px.funnel / Chart.js."""
    stages = list(stages)
    label_map = {**STAGE_LABELS, **(labels or {})}
    return {
        "stage": [label_map.get(s, s) for s in stages],
        "number": [int(df[s].sum()) if s in df.columns else 0 for s in stages],
    }


def is_empty(funnel: dict[str, list]) -> bool:
    return all(v == 0 for v in funnel.get("number", []))


def split_by_user_type(
    df: pd.DataFrame,
    user_type_col: str = "user_type",
) -> dict[str, pd.DataFrame]:
    """Slice once into {value: subframe} for every distinct user_type."""
    return {ut: df[df[user_type_col] == ut].copy() for ut in df[user_type_col].unique()}
