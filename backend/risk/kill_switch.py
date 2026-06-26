"""Drawdown circuit breaker / kill switch (Phase 6.4).

Tracks the running equity peak; once drawdown breaches the threshold it latches
"triggered", and the book is flattened (every position sent to zero).
"""
from __future__ import annotations

from typing import Optional


class DrawdownKillSwitch:
    def __init__(self, threshold: float = 0.20):
        self.threshold = threshold          # e.g. 0.20 => flatten at -20% drawdown
        self.peak: Optional[float] = None
        self.triggered = False

    def drawdown(self, equity: float) -> float:
        if self.peak is None or self.peak <= 0:
            return 0.0
        return equity / self.peak - 1.0

    def update(self, equity: float) -> bool:
        """Feed the latest equity; returns True once (and forever after) tripped."""
        if self.peak is None or equity > self.peak:
            self.peak = equity
        if not self.triggered and self.drawdown(equity) <= -self.threshold:
            self.triggered = True
        return self.triggered


def flatten_orders(positions: dict) -> dict:
    """Orders that take every position to flat: {symbol: signed_qty_to_trade}."""
    return {sym: -qty for sym, qty in positions.items() if qty != 0}
