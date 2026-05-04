from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Any, Literal, Protocol

import pandas as pd

RenderableKind = Literal["plotly", "html"]


@dataclass(frozen=True)
class Renderable:
    """A chart payload that the page renders via Streamlit."""

    kind: RenderableKind
    payload: Any  # plotly.graph_objects.Figure | str (html)
    config: dict[str, Any] | None = None

    def render(self, st_module: Any) -> None:
        if self.kind == "plotly":
            st_module.plotly_chart(self.payload, use_container_width=True, config=self.config or {})
        elif self.kind == "html":
            import streamlit.components.v1 as components

            components.html(self.payload, height=(self.config or {}).get("height", 500))
        else:
            raise ValueError(f"Unknown Renderable.kind={self.kind}")


class ChartPort(Protocol):
    def funnel(
        self,
        data: dict[str, list],
        *,
        title: str,
        palette: Sequence[str] | None = None,
        hide_yaxis: bool = False,
    ) -> Renderable: ...

    def grouped_bar(
        self,
        df: pd.DataFrame,
        *,
        x: str,
        y: str,
        color: str,
        title: str,
        palette: Sequence[str] | None = None,
    ) -> Renderable: ...

    def scatter(
        self,
        df: pd.DataFrame,
        *,
        x: str,
        y: str,
        color: str | None = None,
        size: str | None = None,
        hover: Iterable[str] | None = None,
        title: str,
        palette: Sequence[str] | None = None,
    ) -> Renderable: ...

    def line(
        self,
        df: pd.DataFrame,
        *,
        x: str,
        y: str,
        title: str,
        color: str | None = None,
    ) -> Renderable: ...

    def pareto(
        self,
        df: pd.DataFrame,
        *,
        x: str,
        bar_y: str,
        line_y: str,
        title: str,
    ) -> Renderable: ...

    def heatmap(
        self,
        df: pd.DataFrame,
        *,
        title: str,
        colorscale: str = "Blues",
    ) -> Renderable: ...
