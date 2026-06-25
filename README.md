# AlphaForge — Systematic Trading & Research Platform

> A mini version of what a quant desk runs internally: **data in → research & signals in the middle → execution & risk out.** Built on Indian equities (NSE / Nifty), not crypto.

**Status:** 🚧 Work in progress, built in vertical slices. **✅ Phase 0 — Setup & Foundations is complete:** the repo skeleton, Dockerized TimescaleDB + Redis, and a runnable FastAPI backend with live health checks.

---

## What it is

AlphaForge ingests real-time and historical market data, researches and generates
trading signals, simulates **realistic** order execution against a limit-order-book,
and runs a **live risk engine** — all surfaced through a React dashboard. It is
designed as a portfolio-grade demonstration of the full systematic-trading stack,
with an emphasis on the things quants actually care about: no lookahead bias,
honest out-of-sample evaluation, and realistic execution cost.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       REACT DASHBOARD                        │
│   live charts · order book · P&L · risk panel · backtest UI  │
└───────────────────────────┬─────────────────────────────────┘
                            │ WebSocket / REST
┌───────────────────────────┴─────────────────────────────────┐
│                  FASTAPI BACKEND (async)                     │
├──────────┬───────────┬────────────┬───────────┬─────────────┤
│  DATA    │ BACKTEST  │   ALPHA    │ EXECUTION │    RISK      │
│  LAYER   │  ENGINE   │  + ML      │  ENGINE   │   ENGINE     │
└──────────┴───────────┴────────────┴───────────┴─────────────┘
       │                                              │
┌──────┴──────────┐                        ┌──────────┴────────┐
│  TimescaleDB +  │                        │  Live broker API  │
│     Redis       │                        │  or paper-trading │
└─────────────────┘                        └───────────────────┘
```

## The 7 pillars

| # | Pillar | What it does | Phase |
|---|--------|--------------|-------|
| 1 | **Data Layer** | Concurrent real-time + historical ingestion → TimescaleDB, Redis pub/sub bus | 1 |
| 2 | **Backtest Engine** | Event-driven loop with structural lookahead-bias protection | 2 |
| 3 | **Alpha / Strategy** | Pluggable strategies: mean reversion, momentum, market making | 3 |
| 4 | **ML / Forecasting** | Forward-return rank prediction, walk-forward CV, IC, SHAP | 4 |
| 5 | **Execution Engine** | LOB simulator + Almgren-Chriss vs TWAP/VWAP, implementation shortfall | 5 |
| 6 | **Risk Engine** | Live VaR/CVaR, exposure limits, drawdown kill switch | 6 |
| 7 | **React Dashboard** | Live charts, depth ladder, P&L, risk panel, backtest runner | 7 |

## Tech decisions

| Layer | Choice | Why |
|-------|--------|-----|
| **Asset class** | NSE equities (Nifty) | Signals local-market awareness; differentiates from crypto-bot resumes |
| **Backend** | FastAPI (async) | First-class async/WebSocket support for real-time data; what newer quant shops use |
| **Database** | TimescaleDB (Postgres) | Time-series done properly — what real shops use, not CSV dumps |
| **Cache / bus** | Redis pub/sub | One live tick stream that strategy + frontend + DB writer all subscribe to |
| **Backtest** | Event-driven (not vectorized) | Mirrors the real execution loop; structurally avoids lookahead bias |
| **ML target** | Forward-return rank / direction | Raw price prediction is a red flag; evaluate with IC + walk-forward CV |
| **Execution** | LOB sim + Almgren-Chriss + TWAP/VWAP | Realistic slippage and price impact, measured in BPS |
| **Frontend** | React + Vite + Tailwind + lightweight-charts | Industry-standard, fast charts (TradingView, free) |
| **Deploy** | Docker Compose | One-command spin-up |

## Project structure

```
AI_TRADING_PLATFORM/
├── backend/
│   ├── api/            # FastAPI app (REST + WebSocket)  ← runnable now
│   ├── data/           # ingestion + storage            (Phase 1)
│   ├── backtest/       # event-driven engine            (Phase 2)
│   ├── strategies/     # pluggable alpha                (Phase 3)
│   ├── ml/             # forecasting models             (Phase 4)
│   ├── execution/      # LOB sim + Almgren-Chriss        (Phase 5)
│   ├── risk/           # VaR / limits / kill switch     (Phase 6)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/           # React dashboard                (Phase 7)
├── notebooks/          # research / EDA / reports
├── db/
│   └── init.sql        # TimescaleDB hypertables (ticks, bars)
├── docker-compose.yml
├── .env.example
└── README.md
```

## Getting started

### Prerequisites
- **Docker Desktop** (with Docker Compose v2+) — for TimescaleDB, Redis, and the backend.
- **Python 3.11+** — only if you want to run/develop the backend outside Docker.

### 1. Clone
```bash
git clone https://github.com/vanshi278/alphaforge.git
cd alphaforge
```

### 2. Spin up the stack (one command)
```bash
docker compose up -d
```
This starts:
- **TimescaleDB** on `localhost:5432` (hypertables `ticks` and `bars` created automatically from [`db/init.sql`](db/init.sql))
- **Redis** on `localhost:6379`
- **Backend API** on `localhost:8000`

Verify it's healthy:
```bash
curl http://localhost:8000/health
# {"status":"ok","services":{"timescaledb":"up","redis":"up"}}
```
Interactive API docs (Swagger UI): **http://localhost:8000/docs**

> Just the data services, without the backend container:
> `docker compose up -d timescaledb redis`

### 3. Backend dev environment (optional — for local hacking)
```bash
cp .env.example .env          # POSTGRES_HOST/REDIS_URL already default to localhost
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# run the API against the Dockerized DB + Redis
cd backend && uvicorn api.main:app --reload
```

## Build roadmap (progress)

- [x] **Phase 0 — Setup & Foundations** · repo skeleton, env, Docker (TimescaleDB + Redis), runnable FastAPI health check
- [ ] **Phase 1 — Data Layer** · historical loader, TimescaleDB I/O, live WebSocket feed, Redis pub/sub, 3 concurrent sources
- [ ] **Phase 2 — Event-Driven Backtester** · event loop, replay handler, portfolio, momentum strategy, equity curve
- [ ] **Phase 3 — Alpha / Strategy** · base class, mean reversion, cross-sectional momentum, market making, comparison
- [ ] **Phase 4 — ML / Forecasting** · features, rank target, walk-forward CV, LightGBM, IC report, SHAP
- [ ] **Phase 5 — Execution + LOB** · order book, matching engine, Almgren-Chriss, TWAP/VWAP, implementation shortfall
- [ ] **Phase 6 — Risk Engine** · VaR/CVaR, Kupiec test, limits, drawdown kill switch
- [ ] **Phase 7 — React Dashboard** · live charts, depth ladder, P&L, backtest runner, risk panel
- [ ] **Phase 8 — Polish** · results-led README, one-command spin-up, tests, write-up

## Disclaimer

Educational / research project. **Not investment advice.** No warranty; use at your own risk.
