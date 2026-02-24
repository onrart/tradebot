from __future__ import annotations

import time

from tradebot.config.settings import BotConfig


class RiskManager:
    def __init__(self, cfg: BotConfig) -> None:
        self.cfg = cfg
        self.last_trade_ts: dict[str, float] = {}

    def validate(self, symbol: str, decision: dict, available_balance: float, open_positions: int, session_realized_pnl: float) -> tuple[bool, str]:
        if decision["action"] == "buy" and open_positions >= self.cfg.max_positions:
            return False, "max_positions limit"
        if decision.get("position_size_pct", 0.0) > self.cfg.max_position_size_pct:
            return False, "max_position_size_pct limit"
        if -session_realized_pnl >= self.cfg.max_daily_loss_usdt:
            return False, "max_daily_loss_usdt reached"
        if decision["action"] == "buy" and available_balance <= 0:
            return False, "insufficient available balance"
        now = time.time()
        if now - self.last_trade_ts.get(symbol, 0) < self.cfg.cooldown_seconds:
            return False, "cooldown active"
        return True, "ok"

    def register_trade(self, symbol: str) -> None:
        self.last_trade_ts[symbol] = time.time()
