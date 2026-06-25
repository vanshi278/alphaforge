# Execution Engine + LOB Simulator (Pillar 5 · Phase 5)

Realistic order execution against a simulated limit order book — the headline
quant result.

**Planned components**
- Limit order book: `SortedDict` bids/asks, `deque` per price level, `order_map`
  for O(1) cancels.
- Matching engine: market orders walk the book level by level (visible impact).
- Poisson order-flow generator (exponential inter-arrivals, log-normal sizes).
- Price-impact model (Kyle's-lambda style temporary + permanent).
- Almgren-Chriss optimal execution (closed-form `sinh` trajectory, risk-aversion λ).
- TWAP / VWAP baselines.
- Implementation-shortfall comparison (BPS) across all three.

**Demo target:** "AC cut shortfall ~X BPS vs TWAP at matched risk." Then swap this
in as the backtester's fill engine, replacing the naive Phase 2 placeholder.
