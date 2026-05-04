from __future__ import annotations

from pathlib import Path

import duckdb
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

# Pre-aggregated parquet files written by scripts/migrate_pickle_to_parquet.py.
_VIEWS = (
    "sessions",
    "cart",
    "orders",
    "merged",
    "daily_overall",
    "daily_by_category",
    "daily_by_brand",
    "brand_summary",
    "category_summary",
    "meta",
)


class DuckDBRepository:
    def __init__(self, parquet_dir: Path) -> None:
        self._dir = Path(parquet_dir)
        self._con: duckdb.DuckDBPyConnection | None = None

    def _connect(self) -> duckdb.DuckDBPyConnection:
        if self._con is None:
            self._con = duckdb.connect(":memory:")
            for name in _VIEWS:
                path = self._dir / f"{name}.parquet"
                if path.exists():
                    self._con.execute(
                        f"CREATE OR REPLACE VIEW {name} AS "
                        f"SELECT * FROM read_parquet('{path.as_posix()}')"
                    )
        return self._con

    # ----- raw views ------------------------------------------------------

    def _read_view(self, view: str) -> pd.DataFrame:
        df = self._connect().execute(f"SELECT * FROM {view}").df()
        if DATE in df.columns:
            df[DATE] = pd.to_datetime(df[DATE])
        return df

    def sessions(self) -> pd.DataFrame: return self._read_view("sessions")
    def cart(self) -> pd.DataFrame:     return self._read_view("cart")
    def orders(self) -> pd.DataFrame:   return self._read_view("orders")

    # ----- date-filtered helpers -----------------------------------------

    def _date_filtered(
        self,
        view: str,
        start: pd.Timestamp | str | None,
        end: pd.Timestamp | str | None,
    ) -> pd.DataFrame:
        con = self._connect()
        if start is not None and end is not None:
            sql = f"SELECT * FROM {view} WHERE {DATE} BETWEEN ? AND ?"
            params: list = [pd.Timestamp(start), pd.Timestamp(end)]
        else:
            sql = f"SELECT * FROM {view}"
            params = []
        out = con.execute(sql, params).df()
        if DATE in out.columns:
            out[DATE] = pd.to_datetime(out[DATE]).dt.date
        return out

    def merged(
        self,
        start: pd.Timestamp | str | None = None,
        end: pd.Timestamp | str | None = None,
    ) -> pd.DataFrame:
        merged_path = self._dir / "merged.parquet"
        if merged_path.exists():
            return self._date_filtered("merged", start, end)
        return self._compute_merged(start, end)

    def daily_overall(
        self, start: pd.Timestamp | str | None = None, end: pd.Timestamp | str | None = None
    ) -> pd.DataFrame:
        return self._date_filtered("daily_overall", start, end)

    def daily_by_category(
        self, start: pd.Timestamp | str | None = None, end: pd.Timestamp | str | None = None
    ) -> pd.DataFrame:
        return self._date_filtered("daily_by_category", start, end)

    def daily_by_brand(
        self, start: pd.Timestamp | str | None = None, end: pd.Timestamp | str | None = None
    ) -> pd.DataFrame:
        return self._date_filtered("daily_by_brand", start, end)

    def brand_summary(self) -> pd.DataFrame:
        return self._connect().execute("SELECT * FROM brand_summary").df()

    def category_summary(self) -> pd.DataFrame:
        return self._connect().execute("SELECT * FROM category_summary").df()

    # ----- metadata -------------------------------------------------------

    def date_range(self) -> tuple[pd.Timestamp, pd.Timestamp]:
        m = self.meta()
        return pd.Timestamp(m.data_min_date), pd.Timestamp(m.data_max_date)

    def meta(self) -> DataMeta:
        meta_path = self._dir / "meta.parquet"
        if meta_path.exists():
            row = self._connect().execute("SELECT * FROM meta").df().iloc[0]
            return DataMeta(
                data_min_date=pd.Timestamp(row["data_min_date"]),
                data_max_date=pd.Timestamp(row["data_max_date"]),
                migrated_at=pd.Timestamp(row["migrated_at"]),
                merged_row_count=int(row["merged_row_count"]),
            )
        # fallback: compute live from sessions
        con = self._connect()
        row = con.execute("SELECT MIN(date) AS lo, MAX(date) AS hi, COUNT(*) AS n FROM sessions").df().iloc[0]
        return DataMeta(
            data_min_date=pd.Timestamp(row["lo"]),
            data_max_date=pd.Timestamp(row["hi"]),
            migrated_at=pd.Timestamp("now"),
            merged_row_count=int(row["n"]),
        )

    # ----- fallback when migration's merged.parquet is missing -----------

    def _compute_merged(self, start, end) -> pd.DataFrame:
        keys = ", ".join(GROUP_KEYS)
        s_sums = ", ".join(f"SUM({m}) AS {m}" for m in SESSIONS_METRICS)
        c_sums = ", ".join(f"SUM({m}) AS {m}" for m in CART_METRICS)
        o_sums = ", ".join(f"SUM({m}) AS {m}" for m in ORDERS_METRICS)
        params: list = []
        where = ""
        if start is not None and end is not None:
            where = f"WHERE {DATE} BETWEEN ? AND ?"
            params = [pd.Timestamp(start), pd.Timestamp(end)]
        sql = f"""
            WITH s AS (SELECT {keys}, {s_sums} FROM sessions GROUP BY {keys}),
                 c AS (SELECT {keys}, {c_sums} FROM cart     GROUP BY {keys}),
                 o AS (SELECT {keys}, {o_sums} FROM orders   GROUP BY {keys})
            SELECT * FROM s
                 FULL OUTER JOIN c USING ({keys})
                 FULL OUTER JOIN o USING ({keys})
            {where}
        """
        out = self._connect().execute(sql, params).df()
        out[DATE] = pd.to_datetime(out[DATE]).dt.date
        return out
