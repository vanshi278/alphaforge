"""Inventory-aware market-making simulation (Phase 3.4).

Market making is a quote/inventory game, not a bar signal, so this is a
standalone tick-level sim on a mid-price path rather than a Strategy run through
the engine. The realistic limit-order-book version arrives in Phase 5. What it
demonstrates here:

  * two-sided quotes around mid (bid below, ask above),
  * inventory skew — when long, both quotes shift down so the ask is likelier to
    get hit and the bid less so, pulling inventory back toward zero,
  * a hard inventory cap, and
  * P&L accrued from capturing the spread.

Fill model: each side fills with a probability that decays with how far its quote
sits from mid (tighter = likelier), suppressed entirely at the inventory cap.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


class MarketMaker:
    def __init__(
        self,
        half_spread_bps: float = 5.0,
        inventory_limit: int = 50,
        skew_bps_per_unit: float = 0.3,
        base_fill: float = 0.5,
        decay_bps: float = 10.0,
        order_size: int = 1,
        seed: int | None = None,
    ):
        self.hs = half_spread_bps
        self.inv_limit = inventory_limit
        self.skew = skew_bps_per_unit
        self.base_fill = base_fill
        self.decay_bps = decay_bps
        self.size = order_size
        self.rng = np.random.default_rng(seed)

    def simulate(self, mid: pd.Series) -> pd.DataFrame:
        inv = 0
        cash = 0.0
        rows = []
        for m in mid.to_numpy(dtype=float):
            skew = self.skew * inv                 # bps; >0 when long -> shift quotes down
            bid_off = self.hs + skew               # bps below mid
            ask_off = self.hs - skew               # bps above mid
            bid = m * (1 - bid_off / 1e4)
            ask = m * (1 + ask_off / 1e4)

            p_buy = self.base_fill * np.exp(-max(bid_off, 0.0) / self.decay_bps)
            p_sell = self.base_fill * np.exp(-max(ask_off, 0.0) / self.decay_bps)
            if inv >= self.inv_limit:
                p_buy = 0.0
            if inv <= -self.inv_limit:
                p_sell = 0.0

            if self.rng.random() < p_buy:
                inv += self.size
                cash -= bid * self.size
            if self.rng.random() < p_sell:
                inv -= self.size
                cash += ask * self.size

            rows.append({"mid": m, "bid": bid, "ask": ask, "inventory": inv,
                         "cash": cash, "pnl": cash + inv * m})
        return pd.DataFrame(rows, index=mid.index)


def _demo() -> None:
    from pathlib import Path

    rng = np.random.default_rng(0)
    n = 3000
    mid = 100.0 * np.exp(np.cumsum(rng.normal(0, 5e-4, n)))
    idx = pd.date_range("2024-01-01", periods=n, freq="min", tz="UTC")
    series = pd.Series(mid, index=idx)

    res = MarketMaker(half_spread_bps=5, inventory_limit=50, skew_bps_per_unit=0.3, seed=1).simulate(series)
    print(f"steps          : {len(res)}")
    print(f"inventory range: [{int(res['inventory'].min())}, {int(res['inventory'].max())}]  (cap ±50)")
    print(f"final inventory: {int(res['inventory'].iloc[-1])}")
    print(f"final P&L      : {res['pnl'].iloc[-1]:.2f}")

    out = Path(__file__).resolve().parents[2] / "results"
    out.mkdir(exist_ok=True)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
        ax1.plot(res.index, res["inventory"], color="#534AB7")
        ax1.axhline(50, ls="--", c="#999"); ax1.axhline(-50, ls="--", c="#999")
        ax1.set_ylabel("inventory")
        ax2.plot(res.index, res["pnl"], color="#1D9E75")
        ax2.set_ylabel("P&L")
        fig.tight_layout()
        fig.savefig(out / "market_making.png", dpi=110)
        plt.close(fig)
        print(f"plot           : {out / 'market_making.png'}")
    except Exception as exc:  # noqa: BLE001
        print(f"(plot skipped: {exc})")


if __name__ == "__main__":
    _demo()
