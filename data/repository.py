from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import pandas as pd

# Canonical column names — single source of truth.
DATE = "date"
USER_TYPE = "user_type"
CATEGORY = "category"
BRAND = "brand"

GROUP_KEYS = [DATE, USER_TYPE, CATEGORY, BRAND]

# Metric vocabulary — mirrors what the migration script writes.
SESSIONS_METRICS = ["Sessions", "Views"]
CART_METRICS = ["Cart"]
ORDERS_METRICS = ["Orders", "Buyers", "Products_Sold", "Sales"]
ALL_METRICS = SESSIONS_METRICS + CART_METRICS + ORDERS_METRICS


@dataclass(frozen=True)
class DataMeta:
    data_min_date: pd.Timestamp
    data_max_date: pd.Timestamp
    migrated_at: pd.Timestamp
    merged_row_count: int


class DataRepository(Protocol):
    # Raw rollups (rarely needed in the UI)
    def sessions(self) -> pd.DataFrame: ...
    def cart(self) -> pd.DataFrame: ...
    def orders(self) -> pd.DataFrame: ...

    # Joined merged table — date filter pushed into SQL
    def merged(
        self,
        start: pd.Timestamp | str | None = None,
        end: pd.Timestamp | str | None = None,
    ) -> pd.DataFrame: ...

    # Pre-aggregated rollups (cheap reads — built at migration time)
    def daily_overall(
        self, start: pd.Timestamp | str | None = None, end: pd.Timestamp | str | None = None
    ) -> pd.DataFrame: ...
    def daily_by_category(
        self, start: pd.Timestamp | str | None = None, end: pd.Timestamp | str | None = None
    ) -> pd.DataFrame: ...
    def daily_by_brand(
        self, start: pd.Timestamp | str | None = None, end: pd.Timestamp | str | None = None
    ) -> pd.DataFrame: ...
    def brand_summary(self) -> pd.DataFrame: ...
    def category_summary(self) -> pd.DataFrame: ...

    def date_range(self) -> tuple[pd.Timestamp, pd.Timestamp]: ...
    def meta(self) -> DataMeta: ...
