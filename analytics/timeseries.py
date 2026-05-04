from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class TrendResult:
    df: pd.DataFrame  # original frame, optionally augmented with 'Cum_perc'
    extreme_points: pd.DataFrame  # subset where |residual| > threshold
    fitted_y: np.ndarray | None  # lowess fit (None on failure)


def trend_with_extremes(
    df: pd.DataFrame,
    *,
    x_col: str,
    y_col: str,
    z_threshold: float = 2.0,
) -> TrendResult:
    """Fit a lowess trend and return points whose residuals exceed `z_threshold` * std.

    `x_col` is only used for ordering — lowess takes a numeric x, so we pass
    the row index (already ordered by caller).
    """
    if df.empty or len(df) < 3:
        return TrendResult(df=df.copy(), extreme_points=df.iloc[0:0].copy(), fitted_y=None)
    try:
        import statsmodels.api as sm
    except ImportError:
        return TrendResult(df=df.copy(), extreme_points=df.iloc[0:0].copy(), fitted_y=None)

    x_numeric = np.arange(len(df), dtype=float)
    y = df[y_col].to_numpy(dtype=float)
    smoothed = sm.nonparametric.lowess(y, x_numeric, return_sorted=False)
    residuals = y - smoothed
    threshold = z_threshold * float(np.std(residuals))
    mask = np.abs(residuals) > threshold
    return TrendResult(df=df.copy(), extreme_points=df.loc[mask].copy(), fitted_y=smoothed)


def decompose(
    series: pd.Series,
    *,
    period: int,
    model: str = "additive",
) -> dict[str, pd.Series]:
    """Wrap statsmodels.tsa.seasonal_decompose into trend/seasonal/resid dict."""
    from statsmodels.tsa.seasonal import seasonal_decompose

    res = seasonal_decompose(series, period=period, model=model)
    return {"trend": res.trend, "seasonal": res.seasonal, "resid": res.resid, "observed": res.observed}
