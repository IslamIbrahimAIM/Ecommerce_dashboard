from __future__ import annotations

import pandas as pd

from charts.chartjs_backend import ChartJsChart
from charts.plotly_backend import PlotlyChart


def _df():
    return pd.DataFrame({"x": ["a", "b"], "y": [1, 2], "g": ["g1", "g2"]})


def test_plotly_funnel_returns_plotly_kind():
    out = PlotlyChart().funnel({"stage": ["A"], "number": [1]}, title="t")
    assert out.kind == "plotly"


def test_chartjs_funnel_returns_html():
    out = ChartJsChart().funnel({"stage": ["A"], "number": [1]}, title="t")
    assert out.kind == "html"
    assert "<canvas" in out.payload
    assert "chart.js" in out.payload.lower()


def test_chartjs_grouped_bar_html_contains_canvas():
    out = ChartJsChart().grouped_bar(_df(), x="x", y="y", color="g", title="t")
    assert out.kind == "html"
    assert "<canvas" in out.payload


def test_plotly_pareto_dual_axis():
    df = pd.DataFrame({"x": list("abcd"), "v": [40, 30, 20, 10], "c": [40, 70, 90, 100]})
    out = PlotlyChart().pareto(df, x="x", bar_y="v", line_y="c", title="P")
    assert out.kind == "plotly"
