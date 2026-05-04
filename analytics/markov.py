"""Markov-chain helpers.

Two use-cases supported:
1. Behavioral funnel-state transitions (Sessions → Views → Cart → Orders).
   Works on this project's data because the funnel stages are aggregate
   counts already.
2. Customer/touchpoint attribution via first-order Markov chains. Needs raw
   per-customer event sequences — the project's pickles don't have this.
"""
from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd


def transition_matrix(
    sequences: Sequence[Sequence[str]],
    *,
    states: Sequence[str] | None = None,
    laplace: float = 0.0,
) -> pd.DataFrame:
    """First-order transition matrix from a list of state sequences.

    `laplace` adds smoothing to avoid zero-rows.
    """
    if not sequences:
        return pd.DataFrame()

    if states is None:
        seen: dict[str, None] = {}
        for seq in sequences:
            for s in seq:
                seen[s] = None
        states = list(seen.keys())

    idx = {s: i for i, s in enumerate(states)}
    n = len(states)
    counts = np.full((n, n), float(laplace))

    for seq in sequences:
        for a, b in zip(seq[:-1], seq[1:], strict=False):
            if a in idx and b in idx:
                counts[idx[a], idx[b]] += 1

    row_sums = counts.sum(axis=1, keepdims=True)
    safe = np.where(row_sums == 0, 1, row_sums)
    probs = counts / safe
    return pd.DataFrame(probs, index=list(states), columns=list(states))


def funnel_transition_matrix(
    funnel_counts: dict[str, int],
    *,
    stages: Sequence[str] = ("Total_Sessions", "Total_Views", "Total_Cart", "Total_Orders"),
) -> pd.DataFrame:
    """Build a 'next-stage retention' transition matrix from aggregate funnel counts.

    Each row state transitions to either the next stage (with probability
    next/current, capped at 1) or 'drop' (the remainder).
    """
    states = [*stages, "drop"]
    n = len(states)
    matrix = np.zeros((n, n))
    for i, stage in enumerate(stages[:-1]):
        cur = funnel_counts.get(stage, 0)
        nxt = funnel_counts.get(stages[i + 1], 0)
        retained = min(nxt / cur, 1.0) if cur else 0.0
        matrix[i, i + 1] = retained
        matrix[i, -1] = 1.0 - retained
    matrix[-2, -1] = 1.0  # last real stage absorbs into 'drop'
    matrix[-1, -1] = 1.0  # 'drop' is absorbing
    return pd.DataFrame(matrix, index=states, columns=states)


def removal_effect(
    matrix: pd.DataFrame,
    *,
    conversion_state: str,
) -> pd.Series:
    """Per-state 'removal effect': drop in conversion probability if that state is removed.

    Useful as a first-order multi-touch attribution proxy.
    """
    base = _conversion_probability(matrix, conversion_state=conversion_state)
    effects: dict[str, float] = {}
    for state in matrix.index:
        if state == conversion_state:
            continue
        reduced = matrix.drop(index=state, columns=state)
        effects[state] = base - _conversion_probability(reduced, conversion_state=conversion_state)
    return pd.Series(effects).sort_values(ascending=False)


def _conversion_probability(matrix: pd.DataFrame, *, conversion_state: str, steps: int = 50) -> float:
    if matrix.empty or conversion_state not in matrix.index:
        return 0.0
    powered = np.linalg.matrix_power(matrix.to_numpy(), steps)
    return float(powered[0, list(matrix.index).index(conversion_state)])
