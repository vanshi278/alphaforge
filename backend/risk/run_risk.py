"""Phase 6 risk-engine demo.

  6.1 VaR / CVaR three ways on an equal-weight Nifty portfolio
  6.2 Kupiec backtest of the 99% VaR model
  6.3 pre-trade limit checks (resize / block)
  6.4 drawdown kill switch (simulated crash -> flatten)

    cd backend && python -m risk.run_risk
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from data.history import load_history
from risk.kill_switch import DrawdownKillSwitch, flatten_orders
from risk.kupiec import kupiec_pof, var_exceptions
from risk.limits import RiskLimits, RiskManager
from risk.var import var_report

RESULTS = Path(__file__).resolve().parents[2] / "results"
UNIVERSE = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]


def _portfolio_returns(start="2018-01-01", end="2024-01-01") -> pd.Series:
    closes = {}
    for s in UNIVERSE:
        df = load_history(s, start, end, "1d")
        if not df.empty:
            closes[s] = df["close"]
    px = pd.DataFrame(closes).dropna()
    rets = px.pct_change().dropna()
    w = np.full(rets.shape[1], 1.0 / rets.shape[1])
    return rets @ w


def main() -> dict:
    port = _portfolio_returns()
    value = 1_000_000.0
    print(f"equal-weight {len(UNIVERSE)}-name portfolio | {len(port)} days | ${value:,.0f}\n")

    rep = var_report(port.values, confidence=0.99, value=value, seed=0)
    print("=== 99% 1-day VaR / CVaR ===")
    print(f"{'method':<14}{'VaR ($)':>14}{'CVaR ($)':>14}")
    for m in ("historical", "parametric", "monte_carlo"):
        print(f"{m:<14}{rep[m + '_var']:>14,.0f}{rep[m + '_cvar']:>14,.0f}")

    n, exc = var_exceptions(port.values, window=250, confidence=0.99)
    kp = kupiec_pof(n, exc, 0.99)
    print("\n=== Kupiec POF backtest (99% VaR, 250d rolling) ===")
    print(f"obs {kp['n_obs']} | exceptions {kp['exceptions']} (expected {kp['expected']:.1f}) | "
          f"LR {kp['lr_pof']:.2f} | p {kp['p_value']:.2f} | "
          f"{'REJECT model' if kp['reject_model'] else 'model OK'}")

    print("\n=== pre-trade limits (max 20% per name, 2x gross) ===")
    rm = RiskManager(RiskLimits(max_position_pct=0.20, max_gross_pct=2.0))
    positions, prices = {"RELIANCE": 0}, {"RELIANCE": 2900.0}
    appr, reason = rm.check_order("RELIANCE", 1000, 2900.0, positions, prices, value)
    print(f"BUY 1000 RELIANCE @2900 (~290% of equity) -> approved {appr} ({reason})")
    appr2, reason2 = rm.check_order("RELIANCE", 50, 2900.0, positions, prices, value)
    print(f"BUY 50 RELIANCE @2900 (~14.5%)           -> approved {appr2} ({reason2})")

    print("\n=== drawdown kill switch (threshold -20%) ===")
    ks = DrawdownKillSwitch(threshold=0.20)
    equity_path = np.concatenate([np.linspace(1.0, 1.3, 50), np.linspace(1.3, 0.95, 30)]) * value
    trip_at = None
    for i, e in enumerate(equity_path):
        if ks.update(e) and trip_at is None:
            trip_at = i
    book = {"RELIANCE": 100, "TCS": -50}
    print(f"peak ${ks.peak:,.0f} | tripped at step {trip_at} "
          f"(drawdown {ks.drawdown(equity_path[trip_at]):.1%})")
    print(f"flatten orders: {flatten_orders(book)}")

    _plot(port.values, rep, value)
    return {"var": rep, "kupiec": kp}


def _plot(returns, rep, value) -> None:
    RESULTS.mkdir(exist_ok=True)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(9, 5))
        ax.hist(returns * value, bins=80, color="#888780", alpha=0.7)
        ax.axvline(-rep["historical_var"], color="#dc2626", ls="--",
                   label=f"VaR {rep['historical_var']:,.0f}")
        ax.axvline(-rep["historical_cvar"], color="#7f1d1d", ls=":",
                   label=f"CVaR {rep['historical_cvar']:,.0f}")
        ax.set_xlabel("daily P&L ($)"); ax.set_ylabel("days")
        ax.set_title("portfolio daily P&L with 99% VaR / CVaR"); ax.legend()
        fig.tight_layout(); fig.savefig(RESULTS / "var_distribution.png", dpi=110); plt.close(fig)
    except Exception as exc:  # noqa: BLE001
        print(f"(plot skipped: {exc})")


if __name__ == "__main__":
    main()
