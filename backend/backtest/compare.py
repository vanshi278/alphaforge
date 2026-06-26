"""Phase 3.5 — strategy comparison report.

Runs each strategy through the same event-driven engine over the same window and
tabulates return / CAGR / Sharpe / max drawdown / turnover, with an overlaid
equity-curve plot. Strategies trade their natural universes (buy & hold and MA on
one name, pairs on a cointegrated pair, cross-sectional on a basket), so this
compares *approaches*, not a single instrument.

    cd backend && python -m backtest.compare
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from backtest.data import DataHandler
from backtest.engine import Backtest
from backtest.execution import SimulatedExecutionHandler
from backtest.performance import compute_metrics, turnover
from backtest.portfolio import Portfolio
from data.history import load_history
from strategies import BuyAndHold, CrossSectionalMomentum, MACrossover, PairsTradingStrategy

RESULTS = Path(__file__).resolve().parents[2] / "results"
UNIVERSE = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "ITC", "LT"]


def _load(symbols, start, end, interval="1d"):
    bars = {}
    for s in symbols:
        df = load_history(s, start, end, interval)
        if not df.empty:
            bars[s] = df
    return bars


def _run(factory, bars, capital=100_000.0):
    symbols = list(bars)
    data = DataHandler(bars, symbols)
    pf = Portfolio(data, symbols, initial_capital=capital)
    return Backtest(data, factory(data, symbols), pf, SimulatedExecutionHandler(data)).run()


def _print_table(table: pd.DataFrame) -> None:
    head = f"{'strategy':<26}{'return':>9}{'CAGR':>8}{'Sharpe':>8}{'maxDD':>9}{'turnover':>10}{'trades':>8}"
    print(head)
    print("-" * len(head))
    for name, r in table.iterrows():
        print(
            f"{name:<26}{r.total_return:>8.1%}{r.cagr:>8.1%}{r.sharpe:>8.2f}"
            f"{r.max_dd:>9.1%}{r.turnover:>10.1f}{int(r.trades):>8}"
        )


def run_comparison(start="2018-01-01", end="2024-01-01") -> pd.DataFrame:
    allbars = _load(UNIVERSE, start, end)
    one = {k: allbars[k] for k in ["RELIANCE"] if k in allbars}
    pair = {k: allbars[k] for k in ["TCS", "INFY"] if k in allbars}

    runs = {}
    if one:
        runs["buy & hold (RELIANCE)"] = _run(lambda d, s: BuyAndHold(d, s), one)
        runs["MA 20/50 (RELIANCE)"] = _run(lambda d, s: MACrossover(d, s, 20, 50), one)
    if len(pair) == 2:
        runs["pairs TCS/INFY"] = _run(
            lambda d, s: PairsTradingStrategy(d, s[0], s[1], lookback=60, entry_z=2.0, exit_z=0.5), pair
        )
    if len(allbars) >= 4:
        runs["x-sec momentum (basket)"] = _run(
            lambda d, s: CrossSectionalMomentum(d, s, lookback=126, quantile=0.3), allbars
        )

    rows, curves = [], {}
    for name, pf in runs.items():
        eq = pf.equity_curve()
        m = compute_metrics(eq)
        rows.append({
            "strategy": name,
            "total_return": m.get("total_return", 0.0),
            "cagr": m.get("cagr", 0.0),
            "sharpe": m.get("sharpe", 0.0),
            "max_dd": m.get("max_drawdown", 0.0),
            "turnover": turnover(pf.trades, eq),
            "trades": len(pf.trades),
        })
        curves[name] = eq["equity"]

    table = pd.DataFrame(rows).set_index("strategy")
    RESULTS.mkdir(exist_ok=True)
    table.to_csv(RESULTS / "comparison.csv")
    pd.DataFrame(curves).to_csv(RESULTS / "comparison_curves.csv")
    _save_plot(curves)
    return table


def _save_plot(curves: dict) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(10, 5))
        for name, series in curves.items():
            ax.plot(series.index, series.values, label=name)
        ax.axhline(1.0, color="#999", lw=0.8, ls="--")
        ax.set_ylabel("equity (×)")
        ax.set_title("strategy comparison")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)
        fig.tight_layout()
        fig.savefig(RESULTS / "comparison.png", dpi=110)
        plt.close(fig)
    except Exception as exc:  # noqa: BLE001
        print(f"(plot skipped: {exc})")


def main() -> None:
    table = run_comparison()
    print()
    _print_table(table)
    print(f"\nsaved: {RESULTS / 'comparison.csv'}  |  {RESULTS / 'comparison.png'}")


if __name__ == "__main__":
    main()
