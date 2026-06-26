import numpy as np
import pandas as pd

from strategies.cointegration import find_cointegrated_pairs, hedge_ratio, spread_zscore


def test_hedge_ratio_recovers_slope():
    rng = np.random.default_rng(0)
    x = np.cumsum(rng.normal(0, 1, 500)) + 100
    y = 2.0 * x + rng.normal(0, 0.5, 500)
    assert abs(hedge_ratio(y, x) - 2.0) < 0.1


def test_spread_zscore_positive_when_rich():
    x = np.full(50, 100.0)
    y = 2.0 * x.copy()
    y[-1] += 5.0                       # latest spread well above its mean
    z, beta = spread_zscore(y, x, beta=2.0)
    assert z > 0 and beta == 2.0


def test_find_cointegrated_pairs_detects_the_pair():
    rng = np.random.default_rng(1)
    x = np.cumsum(rng.normal(0, 1, 400)) + 100
    y = 2.0 * x + rng.normal(0, 0.5, 400)        # cointegrated with x
    z = np.cumsum(rng.normal(0, 1, 400)) + 100   # independent random walk
    idx = pd.date_range("2022-01-01", periods=400, freq="D", tz="UTC")
    prices = pd.DataFrame({"A": y, "B": x, "C": z}, index=idx)

    pairs = find_cointegrated_pairs(prices, pvalue_threshold=0.05)
    names = {(a, b) for a, b, _ in pairs}
    assert ("A", "B") in names
