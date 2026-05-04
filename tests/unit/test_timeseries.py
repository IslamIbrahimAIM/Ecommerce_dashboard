from __future__ import annotations

import numpy as np
import pandas as pd

from analytics.timeseries import decompose, trend_with_extremes


def test_trend_with_extremes_runs_and_finds_outlier():
    rng = pd.date_range("2024-01-01", periods=30, freq="D")
    base = np.linspace(10, 20, 30) + np.random.RandomState(0).normal(0, 0.5, 30)
    base[15] += 50  # injected outlier
    df = pd.DataFrame({"date": rng, "Orders": base})
    res = trend_with_extremes(df, x_col="date", y_col="Orders")
    assert res.fitted_y is not None
    assert len(res.extreme_points) >= 1


def test_trend_with_extremes_empty():
    df = pd.DataFrame({"date": [], "Orders": []})
    res = trend_with_extremes(df, x_col="date", y_col="Orders")
    assert res.fitted_y is None
    assert res.extreme_points.empty


def test_decompose_returns_components():
    rng = pd.date_range("2024-01-01", periods=24, freq="ME")
    series = pd.Series(np.sin(np.linspace(0, 4 * np.pi, 24)) + np.linspace(0, 5, 24), index=rng)
    out = decompose(series, period=12)
    assert {"trend", "seasonal", "resid", "observed"} <= set(out.keys())
