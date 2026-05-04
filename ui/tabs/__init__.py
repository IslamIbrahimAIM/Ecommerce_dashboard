from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from charts.port import ChartPort
from data.repository import DataRepository
from infra.config import AppConfig


@dataclass(frozen=True)
class Tab:
    title: str
    render: Callable[[DataRepository, ChartPort, AppConfig], None]


def all_tabs() -> list[Tab]:
    from ui.tabs import (
        basket,
        clv,
        cohort,
        dashboard,
        markov,
        rfm,
        timeseries,
        univariate,
    )

    return [
        Tab("Ecom Dashboard", dashboard.render),
        Tab("Time Series", timeseries.render),
        Tab("Funnel Markov", markov.render),
        Tab("RFM", rfm.render),
        Tab("Cohort", cohort.render),
        Tab("CLV", clv.render),
        Tab("Basket (Apriori)", basket.render),
        Tab("Univariate", univariate.render),
    ]
