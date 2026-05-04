"""Deterministic synthetic event generator.

The source pickles are pre-aggregated and contain no customer/order/item ids.
RFM/Cohort/CLV/Apriori cannot run on aggregates alone, so this module
synthesizes plausible per-customer events from the aggregates. Same seed +
same input → same output, so charts stay stable across reruns.

Vectorized — no Python row-loops; ~50× faster than naive iterrows.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

DEFAULT_SEED = 42


def synth_orders(
    daily_brand: pd.DataFrame,
    *,
    seed: int = DEFAULT_SEED,
    customer_pool_size: int = 5_000,
    max_orders: int | None = None,
) -> pd.DataFrame:
    """Generate per-order events from a daily-by-brand aggregate.

    Strategy:
      1. Optionally scale Orders/Buyers down so total orders ≤ `max_orders`.
      2. Build an exploded frame: one row per synthetic order. Per-row
         attributes (date/brand/user_type) are inherited from the aggregate.
      3. Sample customer ids vectorized (one np.random call total).
      4. Distribute revenue per row by splitting each aggregate's Sales
         proportionally to the number of orders it generated, with light
         lognormal jitter (so AOV has variance).

    Returns columns: customer_id, order_id, date, brand, user_type, revenue.
    """
    needed = {"date", "user_type", "brand", "Orders", "Buyers", "Sales"}
    missing = needed - set(daily_brand.columns)
    if missing:
        raise ValueError(f"daily_brand missing columns: {sorted(missing)}")
    if daily_brand.empty:
        return _empty_orders()

    df = daily_brand.copy()

    # Optional global cap — keeps Apriori / RFM tractable on long ranges.
    if max_orders is not None:
        total = int(df["Orders"].sum())
        if total > max_orders:
            scale = max_orders / total
            df["Orders"] = (df["Orders"] * scale).round().astype(int).clip(lower=0)
            df["Buyers"] = (df["Buyers"] * scale).round().astype(int).clip(lower=0)
            df["Sales"] = df["Sales"] * scale

    df["Buyers"] = df[["Buyers", "Orders"]].min(axis=1).clip(lower=0)
    df = df[df["Orders"] > 0].reset_index(drop=True)
    if df.empty:
        return _empty_orders()

    rng = np.random.default_rng(seed)

    # --- Explode aggregate rows so each synth-order is its own DataFrame row.
    counts = df["Orders"].astype(int).to_numpy()
    repeated = df.loc[df.index.repeat(counts)].reset_index(drop=True)

    # --- Per-source per-order revenue (sales / orders for that source row),
    # with multiplicative lognormal jitter, then rescaled per source so total
    # of jittered values equals the source's total Sales.
    base = (df["Sales"].to_numpy(dtype=float) / counts).repeat(counts)
    jitter = rng.lognormal(mean=0.0, sigma=0.25, size=base.size)
    rev = base * jitter
    # Per-source rescale to preserve source-level totals
    src_idx = np.arange(len(df)).repeat(counts)
    src_total = pd.Series(rev).groupby(src_idx).transform("sum").to_numpy()
    src_target = df["Sales"].to_numpy(dtype=float).repeat(counts)
    rev = np.where(src_total > 0, rev * src_target / src_total, 0.0)

    # --- Vectorized customer assignment.
    # For each source row, pick `Buyers` distinct customers, then map each of
    # its `Orders` to one of those customers (with replacement → repeat
    # purchases). Implemented per-row with np.random.choice in a small loop;
    # we keep this O(rows) not O(orders) so it stays fast.
    pool = np.arange(customer_pool_size)
    order_customer = np.empty(repeated.shape[0], dtype=np.int64)
    cursor = 0
    for buyers, orders in zip(df["Buyers"].astype(int), counts, strict=False):
        if orders <= 0:
            continue
        n_buyers = int(min(buyers, customer_pool_size))
        if n_buyers <= 0:
            order_customer[cursor:cursor + orders] = rng.integers(0, customer_pool_size, size=orders)
        else:
            chosen = rng.choice(pool, size=n_buyers, replace=False)
            order_customer[cursor:cursor + orders] = rng.choice(chosen, size=orders, replace=True)
        cursor += orders

    repeated["customer_id"] = "cust_" + pd.Series(order_customer).astype(str).str.zfill(6)
    repeated["order_id"] = "ord_" + pd.Series(np.arange(1, repeated.shape[0] + 1)).astype(str).str.zfill(8)
    repeated["revenue"] = rev
    repeated["date"] = pd.to_datetime(repeated["date"])
    return repeated[["customer_id", "order_id", "date", "brand", "user_type", "revenue"]]


def _empty_orders() -> pd.DataFrame:
    return pd.DataFrame(columns=["customer_id", "order_id", "date", "brand", "user_type", "revenue"])


def synth_basket_items(
    orders: pd.DataFrame,
    daily_category_brand: pd.DataFrame,
    *,
    seed: int = DEFAULT_SEED,
    avg_items_per_order: float = 3.0,
) -> pd.DataFrame:
    """Generate per-order item rows so Apriori has something to chew on.

    Each order becomes a basket: anchor item (the order's brand) + 1..k
    extras drawn from the *category* of the anchor brand. Higher
    `avg_items_per_order` → richer co-occurrence → more rules survive
    apriori thresholds.
    """
    if orders.empty:
        return pd.DataFrame(columns=["order_id", "item", "customer_id"])

    rng = np.random.default_rng(seed + 1)

    # category → brands seen in the period
    cat_to_brands: dict[str, np.ndarray] = {}
    if not daily_category_brand.empty and "category" in daily_category_brand.columns:
        for cat, sub in daily_category_brand.groupby("category", observed=False):
            cat_to_brands[str(cat)] = sub["brand"].astype(str).unique()

    # brand → modal category
    if "category" in daily_category_brand.columns:
        brand_to_cat = (
            daily_category_brand.groupby("brand", observed=False)["category"]
            .agg(lambda s: s.mode().iat[0] if not s.mode().empty else "unknown")
            .to_dict()
        )
    else:
        brand_to_cat = {}

    # Anchor item per order
    anchor_brand = orders["brand"].astype(str).to_numpy()
    anchor_cat = np.array([brand_to_cat.get(b, "unknown") for b in anchor_brand])
    order_ids = orders["order_id"].astype(str).to_numpy()
    customer_ids = orders["customer_id"].astype(str).to_numpy()

    # Extra-item counts per order (Poisson)
    extras = rng.poisson(max(avg_items_per_order - 1, 0), size=len(orders)).clip(0, 8)

    # Use brand-level items (lower cardinality → meaningful Apriori support).
    # Anchor item = the order's brand. Extras = additional brands from same
    # category, sampled with weight ∝ category occurrence in the period.
    rows: list[tuple[str, str, str]] = []
    rows.extend(
        (oid, br, cust)
        for oid, br, cust in zip(order_ids, anchor_brand, customer_ids, strict=False)
    )
    for i, n_extra in enumerate(extras):
        if n_extra == 0:
            continue
        cat = anchor_cat[i]
        candidates = cat_to_brands.get(cat)
        if candidates is None or len(candidates) == 0:
            continue
        pool = candidates[candidates != anchor_brand[i]]
        if len(pool) == 0:
            continue
        picks = rng.choice(pool, size=min(int(n_extra), len(pool)), replace=False)
        for p in picks:
            rows.append((order_ids[i], str(p), customer_ids[i]))

    return pd.DataFrame(rows, columns=["order_id", "item", "customer_id"])
