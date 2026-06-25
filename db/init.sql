-- AlphaForge — TimescaleDB schema.
-- Runs automatically on first container start via /docker-entrypoint-initdb.d.
-- This is the foundation the Phase 1 data layer writes to and reads from.

CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ---------------------------------------------------------------------------
-- Raw trade / quote ticks (the live feed lands here).
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ticks (
    time   TIMESTAMPTZ      NOT NULL,
    symbol TEXT             NOT NULL,
    price  DOUBLE PRECISION NOT NULL,
    size   DOUBLE PRECISION,
    side   TEXT
);
SELECT create_hypertable('ticks', 'time', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_ticks_symbol_time ON ticks (symbol, time DESC);

-- ---------------------------------------------------------------------------
-- OHLCV bars (any interval; the interval is kept as a column so daily and
-- intraday bars share one hypertable).
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bars (
    time     TIMESTAMPTZ      NOT NULL,
    symbol   TEXT             NOT NULL,
    interval TEXT             NOT NULL DEFAULT '1d',
    open     DOUBLE PRECISION,
    high     DOUBLE PRECISION,
    low      DOUBLE PRECISION,
    close    DOUBLE PRECISION,
    volume   DOUBLE PRECISION,
    PRIMARY KEY (symbol, interval, time)
);
SELECT create_hypertable('bars', 'time', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_bars_symbol_interval_time ON bars (symbol, interval, time DESC);
