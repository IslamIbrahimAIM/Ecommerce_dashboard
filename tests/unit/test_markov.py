from __future__ import annotations

from analytics.markov import (
    funnel_transition_matrix,
    removal_effect,
    transition_matrix,
)


def test_transition_matrix_rows_sum_to_one():
    sequences = [["A", "B", "C"], ["A", "B"], ["A", "C", "B"]]
    m = transition_matrix(sequences)
    sums = m.sum(axis=1)
    # Rows that have outgoing transitions must sum to 1.
    for state, total in sums.items():
        if state == "C":
            continue  # terminal state — no outgoing transitions in this fixture
        assert abs(total - 1.0) < 1e-9


def test_transition_matrix_empty():
    m = transition_matrix([])
    assert m.empty


def test_funnel_transition_matrix_drop_absorbing():
    counts = {"Total_Sessions": 100, "Total_Views": 80, "Total_Cart": 30, "Total_Orders": 10}
    m = funnel_transition_matrix(counts)
    assert m.loc["drop", "drop"] == 1.0
    # Sessions → Views retention is 0.8
    assert abs(m.loc["Total_Sessions", "Total_Views"] - 0.8) < 1e-9
    assert abs(m.loc["Total_Sessions", "drop"] - 0.2) < 1e-9


def test_removal_effect_returns_series():
    counts = {"Total_Sessions": 100, "Total_Views": 80, "Total_Cart": 30, "Total_Orders": 10}
    m = funnel_transition_matrix(counts)
    eff = removal_effect(m, conversion_state="Total_Orders")
    assert "Total_Sessions" in eff.index
