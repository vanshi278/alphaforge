"""Pairs and cross-sectional momentum run end-to-end and position as expected."""
import numpy as np
import pandas as pd

from backtest.data import DataHandler
from backtest.engine import Backtest
from backtest.execution import SimulatedExecutionHandler
from backtest.portfolio import Portfolio
from strategies import CrossSectionalMomentum, PairsTradingStrategy


def _bars(closes, symbol, start="2020-01-01"):
    idx = pd.date_range(start, periods=len(closes), freq="D", tz="UTC")
    closes = np.asarray(closes, dtype=float)
    return pd.DataFrame(
        {"open": closes, "high": closes, "low": closes, "close": closes,
         "volume": 1000.0, "symbol": symbol},
        index=idx,
    )


def test_pairs_strategy_trades_both_legs():
    rng = np.random.default_rng(0)
    n = 400
    common = np.cumsum(rng.normal(0, 1, n)) + 100
    spread = np.sin(np.linspace(0, 20 * np.pi, n)) * 3      # mean-reverting
    bars = {"A": _bars(common + spread, "A"), "B": _bars(common, "B")}
    data = DataHandler(bars, ["A", "B"])
    pf = Portfolio(data, ["A", "B"], initial_capital=100_000.0)
    strat = PairsTradingStrategy(data, "A", "B", lookback=30, entry_z=1.5, exit_z=0.3)
    pf = Backtest(data, strat, pf, SimulatedExecutionHandler(data)).run()

    assert len(pf.trades) > 0
    assert {t.symbol for t in pf.trades} == {"A", "B"}      # both legs traded


def test_cross_sectional_longs_winners_shorts_losers():
    n = 300

    def drifting(daily):
        return 100.0 * np.exp(np.cumsum(np.full(n, daily)))

    bars = {
        "WIN": _bars(drifting(0.003), "WIN"),
        "LOSE": _bars(drifting(-0.003), "LOSE"),
        "MID1": _bars(drifting(0.0005), "MID1"),
        "MID2": _bars(drifting(0.0), "MID2"),
    }
    data = DataHandler(bars, list(bars))
    pf = Portfolio(data, list(bars), initial_capital=100_000.0)
    strat = CrossSectionalMomentum(data, list(bars), lookback=60, quantile=0.25)
    pf = Backtest(data, strat, pf, SimulatedExecutionHandler(data)).run()

    assert pf.positions["WIN"] > 0      # long the strongest
    assert pf.positions["LOSE"] < 0     # short the weakest
