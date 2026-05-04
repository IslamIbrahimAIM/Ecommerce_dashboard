from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


# ----- Single-number KPIs --------------------------------------------------

def aov(orders: pd.DataFrame, *, sales_col: str = "Sales", orders_col: str = "Orders") -> float:
    """Average Order Value = total sales / total orders. Returns 0 when orders=0."""
    total_orders = orders[orders_col].sum()
    return float(orders[sales_col].sum() / total_orders) if total_orders else 0.0


def median_order_value(
    orders_per_row: pd.DataFrame,
    *,
    sales_col: str = "Sales",
    orders_col: str = "Orders",
) -> float:
    """Median of per-row sales/orders ratios. Pairs with `aov` to expose skew."""
    valid = orders_per_row.loc[orders_per_row[orders_col] > 0]
    if valid.empty:
        return 0.0
    return float((valid[sales_col] / valid[orders_col]).median())


def conversion_rate(
    sessions: pd.DataFrame,
    orders: pd.DataFrame,
    *,
    sessions_col: str = "Sessions",
    orders_col: str = "Orders",
) -> float:
    """Order-per-session ratio. Note: NOT a unique-user CR (requires customer_id)."""
    s = sessions[sessions_col].sum()
    return float(orders[orders_col].sum() / s) if s else 0.0


def abandonment_rate_total(
    df: pd.DataFrame,
    *,
    cart_col: str = "Cart",
    orders_col: str = "Orders",
) -> float:
    """Fleet-wide abandonment rate = (Σ Cart − Σ Orders) / Σ Cart, as percent.

    Aggregating *first* and dividing *last* is the only correct way; computing
    per-row rates and averaging weights small carts equally with huge ones.
    """
    cart = float(df[cart_col].sum())
    orders = float(df[orders_col].sum())
    if cart <= 0:
        return 0.0
    return max(0.0, (cart - orders) / cart) * 100.0


def repeat_rate(orders: pd.DataFrame, *, customer_col: str) -> float:
    if customer_col not in orders.columns:
        return float("nan")
    counts = orders.groupby(customer_col).size()
    return float((counts > 1).sum() / max(len(counts), 1))


# ----- Per-row metrics (vectorized) ---------------------------------------

def abandonment_rate(
    df: pd.DataFrame,
    *,
    cart_col: str = "Cart",
    orders_col: str = "Orders",
) -> pd.DataFrame:
    """Per-row abandonment rate as a percentage (0..100).

    Fixed (vs. previous): no premature rounding before the *100, no silent
    zero when Orders > Cart (which indicates a data-quality issue we surface
    via clip(lower=0) but log at higher layers).
    """
    out = df.copy()
    cart = out[cart_col].astype(float)
    ords = out[orders_col].astype(float)
    rate = np.where(cart > 0, (cart - ords) / cart * 100.0, 0.0)
    out["Abandonment Rate"] = np.clip(rate, 0.0, 100.0)
    return out


def pareto_cumulative(df: pd.DataFrame, *, value_col: str, sort_desc: bool = True) -> pd.DataFrame:
    out = df.sort_values(by=value_col, ascending=not sort_desc).copy()
    total = out[value_col].sum()
    out["Cum_perc"] = (out[value_col].cumsum() / total) * 100 if total else 0.0
    return out


def metric_extremes(
    df: pd.DataFrame,
    *,
    metric: str,
    date_col: str = "date",
) -> dict[str, Any]:
    if df.empty or metric not in df.columns:
        return {"min": None, "max": None, "avg": float("nan"), "median": float("nan")}
    max_row = df.loc[df[metric].idxmax()]
    min_row = df.loc[df[metric].idxmin()]
    return {
        "min": {"value": float(min_row[metric]), "date": min_row[date_col]},
        "max": {"value": float(max_row[metric]), "date": max_row[date_col]},
        "avg": float(df[metric].mean()),
        "median": float(df[metric].median()),
    }


# ----- Period-over-period comparison --------------------------------------

@dataclass(frozen=True)
class PoPDelta:
    """Period-over-period comparison for a single metric."""
    value: float
    prior: float
    abs_delta: float
    pct_delta: float | None  # None when prior == 0
    direction: str  # "up" | "down" | "flat"


def pop_delta(value: float, prior: float, *, flat_threshold_pct: float = 0.5) -> PoPDelta:
    """Compute a structured delta. `flat_threshold_pct` is the +/- band considered 'flat'."""
    abs_delta = float(value) - float(prior)
    pct: float | None
    if prior == 0:
        pct = None
        direction = "up" if value > 0 else "flat"
    else:
        pct = (abs_delta / prior) * 100.0
        if abs(pct) < flat_threshold_pct:
            direction = "flat"
        elif pct > 0:
            direction = "up"
        else:
            direction = "down"
    return PoPDelta(
        value=float(value),
        prior=float(prior),
        abs_delta=abs_delta,
        pct_delta=pct,
        direction=direction,
    )


def prior_window(start: pd.Timestamp | str, end: pd.Timestamp | str) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Return the immediately-preceding window of equal length."""
    s, e = pd.Timestamp(start), pd.Timestamp(end)
    span = e - s
    return s - span - pd.Timedelta(days=1), s - pd.Timedelta(days=1)


# ----- Rolling helpers -----------------------------------------------------

def rolling_mean(series: pd.Series, *, window: int = 7) -> pd.Series:
    return series.rolling(window=window, min_periods=1).mean()
