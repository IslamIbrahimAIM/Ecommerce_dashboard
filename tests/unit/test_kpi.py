from __future__ import annotations

import pandas as pd

from analytics.kpi import (
    abandonment_rate,
    abandonment_rate_total,
    aov,
    conversion_rate,
    median_order_value,
    metric_extremes,
    pareto_cumulative,
    pop_delta,
    prior_window,
    repeat_rate,
    rolling_mean,
)


def test_aov_basic():
    df = pd.DataFrame({"Orders": [2, 3], "Sales": [100.0, 150.0]})
    assert aov(df) == 50.0


def test_aov_zero_orders_returns_zero():
    df = pd.DataFrame({"Orders": [0], "Sales": [0.0]})
    assert aov(df) == 0.0


def test_median_order_value_robust_to_outliers():
    df = pd.DataFrame({"Orders": [1, 1, 1, 1], "Sales": [10.0, 12.0, 11.0, 1000.0]})
    # mean would be ~258, median should be ~11.5
    assert median_order_value(df) == 11.5


def test_conversion_rate():
    s = pd.DataFrame({"Sessions": [100, 200]})
    o = pd.DataFrame({"Orders": [3, 6]})
    assert conversion_rate(s, o) == 0.03


def test_repeat_rate(synth_customer_orders):
    assert 0 < repeat_rate(synth_customer_orders, customer_col="customer_id") <= 1


def test_abandonment_rate_per_row_no_precision_loss():
    df = pd.DataFrame({"Cart": [100, 0, 5], "Orders": [33, 0, 2]})
    out = abandonment_rate(df)
    # (100-33)/100 = 67% — no rounding precision loss
    assert out["Abandonment Rate"].tolist() == [67.0, 0.0, 60.0]


def test_abandonment_rate_clamps_negative_to_zero():
    df = pd.DataFrame({"Cart": [10], "Orders": [12]})  # data-quality oddity
    out = abandonment_rate(df)
    assert out["Abandonment Rate"].iloc[0] == 0.0


def test_abandonment_rate_total_aggregates_first():
    df = pd.DataFrame({"Cart": [100, 100], "Orders": [50, 90]})
    # naive average of per-row rates: (50 + 10)/2 = 30%
    # correct: (200 - 140) / 200 = 30% — happens to match here, but…
    df2 = pd.DataFrame({"Cart": [1, 1000], "Orders": [0, 999]})
    # naive avg: (100 + 0.1)/2 ≈ 50.05% — wrong
    # correct: (1001 - 999)/1001 ≈ 0.2%
    assert abs(abandonment_rate_total(df2) - 0.2) < 0.05


def test_pareto_cumulative_monotonic():
    df = pd.DataFrame({"x": list("abcde"), "v": [50, 30, 10, 5, 5]})
    out = pareto_cumulative(df, value_col="v")
    assert out["Cum_perc"].is_monotonic_increasing
    assert abs(out["Cum_perc"].iloc[-1] - 100.0) < 1e-6


def test_metric_extremes_returns_dates_and_values():
    df = pd.DataFrame({
        "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
        "Orders": [10, 50],
    })
    ext = metric_extremes(df, metric="Orders")
    assert ext["max"]["value"] == 50
    assert ext["min"]["value"] == 10
    assert ext["avg"] == 30
    assert ext["median"] == 30


def test_metric_extremes_empty():
    df = pd.DataFrame({"date": [], "Orders": []})
    ext = metric_extremes(df, metric="Orders")
    assert ext["min"] is None


# ----- pop_delta + prior_window ------------------------------------------

def test_pop_delta_up():
    d = pop_delta(110, 100)
    assert d.abs_delta == 10
    assert abs(d.pct_delta - 10.0) < 1e-9
    assert d.direction == "up"


def test_pop_delta_down():
    d = pop_delta(80, 100)
    assert d.direction == "down"
    assert abs(d.pct_delta - (-20.0)) < 1e-9


def test_pop_delta_flat_within_threshold():
    d = pop_delta(100.4, 100, flat_threshold_pct=0.5)
    assert d.direction == "flat"


def test_pop_delta_zero_prior():
    d = pop_delta(50, 0)
    assert d.pct_delta is None
    assert d.direction == "up"


def test_prior_window_immediately_precedes():
    p_start, p_end = prior_window("2024-01-08", "2024-01-14")
    # current span = 6 days, prior_end = day before start, prior_start = prior_end - 6
    assert p_end == pd.Timestamp("2024-01-07")
    assert p_start == pd.Timestamp("2024-01-01")


def test_rolling_mean_smoothes():
    s = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    rm = rolling_mean(s, window=3)
    # 3-day MA at index 2 = (1+2+3)/3 = 2.0
    assert rm.iloc[2] == 2.0
    # at index 9 = (8+9+10)/3 = 9.0
    assert rm.iloc[9] == 9.0
