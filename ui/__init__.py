from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as st_components

from infra.config import AppConfig

_NO_SIDEBAR_CSS = """
<style>
    div[data-testid="stSidebarNav"] {display: none;}
    div.block-container {padding-top: 1rem;}
</style>
"""


def set_page_config() -> None:
    """Must be the very first Streamlit call in the script — call before load_config()."""
    st.set_page_config(
        layout="wide",
        page_title="Ecom-Dashboard",
        initial_sidebar_state="collapsed",
    )


def apply_chrome(config: AppConfig) -> None:
    """Inject sidebar-hiding CSS, GA snippet, and the project stylesheet."""
    st.markdown(_NO_SIDEBAR_CSS, unsafe_allow_html=True)

    ga_html = config.ga_snippet_path.read_text() if config.ga_snippet_path.exists() else ""
    if ga_html:
        st_components.html(ga_html, height=0)

    if config.styles_path.exists():
        st.markdown(f"<style>{config.styles_path.read_text()}</style>", unsafe_allow_html=True)
