"""Engle-Granger cointegration utilities for pairs selection.

`find_cointegrated_pairs` screens a universe; `spread_zscore` is the live signal
the pairs strategy trades. Hedge ratio is a simple OLS slope (degree-1 polyfit).
"""
from __future__ import annotations

import itertools

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import coint


def hedge_ratio(y, x) -> float:
    """OLS slope of y on x — how many units of x hedge one unit of y."""
    y = np.asarray(y, dtype=float)
    x = np.asarray(x, dtype=float)
    slope, _intercept = np.polyfit(x, y, 1)
    return float(slope)


def spread_zscore(y, x, beta: float | None = None) -> tuple[float, float]:
    """Return (z-score of the latest spread, beta). spread = y - beta*x."""
    y = np.asarray(y, dtype=float)
    x = np.asarray(x, dtype=float)
    b = hedge_ratio(y, x) if beta is None else beta
    spread = y - b * x
    sd = spread.std()
    z = float((spread[-1] - spread.mean()) / sd) if sd > 0 else 0.0
    return z, float(b)


def find_cointegrated_pairs(prices: pd.DataFrame, pvalue_threshold: float = 0.05):
    """prices: wide frame (columns = symbols, aligned closes). Returns
    [(sym_a, sym_b, pvalue), ...] below the threshold, most-cointegrated first."""
    cols = list(prices.columns)
    found = []
    for a, b in itertools.combinations(cols, 2):
        s = prices[[a, b]].dropna()
        if len(s) < 50:
            continue
        _tstat, pvalue, _crit = coint(s[a], s[b])
        if pvalue < pvalue_threshold:
            found.append((a, b, float(pvalue)))
    return sorted(found, key=lambda r: r[2])
