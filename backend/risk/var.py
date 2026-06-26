"""Value-at-Risk and Conditional VaR (Phase 6.1).

Three methods on a series of (daily) portfolio returns, all returning the loss as
a positive fraction of portfolio value at the given confidence:

  * historical  — empirical quantile of past returns (no distributional assumption)
  * parametric  — Gaussian (variance-covariance) VaR
  * monte_carlo — simulate Normal(mu, sigma) draws and take the quantile

CVaR (expected shortfall) is the average loss *beyond* VaR — what you lose on a
bad day, given it's bad.
"""
from __future__ import annotations

import numpy as np
from scipy.stats import norm


def historical_var(returns, confidence: float = 0.99) -> float:
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    if r.size == 0:
        return 0.0
    return float(-np.quantile(r, 1 - confidence))


def historical_cvar(returns, confidence: float = 0.99) -> float:
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    if r.size == 0:
        return 0.0
    cutoff = np.quantile(r, 1 - confidence)
    tail = r[r <= cutoff]
    return float(-tail.mean()) if tail.size else float(-cutoff)


def parametric_var(returns, confidence: float = 0.99) -> float:
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    mu, sigma = r.mean(), r.std(ddof=1)
    return float(-(mu + norm.ppf(1 - confidence) * sigma))


def parametric_cvar(returns, confidence: float = 0.99) -> float:
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    mu, sigma = r.mean(), r.std(ddof=1)
    z = norm.ppf(1 - confidence)
    return float(-mu + sigma * norm.pdf(z) / (1 - confidence))


def monte_carlo_var(returns, confidence: float = 0.99, n: int = 100_000, seed=None):
    """Gaussian Monte-Carlo VaR/CVaR fit to the sample mean/vol."""
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    mu, sigma = r.mean(), r.std(ddof=1)
    sims = np.random.default_rng(seed).normal(mu, sigma, n)
    cutoff = np.quantile(sims, 1 - confidence)
    var = float(-cutoff)
    cvar = float(-sims[sims <= cutoff].mean())
    return var, cvar


def portfolio_returns(weights, asset_returns) -> np.ndarray:
    """Weighted daily portfolio returns from an asset-returns frame (cols = assets)."""
    w = np.asarray(weights, dtype=float)
    return np.asarray(asset_returns, dtype=float) @ w


def var_report(returns, confidence: float = 0.99, value: float = 1.0, seed: int = 0) -> dict:
    """All methods at once, scaled to `value` (currency VaR if value=portfolio size)."""
    mc_var, mc_cvar = monte_carlo_var(returns, confidence, seed=seed)
    return {
        "confidence": confidence,
        "historical_var": historical_var(returns, confidence) * value,
        "parametric_var": parametric_var(returns, confidence) * value,
        "monte_carlo_var": mc_var * value,
        "historical_cvar": historical_cvar(returns, confidence) * value,
        "parametric_cvar": parametric_cvar(returns, confidence) * value,
        "monte_carlo_cvar": mc_cvar * value,
    }
