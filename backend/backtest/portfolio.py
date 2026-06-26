"""Portfolio / position tracker.

Turns SignalEvents into sized OrderEvents, applies FillEvents to cash and
positions, and records a per-bar equity time series (marked at each bar's close).

Everything routes through one sizing primitive — rebalance a symbol to a target
fraction of equity — so longs, shorts, scaling, and flips are all the same code
path. Shorts are marked-to-market naturally (negative position => negative
holdings value; short sale proceeds raise cash).
"""
from __future__ import annotations

import pandas as pd

from backtest.data import DataHandler
from backtest.events import FillEvent, OrderEvent, SignalEvent


class Portfolio:
    def __init__(
        self,
        data: DataHandler,
        symbols,
        initial_capital: float = 100_000.0,
        target_pct: float = 0.95,
    ):
        self.data = data
        self.symbols = list(symbols)
        self.initial_capital = float(initial_capital)
        self.target_pct = target_pct          # default weight for a discrete LONG

        self.cash = float(initial_capital)
        self.positions: dict[str, int] = {s: 0 for s in self.symbols}
        self.history: list[dict] = []         # per-bar equity snapshots
        self.trades: list[FillEvent] = []

    # ---- valuation -------------------------------------------------------
    def holdings_value(self) -> float:
        total = 0.0
        for sym, qty in self.positions.items():
            if qty == 0:
                continue
            px = self.data.get_latest_bar_value(sym, "close")
            if px is not None:
                total += qty * px              # qty<0 (short) => negative value
        return total

    def total_equity(self) -> float:
        return self.cash + self.holdings_value()

    # ---- sizing ----------------------------------------------------------
    def _rebalance_order(self, symbol: str, weight: float, time) -> list[OrderEvent]:
        """Emit the order that moves `symbol` to `weight` * equity (signed)."""
        if symbol not in self.positions:
            self.positions[symbol] = 0
        price = self.data.get_latest_bar_value(symbol, "close")
        if price is None or price <= 0:
            return []
        desired = int(round(weight * self.total_equity() / price))
        delta = desired - self.positions[symbol]
        if delta == 0:
            return []
        direction = "BUY" if delta > 0 else "SELL"
        return [OrderEvent(symbol, "MKT", abs(delta), direction, time)]

    # ---- event handlers --------------------------------------------------
    def update_signal(self, signal: SignalEvent) -> list[OrderEvent]:
        if signal.target_pct is not None:
            weight = signal.target_pct
        elif signal.signal == "LONG":
            weight = self.target_pct
        elif signal.signal == "SHORT":
            weight = -self.target_pct
        elif signal.signal == "EXIT":
            weight = 0.0
        else:
            return []
        return self._rebalance_order(signal.symbol, weight, signal.time)

    def update_fill(self, fill: FillEvent) -> None:
        notional = fill.quantity * fill.fill_price
        if fill.direction == "BUY":
            self.cash -= notional + fill.commission
        else:
            self.cash += notional - fill.commission        # short proceeds raise cash
        self.positions[fill.symbol] = self.positions.get(fill.symbol, 0) + fill.signed_quantity
        self.trades.append(fill)

    def update_timeindex(self, time) -> None:
        self.history.append(
            {
                "time": time,
                "cash": self.cash,
                "holdings": self.holdings_value(),
                "total": self.total_equity(),
            }
        )

    # ---- output ----------------------------------------------------------
    def equity_curve(self) -> pd.DataFrame:
        if not self.history:
            return pd.DataFrame(columns=["cash", "holdings", "total", "returns", "equity"])
        df = pd.DataFrame(self.history).set_index("time")
        df["returns"] = df["total"].pct_change().fillna(0.0)
        df["equity"] = df["total"] / self.initial_capital
        return df
