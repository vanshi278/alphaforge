# Risk Engine (Pillar 6 · Phase 6)

A live safety system running alongside execution.

**Planned components**
- VaR / CVaR: 99% 1-day via historical, parametric, and Monte Carlo.
- VaR backtest: Kupiec exception test.
- Limits & exposure checks: per-position caps, sector caps, gross/net limits,
  checked before each order (block or resize on breach).
- Drawdown circuit breaker / kill switch: flatten all positions on threshold breach.

**Demo target:** a live risk panel with VaR and a working kill switch.
