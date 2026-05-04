from __future__ import annotations

import pandas as pd

from analytics.aggregations import (
    aggregate,
    auto_period,
    by_period,
    filter_by_date,
    previous_period_bounds,
)


def test_aggregate_sums_by_keys(synth_sessions):
    out = aggregate(synth_sessions, by=["category"], metrics=["Sessions"])
    assert set(out.columns) == {"category", "Sessions"}
    assert int(out.loc[out["category"] == "electronics", "Sessions"].iloc[0]) == 180
    assert int(out.loc[out["category"] == "fashion", "Sessions"].iloc[0]) == 210


def test_aggregate_prefix(synth_sessions):
    out = aggregate(synth_sessions, by=["category"], metrics=["Sessions"], prefix="Total_")
    assert "Total_Sessions" in out.columns


def test_aggregate_default_metrics_picks_numeric(synth_sessions):
    out = aggregate(synth_sessions, by=["category"])
    assert "Sessions" in out.columns and "Views" in out.columns


def test_filter_by_date_range(synth_sessions):
    out = filter_by_date(synth_sessions, "2024-01-01", "2024-01-01")
    assert len(out) == 2
    assert out["date"].dt.date.unique().tolist() == [pd.Timestamp("2024-01-01").date()]


def test_filter_by_date_inclusive(synth_sessions):
    out = filter_by_date(synth_sessions, "2024-01-01", "2024-01-02")
    assert len(out) == 4


def test_by_period_daily(synth_sessions):
    out = by_period(synth_sessions, period="D", extra_keys=["user_type"], metrics=["Sessions"])
    assert "Total_Sessions" in out.columns
    assert len(out) == 4


def test_auto_period_thresholds():
    assert auto_period(3) == "D"
    assert auto_period(15) == "W"
    assert auto_period(60) == "M"


def test_previous_period_bounds_daily():
    start = pd.Timestamp("2024-02-10")
    prev_start, prev_end = previous_period_bounds(start, num_days=5, period="D")
    assert prev_end == start - pd.DateOffset(days=1)
    assert prev_start == start - pd.DateOffset(days=6)
