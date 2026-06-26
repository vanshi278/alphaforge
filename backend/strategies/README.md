# Alpha / Strategy Module (Pillar 3 · Phase 3)

Pluggable strategies behind a common base class, so ideas compete on equal footing.
All engine strategies emit standardized `SignalEvent`s — either discrete
(`LONG`/`EXIT`) or target-weight (`target_pct`), which the portfolio rebalances to
(this is what enables shorting and dollar-neutral books).

## What's here

| File | Strategy | Idea |
|------|----------|------|
| `base.py` | `Strategy` (ABC) | `calculate_signals(event) -> list[SignalEvent]` |
| `buy_and_hold.py` | `BuyAndHold` | plumbing sanity check |
| `ma_crossover.py` | `MACrossover` | trend: long when short SMA > long SMA |
| `mean_reversion.py` | `PairsTradingStrategy` | trade the z-score of a cointegrated spread |
| `cross_sectional_momentum.py` | `CrossSectionalMomentum` | monthly long top / short bottom decile |
| `cointegration.py` | — | Engle-Granger pair screening + hedge ratio |
| `market_making.py` | `MarketMaker` | inventory-skewed two-sided quoting (standalone sim) |

`MarketMaker` is **not** an engine `Strategy` — market making is a quote/inventory
game, so it's a standalone tick-level simulation (`python -m strategies.market_making`).
The realistic limit-order-book version arrives in Phase 5.

## Run it

```bash
cd backend
python -m backtest.run_backtest --symbols TCS,INFY --strategy pairs --lookback 60
python -m backtest.run_backtest --symbols RELIANCE,TCS,INFY,HDFCBANK,ICICIBANK,SBIN,ITC,LT \
    --strategy crosssec --lookback 126 --quantile 0.3
python -m backtest.compare            # the Phase 3.5 comparison report
python -m strategies.market_making    # bounded-inventory MM sim
```

## Status

- [x] 3.1 Base `Strategy` class (MA crossover refactored onto it in Phase 2)
- [x] 3.2 Mean reversion — cointegration (Engle-Granger) + spread z-score pairs
- [x] 3.3 Cross-sectional momentum — monthly long/short, dollar-neutral
- [x] 3.4 Market making — two-sided quotes, inventory skew, bounded inventory
- [x] 3.5 Comparison report — return / Sharpe / max DD / turnover table + plot
