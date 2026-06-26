"""Short-selling and target-weight rebalancing accounting."""
import pytest

from backtest.data import DataHandler
from backtest.events import FillEvent, SignalEvent
from backtest.portfolio import Portfolio


def test_open_short_via_target_weight(make_bars):
    data = DataHandler({"TEST": make_bars([100.0, 100.0])}, ["TEST"])
    data.update_bars()                                  # bar 0, close 100
    pf = Portfolio(data, ["TEST"], initial_capital=100_000.0)

    orders = pf.update_signal(SignalEvent("TEST", data.current_time, "TARGET", target_pct=-0.5))
    assert len(orders) == 1 and orders[0].direction == "SELL" and orders[0].quantity == 500

    pf.update_fill(FillEvent("TEST", data.current_time, 500, "SELL", 100.0))
    assert pf.positions["TEST"] == -500
    assert pf.cash == pytest.approx(150_000)            # short proceeds raise cash
    assert pf.total_equity() == pytest.approx(100_000)  # holdings -50,000 offsets


def test_short_profits_when_price_falls(make_bars):
    data = DataHandler({"TEST": make_bars([100.0, 90.0])}, ["TEST"])
    data.update_bars()
    pf = Portfolio(data, ["TEST"], initial_capital=100_000.0)
    pf.update_fill(FillEvent("TEST", data.current_time, 500, "SELL", 100.0))

    data.update_bars()                                  # bar 1, close 90
    assert pf.total_equity() == pytest.approx(100_000 + 500 * (100 - 90))  # +5,000


def test_flip_long_to_short(make_bars):
    data = DataHandler({"TEST": make_bars([100.0, 100.0])}, ["TEST"])
    data.update_bars()
    pf = Portfolio(data, ["TEST"], initial_capital=100_000.0)

    pf.update_fill(FillEvent("TEST", data.current_time, 500, "BUY", 100.0))   # long 500
    # rebalance to -0.5 must sell 1000 (500 to flat + 500 to open short)
    orders = pf.update_signal(SignalEvent("TEST", data.current_time, "TARGET", target_pct=-0.5))
    assert orders[0].direction == "SELL" and orders[0].quantity == 1000
