# Backtest Engine (Pillar 2 · Phase 2)

An **event-driven** backtester (not vectorized) — it mirrors the real execution
loop and structurally prevents lookahead bias.

**Planned components**
- Event dataclasses: `MarketEvent`, `SignalEvent`, `OrderEvent`, `FillEvent`.
- A single event queue + dispatch loop.
- A data handler that replays bars from TimescaleDB one timestamp at a time,
  exposing only data up to "now" (no peeking ahead — proven by a test).
- Portfolio / position tracker (cash, holdings, value).
- Performance: returns, equity curve, max drawdown, Sharpe.

**Demo target:** an equity curve + metrics from a momentum strategy, with a test
proving no future bar is accessible mid-replay.
