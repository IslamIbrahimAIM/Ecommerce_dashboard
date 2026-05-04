"""Tier-1 KPI scorecard — five big numbers + PoP delta + Plotly sparkline INSIDE the card.

Renders the entire scorecard as one HTML/JS payload via streamlit.components.v1.html
so each card is a single DOM container holding label + value + delta + Plotly chart.
"""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass

import pandas as pd
import streamlit as st
import streamlit.components.v1 as st_components

from analytics.kpi import (
    PoPDelta,
    abandonment_rate_total,
    aov,
    conversion_rate,
    pop_delta,
    prior_window,
    rolling_mean,
)
from data.repository import DataRepository

_GREEN = "#16a34a"
_RED = "#dc2626"
_NEUTRAL = "#6b7280"
_DELTA_COLOR = {"up": _GREEN, "down": _RED, "flat": _NEUTRAL}
_DELTA_GLYPH = {"up": "▲", "down": "▼", "flat": "→"}

_PLOTLY_CDN = "https://cdn.plot.ly/plotly-2.35.2.min.js"


@dataclass(frozen=True)
class KpiCard:
    label: str
    value: str
    delta: PoPDelta
    sparkline_values: list[float]
    higher_is_better: bool = True


# ----- formatters ----------------------------------------------------------

def _fmt_money(x: float) -> str:
    if x >= 1_000_000:
        return f"${x/1_000_000:.2f}M"
    if x >= 1_000:
        return f"${x/1_000:.1f}K"
    return f"${x:,.0f}"


def _fmt_int(x: float) -> str:
    if x >= 1_000_000:
        return f"{x/1_000_000:.2f}M"
    if x >= 1_000:
        return f"{x/1_000:.1f}K"
    return f"{x:,.0f}"


def _fmt_pct(x: float) -> str:
    return f"{x:.2f}%"


# ----- delta badge ---------------------------------------------------------

def _delta_badge(d: PoPDelta, higher_is_better: bool) -> tuple[str, str]:
    glyph = _DELTA_GLYPH[d.direction]
    if d.pct_delta is None:
        return glyph + " new", _DELTA_COLOR[d.direction]
    text = f"{glyph} {abs(d.pct_delta):.1f}%"
    if d.direction == "flat":
        color = _NEUTRAL
    else:
        good = (d.direction == "up") == higher_is_better
        color = _GREEN if good else _RED
    return text, color


# ----- HTML payload --------------------------------------------------------

def _scorecard_html(cards: list[KpiCard]) -> str:
    """One HTML/JS payload that embeds Plotly sparklines INSIDE each card."""
    card_html_parts: list[str] = []
    plot_init_parts: list[str] = []

    for card in cards:
        delta_text, delta_color = _delta_badge(card.delta, card.higher_is_better)
        chart_id = f"spark-{uuid.uuid4().hex[:10]}"
        card_html_parts.append(f"""
            <div class="kpi-card">
              <div class="kpi-label">{card.label}</div>
              <div class="kpi-value">{card.value}</div>
              <div class="kpi-delta" style="color:{delta_color};">
                {delta_text}<span class="kpi-vs"> vs prior</span>
              </div>
              <div class="kpi-spark" id="{chart_id}"></div>
            </div>
        """)
        # Plotly trace + minimalist layout
        trace = {
            "y": list(card.sparkline_values),
            "type": "scatter",
            "mode": "lines",
            "line": {"color": delta_color, "width": 2, "shape": "spline"},
            "hoverinfo": "skip",
            "fill": "tozeroy",
            "fillcolor": delta_color + "22",
        }
        layout = {
            "margin": {"l": 0, "r": 0, "t": 4, "b": 0},
            "height": 44,
            "xaxis": {"visible": False, "fixedrange": True},
            "yaxis": {"visible": False, "fixedrange": True},
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "showlegend": False,
        }
        plot_init_parts.append(
            f"Plotly.newPlot('{chart_id}', "
            f"{json.dumps([trace])}, "
            f"{json.dumps(layout)}, "
            f"{{displayModeBar: false, staticPlot: true, responsive: true}});"
        )

    cards_html = "\n".join(card_html_parts)
    init_js = "\n".join(plot_init_parts)

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body, html {{ margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                   Helvetica, Arial, sans-serif; }}
  .kpi-row {{ display: grid; grid-template-columns: repeat({len(cards)}, 1fr);
             gap: 12px; padding: 0; }}
  .kpi-card {{ border: 1px solid #e5e7eb; border-radius: 10px;
              padding: 14px 16px 8px 16px; background: white;
              box-shadow: 0 1px 2px rgba(0,0,0,0.03);
              display: flex; flex-direction: column; min-height: 130px; }}
  .kpi-label {{ font-size: 11px; color: #6b7280; letter-spacing: 0.06em;
               text-transform: uppercase; font-weight: 600; }}
  .kpi-value {{ font-size: 28px; font-weight: 700; color: #111827;
               margin-top: 4px; line-height: 1.1; }}
  .kpi-delta {{ font-size: 13px; font-weight: 600; margin-top: 2px; }}
  .kpi-vs    {{ color: #9ca3af; font-weight: 400; margin-left: 4px; }}
  .kpi-spark {{ flex: 1; min-height: 44px; margin-top: 6px; }}
</style>
<script src="{_PLOTLY_CDN}"></script>
</head>
<body>
  <div class="kpi-row">
    {cards_html}
  </div>
<script>
  function init() {{
    if (typeof Plotly === 'undefined') {{ setTimeout(init, 50); return; }}
    {init_js}
  }}
  init();
</script>
</body>
</html>
"""


# ----- public API ----------------------------------------------------------

def render(repo: DataRepository, *, start, end) -> None:
    current = repo.daily_overall(start, end)
    if current.empty:
        st.info("No data in the selected range.")
        return

    prior_s, prior_e = prior_window(start, end)
    prior = repo.daily_overall(prior_s, prior_e)

    cur_total = current[["Sessions", "Cart", "Orders", "Sales"]].sum()
    prior_total = (
        prior[["Sessions", "Cart", "Orders", "Sales"]].sum()
        if not prior.empty
        else pd.Series({"Sessions": 0, "Cart": 0, "Orders": 0, "Sales": 0})
    )

    spark = (
        current.groupby("date", observed=False)[["Sessions", "Cart", "Orders", "Sales"]]
        .sum().sort_index()
    )

    cards: list[KpiCard] = [
        KpiCard(
            label="Sales",
            value=_fmt_money(cur_total["Sales"]),
            delta=pop_delta(cur_total["Sales"], prior_total["Sales"]),
            sparkline_values=rolling_mean(spark["Sales"]).tolist(),
        ),
        KpiCard(
            label="Orders",
            value=_fmt_int(cur_total["Orders"]),
            delta=pop_delta(cur_total["Orders"], prior_total["Orders"]),
            sparkline_values=rolling_mean(spark["Orders"]).tolist(),
        ),
        KpiCard(
            label="AOV",
            value=_fmt_money(aov(current)),
            delta=pop_delta(aov(current), aov(prior) if not prior.empty else 0.0),
            sparkline_values=(spark["Sales"] / spark["Orders"].replace(0, pd.NA))
                .fillna(0).tolist(),
        ),
        KpiCard(
            label="Session CR",
            value=_fmt_pct(conversion_rate(current, current) * 100),
            delta=pop_delta(
                conversion_rate(current, current) * 100,
                (conversion_rate(prior, prior) * 100) if not prior.empty else 0.0,
            ),
            sparkline_values=(
                (spark["Orders"] / spark["Sessions"].replace(0, pd.NA)) * 100
            ).fillna(0).tolist(),
        ),
        KpiCard(
            label="Abandonment",
            value=_fmt_pct(abandonment_rate_total(current)),
            delta=pop_delta(
                abandonment_rate_total(current),
                abandonment_rate_total(prior) if not prior.empty else 0.0,
            ),
            sparkline_values=(
                ((spark["Cart"] - spark["Orders"]).clip(lower=0)
                 / spark["Cart"].replace(0, pd.NA)) * 100
            ).fillna(0).tolist(),
            higher_is_better=False,
        ),
    ]

    # One HTML payload; ~155px tall fits all 5 cards including sparklines.
    st_components.html(_scorecard_html(cards), height=170)
