from __future__ import annotations

import pandas as pd

from data.repository import (
    BRAND,
    CART_METRICS,
    CATEGORY,
    DATE,
    GROUP_KEYS,
    ORDERS_METRICS,
    SESSIONS_METRICS,
    USER_TYPE,
    DataMeta,
)


class InMemoryRepository:
    """Test double — minimal implementation against in-memory DataFrames."""

    def __init__(self, sessions: pd.DataFrame, cart: pd.DataFrame, orders: pd.DataFrame) -> None:
        self._sessions = sessions.copy()
        self._cart = cart.copy()
        self._orders = orders.copy()
        for df in (self._sessions, self._cart, self._orders):
            if DATE in df.columns:
                df[DATE] = pd.to_datetime(df[DATE])

    def sessions(self) -> pd.DataFrame: return self._sessions
    def cart(self) -> pd.DataFrame:     return self._cart
    def orders(self) -> pd.DataFrame:   return self._orders

    @staticmethod
    def _agg(df: pd.DataFrame, metrics: list[str]) -> pd.DataFrame:
        keys = [DATE, USER_TYPE, CATEGORY, BRAND]
        present = [m for m in metrics if m in df.columns]
        return df.groupby(keys, observed=False)[present].sum().reset_index()

    def _compute_merged(self) -> pd.DataFrame:
        s = self._agg(self._sessions, SESSIONS_METRICS)
        c = self._agg(self._cart, CART_METRICS)
        o = self._agg(self._orders, ORDERS_METRICS)
        return s.merge(c, on=GROUP_KEYS, how="outer").merge(o, on=GROUP_KEYS, how="outer")

    def merged(self, start=None, end=None) -> pd.DataFrame:
        out = self._compute_merged()
        out[DATE] = pd.to_datetime(out[DATE])
        if start is not None and end is not None:
            mask = (out[DATE] >= pd.Timestamp(start)) & (out[DATE] <= pd.Timestamp(end))
            out = out.loc[mask].copy()
        out[DATE] = out[DATE].dt.date
        return out

    def _rollup(self, by: list[str], start, end) -> pd.DataFrame:
        df = self.merged(start, end)
        present = [m for m in (SESSIONS_METRICS + CART_METRICS + ORDERS_METRICS) if m in df.columns]
        return df.groupby(by, observed=False)[present].sum().reset_index()

    def daily_overall(self, start=None, end=None) -> pd.DataFrame:
        return self._rollup([DATE, USER_TYPE], start, end)

    def daily_by_category(self, start=None, end=None) -> pd.DataFrame:
        return self._rollup([DATE, USER_TYPE, CATEGORY], start, end)

    def daily_by_brand(self, start=None, end=None) -> pd.DataFrame:
        return self._rollup([DATE, USER_TYPE, BRAND], start, end)

    def brand_summary(self) -> pd.DataFrame:
        df = self._compute_merged()
        present = [m for m in (SESSIONS_METRICS + CART_METRICS + ORDERS_METRICS) if m in df.columns]
        return df.groupby(BRAND, observed=False)[present].sum().reset_index()

    def category_summary(self) -> pd.DataFrame:
        df = self._compute_merged()
        present = [m for m in (SESSIONS_METRICS + CART_METRICS + ORDERS_METRICS) if m in df.columns]
        return df.groupby(CATEGORY, observed=False)[present].sum().reset_index()

    def date_range(self) -> tuple[pd.Timestamp, pd.Timestamp]:
        return self._sessions[DATE].min(), self._sessions[DATE].max()

    def meta(self) -> DataMeta:
        lo, hi = self.date_range()
        return DataMeta(
            data_min_date=lo,
            data_max_date=hi,
            migrated_at=pd.Timestamp("now"),
            merged_row_count=len(self._compute_merged()),
        )
