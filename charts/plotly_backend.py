from __future__ import annotations

from collections.abc import Iterable, Sequence

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from charts.palettes import CHART_CONFIG
from charts.port import Renderable


class PlotlyChart:
    def funnel(self, data, *, title, palette=None, hide_yaxis=False):
        fig = px.funnel(data, x="number", y="stage", color_discrete_sequence=list(palette) if palette else None)
        layout = {"title": {"text": title, "x": 0.5, "xanchor": "center"}}
        if hide_yaxis:
            layout["yaxis"] = {"visible": False}
        fig.update_layout(**layout)
        return Renderable("plotly", fig, CHART_CONFIG)

    def grouped_bar(self, df, *, x, y, color, title, palette=None):
        fig = px.bar(
            df, x=x, y=y, color=color,
            color_discrete_sequence=list(palette) if palette else None,
            barmode="group",
            height=500,
        )
        fig.update_layout(showlegend=False, title={"text": title, "x": 0.5, "xanchor": "center"})
        fig.update_traces(texttemplate="%{y:.2s}", textposition="outside")
        return Renderable("plotly", fig, CHART_CONFIG)

    def scatter(
        self,
        df,
        *,
        x,
        y,
        color=None,
        size=None,
        hover: Iterable[str] | None = None,
        title,
        palette: Sequence[str] | None = None,
    ):
        fig = px.scatter(
            df, x=x, y=y, color=color, size=size,
            hover_data=list(hover) if hover else None,
            color_discrete_sequence=list(palette) if palette else None,
            title=title,
        )
        return Renderable("plotly", fig, CHART_CONFIG)

    def line(self, df, *, x, y, title, color=None):
        fig = px.line(df, x=x, y=y, color=color, title=title)
        return Renderable("plotly", fig, CHART_CONFIG)

    def pareto(self, df, *, x, bar_y, line_y, title):
        fig = px.bar(df, x=x, y=bar_y, title=title)
        fig.add_scatter(x=df[x], y=df[line_y], yaxis="y2", mode="lines+markers", name="Cumulative %")
        fig.update_layout(
            yaxis2={
                "title": "Cumulative Percentage",
                "overlaying": "y",
                "side": "right",
                "tickmode": "array",
                "tickvals": [i * 10 for i in range(11)],
                "ticktext": [f"{i * 10}%" for i in range(11)],
                "showgrid": False,
            }
        )
        fig.update_traces(texttemplate="%{y:.2s}", textposition="outside", selector={"type": "bar"})
        return Renderable("plotly", fig, CHART_CONFIG)

    def heatmap(self, df: pd.DataFrame, *, title, colorscale="Blues"):
        fig = go.Figure(
            data=go.Heatmap(
                z=df.values,
                x=[str(c) for c in df.columns],
                y=[str(i) for i in df.index],
                colorscale=colorscale,
            )
        )
        fig.update_layout(title={"text": title, "x": 0.5, "xanchor": "center"})
        return Renderable("plotly", fig, CHART_CONFIG)
