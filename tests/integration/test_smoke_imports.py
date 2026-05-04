"""Smoke test: every package in the project must import without side effects.

If a module reads a file or pings a service at import time, this test catches it.
"""
from __future__ import annotations

import importlib

import pytest

PURE_MODULES = [
    "analytics.aggregations",
    "analytics.brand_eval",
    "analytics.basket",
    "analytics.clv",
    "analytics.cohort",
    "analytics.funnel",
    "analytics.kpi",
    "analytics.markov",
    "analytics.rfm",
    "analytics.timeseries",
    "charts.palettes",
    "charts.plotly_backend",
    "charts.chartjs_backend",
    "charts.port",
    "data.repository",
    "data.duckdb_repo",
    "data.memory_repo",
    "infra.config",
    "infra.mailer",
]


@pytest.mark.parametrize("name", PURE_MODULES)
def test_module_imports_clean(name: str) -> None:
    importlib.import_module(name)
