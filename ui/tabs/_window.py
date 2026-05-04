"""Shared default-window helper used by every synth-using tab.

Synth/Apriori on the full month creates tens of millions of rows; default
to last 7 days so first paint stays responsive. User can widen via the
date pickers.
"""
from __future__ import annotations

import pandas as pd


def default_window(range_min: pd.Timestamp, range_max: pd.Timestamp, *, days: int = 7) -> tuple:
    end = pd.Timestamp(range_max)
    span = end - pd.Timestamp(range_min)
    n = min(days, max(span.days, 0))
    start = end - pd.Timedelta(days=n)
    return start.date(), end.date()
