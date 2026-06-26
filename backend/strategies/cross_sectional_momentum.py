"""Cross-sectional momentum (Phase 3.3).

Once a month, rank the universe by trailing return (optionally skipping the most
recent bars — the classic 12-1 effect), go long the top quantile and short the
bottom quantile, equal-weight and dollar-neutral. Emits target-weight signals,
so the portfolio rebalances every name to its new weight.
"""
from __future__ import annotations

from backtest.events import MarketEvent, SignalEvent
from strategies.base import Strategy


class CrossSectionalMomentum(Strategy):
    def __init__(
        self,
        data,
        symbols,
        lookback: int = 126,
        quantile: float = 0.3,
        gross: float = 1.0,
        skip: int = 0,
    ):
        super().__init__(data, symbols)
        self.lookback = lookback
        self.quantile = quantile
        self.gross = gross
        self.skip = skip
        self._last_month = None

    def calculate_signals(self, event: MarketEvent):
        now = event.time
        month = (now.year, now.month)
        if month == self._last_month:
            return []

        need = self.lookback + self.skip + 1
        rets: dict[str, float] = {}
        for sym in self.symbols:
            bars = self.data.get_latest_bars(sym, need)
            if len(bars) < need:
                continue
            closes = bars["close"]
            recent = closes.iloc[-1 - self.skip]
            base = closes.iloc[0]
            if base > 0:
                rets[sym] = recent / base - 1.0
        if len(rets) < 4:
            return []

        self._last_month = month
        ranked = sorted(rets, key=rets.get)
        k = max(1, min(int(len(ranked) * self.quantile), len(ranked) // 2))
        longs = set(ranked[-k:])
        shorts = set(ranked[:k])
        weight = self.gross / (2 * k)

        signals = []
        for sym in rets:                      # rebalance every name with data
            if sym in longs:
                target = weight
            elif sym in shorts:
                target = -weight
            else:
                target = 0.0
            signals.append(SignalEvent(sym, now, "TARGET", target_pct=target))
        return signals
