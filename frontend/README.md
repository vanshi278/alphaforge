# React Dashboard (Pillar 7 · Phase 7)

The cockpit — what people see. Scaffolded in Phase 7.

**Planned stack:** React + Vite + Tailwind + [`lightweight-charts`](https://github.com/tradingview/lightweight-charts) (TradingView, free).

**Planned panels**
- Live candlestick + order-book depth ladder (WebSocket from the backend, fed off Redis).
- P&L / equity curve, drawdown chart, open-positions table.
- Backtest runner UI (pick strategy, symbols, date range, params → run → view).
- Risk panel: live VaR, exposure gauges, drawdown bar, kill-switch status.

> Placeholder until Phase 7. The backend already exposes `/` and `/health`
> (and Swagger UI at `/docs`) for the frontend to build against.
