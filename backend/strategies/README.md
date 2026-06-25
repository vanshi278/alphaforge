# Alpha / Strategy Module (Pillar 3 · Phase 3)

Pluggable strategies behind a common base class, so ideas compete on equal footing.

**Planned components**
- `Strategy` base class: `calculate_signals(market_event) -> SignalEvent | None`.
- Mean reversion — cointegrated pairs (Engle-Granger), trade the spread Z-score.
- Cross-sectional momentum — rank a universe, long top / short bottom decile.
- Market making — quote both sides around mid, manage and skew on inventory.
- A strategy comparison report: return, Sharpe, max DD, turnover.

All strategies emit standardized `SignalEvent`s so the engine treats them identically.
