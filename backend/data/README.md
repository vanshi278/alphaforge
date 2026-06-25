# Data Layer (Pillar 1 · Phase 1)

Ingest real-time and historical market data concurrently from multiple sources
and store it as time series.

**Planned components**
- `load_history(symbol, start, end, interval)` → clean OHLCV DataFrame (UTC).
- TimescaleDB read/write helpers for the `ticks` and `bars` hypertables
  (schema in [`db/init.sql`](../../db/init.sql)).
- Async WebSocket client(s) for live broker feeds (Zerodha Kite / Upstox / Angel One).
- Redis pub/sub bus: publish ticks to `ticks:<SYMBOL>`; DB writer + frontend subscribe.
- A common normalized tick format across all sources.

**Demo target:** concurrent pipeline WebSocket → Redis → TimescaleDB from 3 sources.
