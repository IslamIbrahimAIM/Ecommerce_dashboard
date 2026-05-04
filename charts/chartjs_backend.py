"""Chart.js backend — emits HTML payloads with the Chart.js CDN.

Coexists with the Plotly backend behind the same `ChartPort` Protocol. Some
Plotly-specific chart types (funnel, lowess trendlines, dual-axis pareto)
have no clean Chart.js equivalent — those fall back to a horizontal bar.
"""
from __future__ import annotations

import json
from collections.abc import Iterable, Sequence

import pandas as pd

from charts.port import Renderable

CDN_SCRIPT = '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4"></script>'


def _canvas_html(canvas_id: str, config: dict, *, height: int = 480) -> str:
    cfg = json.dumps(config, default=str)
    return f"""
<div style="position:relative;height:{height}px;">
  <canvas id="{canvas_id}"></canvas>
</div>
{CDN_SCRIPT}
<script>
(function() {{
  const ctx = document.getElementById("{canvas_id}");
  if (!ctx) return;
  new Chart(ctx, {cfg});
}})();
</script>
"""


def _new_id(prefix: str) -> str:
    import uuid

    return f"{prefix}-{uuid.uuid4().hex[:8]}"


class ChartJsChart:
    def funnel(self, data, *, title, palette=None, hide_yaxis=False):
        config = {
            "type": "bar",
            "data": {
                "labels": data.get("stage", []),
                "datasets": [
                    {
                        "label": title,
                        "data": data.get("number", []),
                        "backgroundColor": list(palette) if palette else "#00d4ff",
                    }
                ],
            },
            "options": {
                "indexAxis": "y",
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {"title": {"display": True, "text": title}, "legend": {"display": False}},
                "scales": {"y": {"display": not hide_yaxis}},
            },
        }
        return Renderable("html", _canvas_html(_new_id("funnel"), config), {"height": 500})

    def grouped_bar(self, df, *, x, y, color, title, palette=None):
        labels = list(df[x].astype(str).unique())
        groups = list(df[color].astype(str).unique())
        palette = list(palette) if palette else ["#a6cee3", "#1f78b4", "#b2df8a"]
        datasets = []
        for i, g in enumerate(groups):
            sub = df[df[color].astype(str) == g]
            values = [float(sub.loc[sub[x].astype(str) == lbl, y].sum()) for lbl in labels]
            datasets.append({"label": g, "data": values, "backgroundColor": palette[i % len(palette)]})
        config = {
            "type": "bar",
            "data": {"labels": labels, "datasets": datasets},
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {"title": {"display": True, "text": title}},
            },
        }
        return Renderable("html", _canvas_html(_new_id("bar"), config), {"height": 500})

    def scatter(self, df, *, x, y, color=None, size=None, hover: Iterable[str] | None = None, title, palette: Sequence[str] | None = None):
        points = [{"x": str(row[x]), "y": float(row[y])} for _, row in df.iterrows()]
        config = {
            "type": "scatter",
            "data": {"datasets": [{"label": title, "data": points, "backgroundColor": (list(palette) or ["#00d4ff"])[0]}]},
            "options": {"responsive": True, "maintainAspectRatio": False, "plugins": {"title": {"display": True, "text": title}}},
        }
        return Renderable("html", _canvas_html(_new_id("scatter"), config), {"height": 500})

    def line(self, df: pd.DataFrame, *, x, y, title, color=None):
        config = {
            "type": "line",
            "data": {
                "labels": df[x].astype(str).tolist(),
                "datasets": [{"label": y, "data": df[y].astype(float).tolist(), "borderColor": "#00d4ff", "fill": False}],
            },
            "options": {"responsive": True, "maintainAspectRatio": False, "plugins": {"title": {"display": True, "text": title}}},
        }
        return Renderable("html", _canvas_html(_new_id("line"), config), {"height": 500})

    def pareto(self, df, *, x, bar_y, line_y, title):
        config = {
            "type": "bar",
            "data": {
                "labels": df[x].astype(str).tolist(),
                "datasets": [
                    {"type": "bar", "label": bar_y, "data": df[bar_y].astype(float).tolist(), "backgroundColor": "#1f78b4", "yAxisID": "y"},
                    {"type": "line", "label": line_y, "data": df[line_y].astype(float).tolist(), "borderColor": "#e31a1c", "fill": False, "yAxisID": "y2"},
                ],
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {"title": {"display": True, "text": title}},
                "scales": {
                    "y": {"position": "left", "beginAtZero": True},
                    "y2": {"position": "right", "beginAtZero": True, "grid": {"drawOnChartArea": False}, "max": 100},
                },
            },
        }
        return Renderable("html", _canvas_html(_new_id("pareto"), config), {"height": 500})

    def heatmap(self, df: pd.DataFrame, *, title, colorscale="Blues"):
        # Chart.js core doesn't ship a heatmap; render as a stacked-bar approximation.
        labels = [str(i) for i in df.index]
        datasets = [
            {"label": str(c), "data": [float(v) for v in df[c].tolist()]}
            for c in df.columns
        ]
        config = {
            "type": "bar",
            "data": {"labels": labels, "datasets": datasets},
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {"title": {"display": True, "text": title + " (stacked-bar fallback)"}},
                "scales": {"x": {"stacked": True}, "y": {"stacked": True}},
            },
        }
        return Renderable("html", _canvas_html(_new_id("heatmap"), config), {"height": 500})
