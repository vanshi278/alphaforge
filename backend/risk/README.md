# Risk Engine (Pillar 6 · Phase 6)

A live safety system: measure tail risk, validate the risk model, gate orders,
and cut the book in a crisis.

## What's here

| File | Role |
|------|------|
| `var.py` | 99% 1-day VaR & CVaR — historical, parametric (Gaussian), Monte-Carlo |
| `kupiec.py` | Kupiec POF backtest — are VaR breaches as frequent as they should be? |
| `limits.py` | `RiskManager.check_order` — per-position / sector / gross caps (resize or block) |
| `kill_switch.py` | `DrawdownKillSwitch` — flatten the book when drawdown breaches a threshold |

## Run it
```bash
cd backend && python -m risk.run_risk
```

## Result (equal-weight 5-name portfolio, $1M, 2018–2024)

| Method | 99% VaR | 99% CVaR |
|--------|--------:|---------:|
| Historical | $34,366 | $54,955 |
| Parametric | $28,269 | $32,517 |
| Monte-Carlo | $28,495 | $32,747 |

The three agree in ballpark, but **historical VaR exceeds the Gaussian methods**
— real returns have fat tails (the 2020 crash), which a normal distribution
under-states. CVaR ≥ VaR everywhere, by construction.

- **Kupiec backtest:** 15 breaches over 1,230 days vs 12.3 expected (p = 0.45) →
  the model is **not rejected** — well-calibrated.
- **Limits:** a BUY worth ~290% of equity is resized to the 20% per-name cap; a
  14.5% order passes untouched.
- **Kill switch:** a simulated path peaking at $1.3M trips at −20.4% drawdown and
  emits flatten orders for every open position.

## Status
- [x] 6.1 VaR / CVaR (historical, parametric, Monte-Carlo)
- [x] 6.2 Kupiec exception backtest
- [x] 6.3 Position / sector / gross limit checks (resize or block)
- [x] 6.4 Drawdown circuit-breaker / kill switch
