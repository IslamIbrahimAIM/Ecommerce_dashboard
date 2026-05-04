from __future__ import annotations

from pathlib import Path

import duckdb

from data.duckdb_repo import DuckDBRepository
from data.memory_repo import InMemoryRepository
from data.repository import GROUP_KEYS


def _write_parquet(con, df, path: Path) -> None:
    con.register("df", df)
    con.execute(f"COPY df TO '{path.as_posix()}' (FORMAT 'PARQUET')")
    con.unregister("df")


def test_duckdb_repository_round_trip(tmp_path, synth_sessions, synth_cart, synth_orders):
    con = duckdb.connect(":memory:")
    _write_parquet(con, synth_sessions, tmp_path / "sessions.parquet")
    _write_parquet(con, synth_cart, tmp_path / "cart.parquet")
    _write_parquet(con, synth_orders, tmp_path / "orders.parquet")

    repo = DuckDBRepository(tmp_path)
    assert len(repo.sessions()) == 4
    merged = repo.merged()
    for k in GROUP_KEYS:
        assert k in merged.columns


def test_in_memory_repository_merge_preserves_keys(synth_sessions, synth_cart, synth_orders):
    repo = InMemoryRepository(synth_sessions, synth_cart, synth_orders)
    merged = repo.merged()
    for k in GROUP_KEYS:
        assert k in merged.columns
    assert merged["Sales"].sum() == synth_orders["Sales"].sum()
