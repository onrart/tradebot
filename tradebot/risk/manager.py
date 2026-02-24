from __future__ import annotations

import math
import time

from tradebot.config.settings import BotConfig


class RiskManager:
    def __init__(self, cfg: BotConfig) -> None:
        self.cfg = cfg
        self.last_trade_ts: dict[str, float] = {}

    def validate(self, symbol: str, decision: dict, price: float, quote_balance: float, open_positions: int) -> tuple[bool, str]:
        if open_positions >= self.cfg.max_positions and decision["action"] == "buy":
            return False, "max_positions limit"
        size = min(decision.get("position_size_pct", 0.0), self.cfg.max_position_size_pct)
        if size <= 0 and decision["action"] in {"buy", "sell"}:
            return False, "invalid size"
        if decision["action"] == "buy" and quote_balance * size < 5:
            return False, "below min notional"
        now = time.time()
        if self.cfg.cooldown_seconds > 0 and now - self.last_trade_ts.get(symbol, 0) < self.cfg.cooldown_seconds:
            return False, "cooldown active"
        if not math.isfinite(price) or price <= 0:
            return False, "invalid price"
        return True, "ok"

    def register_trade(self, symbol: str) -> None:
        self.last_trade_ts[symbol] = time.time()
