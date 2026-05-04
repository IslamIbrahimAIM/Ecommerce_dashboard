"""One-shot migration: gzip-pickle → parquet, then build pre-aggregated rollups.

Outputs (in data/parquet/):
    sessions.parquet, cart.parquet, orders.parquet  — raw, only used for ad-hoc
    merged.parquet                                  — outer join of the three
    daily_overall.parquet                           — date × user_type rollup
    daily_by_category.parquet                       — date × user_type × category
    daily_by_brand.parquet                          — date × user_type × brand
    brand_summary.parquet                           — brand-level totals
    category_summary.parquet                        — category-level totals
    meta.parquet                                    — single-row metadata (data_max_date)

Why pre-aggregate: cold-loading 3M rows into pandas takes ~30s. The dashboard
only needs date-level rollups for KPI cards and trend charts; brand-level for
ranking. Pre-computed rollups load in <100ms.

Usage (inside Docker):
    docker run --rm -v "$PWD":/app -w /app ecom-dashboard:dev \\
        python scripts/migrate_pickle_to_parquet.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data"
DST = ROOT / "data" / "parquet"

PICKLE_TO_PARQUET = {
    "sessions_by_user_cat.pkl": "sessions.parquet",
    "cart_by_user_cat.pkl": "cart.parquet",
    "orders_by_user_cat.pkl": "orders.parquet",
}

RENAMES = {"Potentianl_sales": "Potential_Sales"}

# Columns dropped from merged.parquet — unused in the dashboard, just bloat.
MERGED_DROP = ("Potential_Sales", "Potential_Buyers", "Products_in_Cart")


def _read_pickle(path: Path) -> pd.DataFrame:
    try:
        return pd.read_pickle(path, compression="gzip")
    except Exception:
        return pd.read_pickle(path)


def _safe_unlink(p: Path) -> None:
    """Remove if present — no-op if it disappears between exists() and unlink()."""
    try:
        p.unlink()
    except FileNotFoundError:
        pass


def _write_parquet(con, df: pd.DataFrame, dst: Path) -> None:
    _safe_unlink(dst)
    # Also nuke any stale tmp from a previous failed COPY (DuckDB writes
    # tmp_<name>.parquet then renames; macOS bind mounts sometimes leave it).
    _safe_unlink(dst.with_name(f"tmp_{dst.name}"))
    con.register("df", df)
    con.execute(f"COPY df TO '{dst.as_posix()}' (FORMAT 'PARQUET')")
    con.unregister("df")


def _copy(con, sql: str, dst: Path) -> None:
    _safe_unlink(dst)
    _safe_unlink(dst.with_name(f"tmp_{dst.name}"))
    con.execute(f"COPY ({sql}) TO '{dst.as_posix()}' (FORMAT 'PARQUET')")


def _row_count(con, path: Path) -> int:
    return con.execute(f"SELECT count(*) FROM read_parquet('{path.as_posix()}')").fetchone()[0]


def main() -> int:
    DST.mkdir(parents=True, exist_ok=True)
    if not SRC.exists():
        print(f"Source dir missing: {SRC}", file=sys.stderr)
        return 1

    con = duckdb.connect(":memory:")

    # Step 1: pickle → parquet (raw)
    for src_name, dst_name in PICKLE_TO_PARQUET.items():
        src = SRC / src_name
        dst = DST / dst_name
        if not src.exists():
            print(f"  skip (missing): {src}", flush=True)
            continue
        df = _read_pickle(src).rename(columns=RENAMES)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
        _write_parquet(con, df, dst)
        print(f"  wrote {dst.name:<32} rows={len(df):>9} cols={list(df.columns)}", flush=True)

    sess = (DST / "sessions.parquet").as_posix()
    cart = (DST / "cart.parquet").as_posix()
    ords = (DST / "orders.parquet").as_posix()
    keys = "date, user_type, category, brand"

    # Step 2: merged.parquet (drops unused Potential_*/Products_in_Cart columns)
    merged_path = DST / "merged.parquet"
    drop_clause = ", ".join(f"NULL AS _drop_{c}" for c in ())  # placeholder
    select_cols = (
        "date, user_type, category, brand, "
        "Sessions, Views, Cart, "
        "Orders, Buyers, Products_Sold, Sales"
    )
    _copy(con, f"""
        WITH s AS (
            SELECT {keys}, SUM(Sessions) AS Sessions, SUM(Views) AS Views
            FROM read_parquet('{sess}') GROUP BY {keys}
        ),
        c AS (
            SELECT {keys}, SUM(Cart) AS Cart
            FROM read_parquet('{cart}') GROUP BY {keys}
        ),
        o AS (
            SELECT {keys},
                SUM(Orders) AS Orders, SUM(Buyers) AS Buyers,
                SUM(Products_Sold) AS Products_Sold, SUM(Sales) AS Sales
            FROM read_parquet('{ords}') GROUP BY {keys}
        )
        SELECT {select_cols} FROM s
            FULL OUTER JOIN c USING ({keys})
            FULL OUTER JOIN o USING ({keys})
    """, merged_path)
    print(f"  wrote {merged_path.name:<32} rows={_row_count(con, merged_path):>9}", flush=True)

    # Step 3: daily_overall — one row per (date, user_type)
    daily_overall = DST / "daily_overall.parquet"
    _copy(con, f"""
        SELECT date, user_type,
            SUM(Sessions) AS Sessions, SUM(Views) AS Views,
            SUM(Cart) AS Cart,
            SUM(Orders) AS Orders, SUM(Buyers) AS Buyers,
            SUM(Products_Sold) AS Products_Sold, SUM(Sales) AS Sales
        FROM read_parquet('{merged_path.as_posix()}')
        GROUP BY date, user_type
        ORDER BY date, user_type
    """, daily_overall)
    print(f"  wrote {daily_overall.name:<32} rows={_row_count(con, daily_overall):>9}", flush=True)

    # Step 4: daily_by_category
    daily_by_category = DST / "daily_by_category.parquet"
    _copy(con, f"""
        SELECT date, user_type, category,
            SUM(Sessions) AS Sessions, SUM(Views) AS Views,
            SUM(Cart) AS Cart,
            SUM(Orders) AS Orders, SUM(Buyers) AS Buyers,
            SUM(Products_Sold) AS Products_Sold, SUM(Sales) AS Sales
        FROM read_parquet('{merged_path.as_posix()}')
        GROUP BY date, user_type, category
        ORDER BY date, user_type, category
    """, daily_by_category)
    print(f"  wrote {daily_by_category.name:<32} rows={_row_count(con, daily_by_category):>9}", flush=True)

    # Step 5: daily_by_brand
    daily_by_brand = DST / "daily_by_brand.parquet"
    _copy(con, f"""
        SELECT date, user_type, brand,
            SUM(Sessions) AS Sessions, SUM(Views) AS Views,
            SUM(Cart) AS Cart,
            SUM(Orders) AS Orders, SUM(Buyers) AS Buyers,
            SUM(Products_Sold) AS Products_Sold, SUM(Sales) AS Sales
        FROM read_parquet('{merged_path.as_posix()}')
        GROUP BY date, user_type, brand
        ORDER BY date, user_type, brand
    """, daily_by_brand)
    print(f"  wrote {daily_by_brand.name:<32} rows={_row_count(con, daily_by_brand):>9}", flush=True)

    # Step 6: brand_summary (period totals)
    brand_summary = DST / "brand_summary.parquet"
    _copy(con, f"""
        SELECT brand,
            SUM(Sessions) AS Sessions, SUM(Views) AS Views,
            SUM(Cart) AS Cart,
            SUM(Orders) AS Orders, SUM(Buyers) AS Buyers,
            SUM(Products_Sold) AS Products_Sold, SUM(Sales) AS Sales
        FROM read_parquet('{merged_path.as_posix()}')
        GROUP BY brand
    """, brand_summary)
    print(f"  wrote {brand_summary.name:<32} rows={_row_count(con, brand_summary):>9}", flush=True)

    # Step 7: category_summary (period totals)
    category_summary = DST / "category_summary.parquet"
    _copy(con, f"""
        SELECT category,
            SUM(Sessions) AS Sessions, SUM(Views) AS Views,
            SUM(Cart) AS Cart,
            SUM(Orders) AS Orders, SUM(Buyers) AS Buyers,
            SUM(Products_Sold) AS Products_Sold, SUM(Sales) AS Sales
        FROM read_parquet('{merged_path.as_posix()}')
        GROUP BY category
    """, category_summary)
    print(f"  wrote {category_summary.name:<32} rows={_row_count(con, category_summary):>9}", flush=True)

    # Step 8: metadata (single-row file with the latest data date)
    meta_path = DST / "meta.parquet"
    _copy(con, f"""
        SELECT
            CAST(MAX(date) AS DATE) AS data_max_date,
            CAST(MIN(date) AS DATE) AS data_min_date,
            CAST(NOW() AS TIMESTAMP) AS migrated_at,
            COUNT(*) AS merged_row_count
        FROM read_parquet('{merged_path.as_posix()}')
    """, meta_path)
    print(f"  wrote {meta_path.name:<32} rows=1", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
