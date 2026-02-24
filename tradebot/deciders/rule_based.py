from __future__ import annotations

from tradebot.deciders.base import BaseDecider, normalize_decision
from tradebot.models.context import BotContext


class RuleBasedDecider(BaseDecider):
    def decide(self, context: BotContext) -> dict:
        ema_fast = context.indicators.get("ema_9", 0.0)
        ema_slow = context.indicators.get("ema_21", 0.0)
        rsi_v = context.indicators.get("rsi_14", 50.0)
        has_position = any(p.qty > 0 for p in context.positions)

        action = "hold"
        size = 0.0
        reason = "No strong signal"
        if ema_fast > ema_slow and rsi_v < 70:
            action, size, reason = "buy", 10.0, "EMA bullish"
        elif has_position and (ema_fast < ema_slow or rsi_v > 75):
            action, size, reason = "close", 100.0, "Trend reversal / RSI high"

        return normalize_decision(
            {
                "action": action,
                "confidence": 0.65,
                "reason": reason,
                "position_size_pct": size,
                "stop_loss": None,
                "take_profit": None,
            }
        )
