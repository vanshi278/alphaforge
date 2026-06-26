"""Kupiec proportion-of-failures (POF) test (Phase 6.2).

Backtests a VaR model: over many days, a 99% 1-day VaR should be breached on
about 1% of days. The POF likelihood-ratio statistic is chi-square(1); a large
value (p < 0.05) means the model mis-states risk (too many or too few breaches).
"""
from __future__ import annotations

import numpy as np
from scipy.stats import chi2

from risk.var import historical_var


def var_exceptions(returns, window: int = 250, confidence: float = 0.99) -> tuple[int, int]:
    """Rolling 1-day VaR backtest. Returns (n_observations, n_exceptions)."""
    r = np.asarray(returns, dtype=float)
    n = exceptions = 0
    for t in range(window, len(r)):
        var = historical_var(r[t - window:t], confidence)
        if r[t] < -var:
            exceptions += 1
        n += 1
    return n, exceptions


def kupiec_pof(n_obs: int, n_exceptions: int, confidence: float = 0.99) -> dict:
    p = 1 - confidence
    n, x = n_obs, n_exceptions
    if n == 0:
        return {}
    if x == 0:
        lr = -2 * n * np.log(1 - p)
    else:
        pi = x / n
        lr = -2 * ((n - x) * np.log(1 - p) + x * np.log(p)) \
             + 2 * ((n - x) * np.log(1 - pi) + x * np.log(pi))
    return {
        "n_obs": n,
        "exceptions": x,
        "expected": p * n,
        "observed_rate": x / n,
        "lr_pof": float(lr),
        "p_value": float(1 - chi2.cdf(lr, 1)),
        "reject_model": bool(lr > chi2.ppf(0.95, 1)),   # reject at 95%
    }
