"""Pre-trade risk limits (Phase 6.3).

Before an order is sent, `RiskManager.check_order` enforces caps on per-position
size, sector exposure, and gross leverage (all as a fraction of equity). Orders
that reduce risk pass; orders that would breach a cap are resized down to the
binding limit, or blocked outright when there's no room.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class RiskLimits:
    max_position_pct: float = 0.20    # |position value| / equity
    max_sector_pct: float = 0.40      # |sector gross| / equity
    max_gross_pct: float = 2.0        # sum |position value| / equity


class RiskManager:
    def __init__(self, limits: RiskLimits, sector_map: Optional[dict] = None):
        self.limits = limits
        self.sector_map = sector_map or {}

    def check_order(self, symbol, signed_qty, price, positions, prices, equity):
        """Return (approved_signed_qty, reason). reason in {ok, resized, blocked}."""
        if signed_qty == 0 or price <= 0 or equity <= 0:
            return 0, "ok"
        cur = positions.get(symbol, 0)
        new = cur + signed_qty
        if abs(new) <= abs(cur):
            return signed_qty, "ok"               # risk-reducing -> always allowed

        sign = 1 if new > 0 else -1
        caps = [self.limits.max_position_pct * equity]

        gross_excl = sum(abs(positions.get(s, 0)) * prices.get(s, price)
                         for s in positions if s != symbol)
        caps.append(self.limits.max_gross_pct * equity - gross_excl)

        if self.sector_map:
            sector = self.sector_map.get(symbol)
            sector_excl = sum(
                abs(positions.get(s, 0)) * prices.get(s, price)
                for s in positions if s != symbol and self.sector_map.get(s) == sector
            )
            caps.append(self.limits.max_sector_pct * equity - sector_excl)

        max_value = max(min(caps), 0.0)
        max_shares = int(max_value / price)
        if max_shares <= abs(cur):
            return 0, "blocked"

        target_new = sign * min(abs(new), max_shares)
        approved = target_new - cur
        return approved, ("ok" if approved == signed_qty else "resized")
