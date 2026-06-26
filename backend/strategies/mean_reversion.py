"""Pairs trading on a cointegrated spread (Phase 3.2).

Estimates a rolling hedge ratio beta, forms spread = A - beta*B, and trades its
z-score: at +entry the spread is rich -> short A / long B; at -entry it's cheap
-> long A / short B; exit toward 0. Equal-dollar legs (±weight each); beta drives
the signal, not the position sizing.
"""
from __future__ import annotations

import numpy as np

from backtest.events import MarketEvent, SignalEvent
from strategies.base import Strategy


class PairsTradingStrategy(Strategy):
    def __init__(
        self,
        data,
        sym_a: str,
        sym_b: str,
        lookback: int = 60,
        entry_z: float = 2.0,
        exit_z: float = 0.5,
        weight: float = 0.5,
        beta: float | None = None,
    ):
        super().__init__(data, [sym_a, sym_b])
        self.a, self.b = sym_a, sym_b
        self.lookback = lookback
        self.entry_z = entry_z
        self.exit_z = exit_z
        self.weight = weight
        self.fixed_beta = beta
        self.state = 0          # +1 long spread, -1 short spread, 0 flat

    def _target(self, sym, w, time):
        return SignalEvent(sym, time, "TARGET", target_pct=w)

    def calculate_signals(self, event: MarketEvent):
        ba = self.data.get_latest_bars(self.a, self.lookback)
        bb = self.data.get_latest_bars(self.b, self.lookback)
        if len(ba) < self.lookback or len(bb) < self.lookback:
            return []
        a = ba["close"].to_numpy(dtype=float)
        b = bb["close"].to_numpy(dtype=float)
        beta = self.fixed_beta if self.fixed_beta is not None else float(np.polyfit(b, a, 1)[0])
        spread = a - beta * b
        sd = spread.std()
        if sd == 0:
            return []
        z = (spread[-1] - spread.mean()) / sd

        if self.state == 0:
            if z >= self.entry_z:                      # spread rich
                self.state = -1
                return [self._target(self.a, -self.weight, event.time),
                        self._target(self.b, +self.weight, event.time)]
            if z <= -self.entry_z:                     # spread cheap
                self.state = +1
                return [self._target(self.a, +self.weight, event.time),
                        self._target(self.b, -self.weight, event.time)]
        elif abs(z) <= self.exit_z:                    # converged -> flatten
            self.state = 0
            return [self._target(self.a, 0.0, event.time),
                    self._target(self.b, 0.0, event.time)]
        return []
