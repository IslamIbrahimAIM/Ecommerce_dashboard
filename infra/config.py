from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


ChartBackend = Literal["plotly", "chartjs"]


@dataclass(frozen=True)
class SmtpConfig:
    server: str
    port: int
    username: str
    password: str

    @property
    def is_configured(self) -> bool:
        return bool(self.server and self.username and self.password)


@dataclass(frozen=True)
class AppConfig:
    project_root: Path
    data_dir: Path
    parquet_dir: Path
    styles_path: Path
    ga_snippet_path: Path
    ga_tracking_id: str | None
    linkedin_url: str
    contact_receiver: str
    contact_sender_display: str
    smtp: SmtpConfig
    google_smtp: SmtpConfig
    chart_backend: ChartBackend


_SECRETS_PATHS = (Path("/root/.streamlit/secrets.toml"), Path("/app/.streamlit/secrets.toml"))


def _streamlit_secrets_available() -> bool:
    return any(p.exists() for p in _SECRETS_PATHS)


def _get(key: str, default: str | None = None) -> str | None:
    val = os.environ.get(key)
    if val:
        return val
    # Only fall back to st.secrets if a secrets file actually exists — otherwise
    # accessing st.secrets emits user-visible "No secrets files found" warnings
    # to the rendered page, once per key.
    if not _streamlit_secrets_available():
        return default
    try:
        import streamlit as st

        if key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return default


def _smtp_from_env(prefix: str) -> SmtpConfig:
    return SmtpConfig(
        server=_get(f"{prefix}_SERVER", "") or "",
        port=int(_get(f"{prefix}_PORT", "587") or 587),
        username=_get(f"{prefix}_USERNAME", "") or "",
        password=_get(f"{prefix}_PASSWORD", "") or "",
    )


def load_config(project_root: Path | None = None) -> AppConfig:
    root = project_root or Path(__file__).resolve().parent.parent
    data_dir = Path(_get("DATA_DIR") or (root / "data"))
    parquet_dir = data_dir / "parquet"

    backend_raw = (_get("CHART_BACKEND", "plotly") or "plotly").lower()
    backend: ChartBackend = "chartjs" if backend_raw == "chartjs" else "plotly"

    return AppConfig(
        project_root=root,
        data_dir=data_dir,
        parquet_dir=parquet_dir,
        styles_path=root / "assets" / "styles.css",
        ga_snippet_path=root / "assets" / "google_analytics.html",
        ga_tracking_id=_get("GA_TRACKING_ID"),
        linkedin_url=_get("LINKEDIN_URL", "https://www.linkedin.com/in/islamabdallam/")
        or "https://www.linkedin.com/in/islamabdallam/",
        contact_receiver=_get("CONTACT_RECEIVER_EMAIL", "innovativesolutions.989@gmail.com")
        or "innovativesolutions.989@gmail.com",
        contact_sender_display=_get("CONTACT_SENDER_DISPLAY", "Private Person <mailtrap@demomailtrap.com>")
        or "Private Person <mailtrap@demomailtrap.com>",
        smtp=_smtp_from_env("SMTP"),
        google_smtp=_smtp_from_env("GOOGLE_SMTP"),
        chart_backend=backend,
    )
