from __future__ import annotations

import pandas as pd

from analytics.cohort import cohort_retention, cohort_retention_rates


def test_cohort_retention_basic(synth_customer_orders):
    grid = cohort_retention(synth_customer_orders, customer_col="customer_id", date_col="date", period="M")
    assert not grid.empty
    # First column is offset 0 — every customer is "retained" in their own cohort month.
    assert (grid.iloc[:, 0] >= 1).all()


def test_cohort_retention_rates_normalize_to_one():
    grid = pd.DataFrame({0: [4, 2], 1: [2, 1], 2: [1, 0]})
    rates = cohort_retention_rates(grid)
    assert (rates[0] == 1.0).all()
    assert rates.iloc[0, 1] == 0.5
