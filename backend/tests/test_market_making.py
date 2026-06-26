"""Market-maker keeps inventory bounded and quotes two-sided."""
import numpy as np
import pandas as pd

from strategies.market_making import MarketMaker


def _mid_path(n=1500, seed=0):
    rng = np.random.default_rng(seed)
    mid = 100.0 * np.exp(np.cumsum(rng.normal(0, 5e-4, n)))
    return pd.Series(mid, index=pd.date_range("2024-01-01", periods=n, freq="min", tz="UTC"))


def test_inventory_stays_within_cap():
    res = MarketMaker(half_spread_bps=5, inventory_limit=40, skew_bps_per_unit=0.3, seed=1).simulate(_mid_path())
    assert res["inventory"].abs().max() <= 40
    assert len(res) == 1500
    assert "pnl" in res.columns


def test_quotes_two_sided_at_neutral_inventory():
    res = MarketMaker(seed=1).simulate(_mid_path())
    first = res.iloc[0]                       # inventory starts at 0 -> symmetric
    assert first["bid"] < first["mid"] < first["ask"]
