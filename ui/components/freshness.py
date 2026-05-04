from __future__ import annotations

import pandas as pd
import streamlit as st

from data.repository import DataRepository


def _format_age(delta: pd.Timedelta) -> str:
    days = int(delta.days)
    if days < 1:
        return "today"
    if days < 30:
        return f"{days}d ago"
    if days < 365:
        return f"{days // 30}mo ago"
    return f"{days // 365}y ago"


def render(repo: DataRepository) -> None:
    meta = repo.meta()
    age = pd.Timestamp("now").normalize() - pd.Timestamp(meta.data_max_date).normalize()
    is_stale = age.days > 7

    bg = "#fef2f2" if is_stale else "#f0fdf4"
    border = "#fecaca" if is_stale else "#bbf7d0"
    fg = "#991b1b" if is_stale else "#166534"
    label = "STALE" if is_stale else "OK"

    st.markdown(
        f"""
        <div style="display:flex; gap:14px; align-items:center; padding:8px 14px;
                    background:{bg}; border:1px solid {border}; border-radius:8px;
                    color:{fg}; font-size:13px; margin-bottom:14px;">
          <span style="font-weight:700;">DATA · {label}</span>
          <span>most recent record: <b>{meta.data_max_date.date()}</b> ({_format_age(age)})</span>
          <span style="color:#6b7280;">range: {meta.data_min_date.date()} → {meta.data_max_date.date()}</span>
          <span style="color:#6b7280;">rows: {meta.merged_row_count:,}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
