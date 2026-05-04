from __future__ import annotations

import os
from pathlib import Path

from infra.config import load_config


def test_load_config_uses_env_vars(monkeypatch, tmp_path):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("SMTP_SERVER", "smtp.example")
    monkeypatch.setenv("SMTP_PORT", "2525")
    monkeypatch.setenv("SMTP_USERNAME", "user")
    monkeypatch.setenv("SMTP_PASSWORD", "pw")
    monkeypatch.setenv("CHART_BACKEND", "chartjs")
    cfg = load_config()
    assert cfg.data_dir == Path(os.environ["DATA_DIR"])
    assert cfg.smtp.server == "smtp.example"
    assert cfg.smtp.port == 2525
    assert cfg.smtp.is_configured
    assert cfg.chart_backend == "chartjs"


def test_default_chart_backend_is_plotly(monkeypatch):
    monkeypatch.delenv("CHART_BACKEND", raising=False)
    assert load_config().chart_backend == "plotly"


def test_smtp_unconfigured_when_missing(monkeypatch):
    for k in ("SMTP_SERVER", "SMTP_USERNAME", "SMTP_PASSWORD"):
        monkeypatch.delenv(k, raising=False)
    cfg = load_config()
    assert not cfg.smtp.is_configured
