"""Composition root.

Owns wiring: build config → repository → chart port → mailers → mount tabs.
No business logic here.
"""
from __future__ import annotations

import streamlit as st

from charts.chartjs_backend import ChartJsChart
from charts.plotly_backend import PlotlyChart
from charts.port import ChartPort
from data.duckdb_repo import DuckDBRepository
from infra.config import AppConfig, load_config
from infra.mailer import Mailer, NoopMailer, SmtpMailer
from ui import apply_chrome, set_page_config
from ui.components import contact_form, freshness
from ui.tabs import all_tabs


def _chart_port(config: AppConfig) -> ChartPort:
    return ChartJsChart() if config.chart_backend == "chartjs" else PlotlyChart()


def _mailer(smtp_config) -> Mailer:
    return SmtpMailer(smtp_config) if smtp_config.is_configured else NoopMailer()


def _footer(config: AppConfig) -> None:
    st.markdown(
        f"""
        <div style="margin-top:32px; padding-top:14px; border-top:1px solid #e5e7eb;
                    color:#6b7280; font-size:12px; display:flex; justify-content:space-between;">
            <span>Ecom-Dashboard · built by <a href="{config.linkedin_url}" target="_blank"
                  style="color:#6b7280; text-decoration:none; border-bottom:1px dotted #9ca3af;">
                  Islam Ibrahim</a></span>
            <span>Streamlit · DuckDB · Plotly · deployed on Hugging Face Spaces</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    # set_page_config MUST be the first Streamlit call (before anything that
    # might touch st.secrets / st.* — load_config() does as a fallback).
    set_page_config()
    config = load_config()
    apply_chrome(config)

    repo = DuckDBRepository(config.parquet_dir)
    charts = _chart_port(config)

    freshness.render(repo)
    contact_form.render(
        config=config,
        inbound_mailer=_mailer(config.smtp),
        autoreply_mailer=_mailer(config.google_smtp),
    )

    tabs = all_tabs()
    for tab_widget, tab in zip(st.tabs([t.title for t in tabs]), tabs, strict=False):
        with tab_widget:
            tab.render(repo, charts, config)

    _footer(config)


if __name__ == "__main__":
    main()
