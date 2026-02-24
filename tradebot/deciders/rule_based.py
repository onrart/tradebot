from __future__ import annotations

from tradebot.deciders.base import BaseDecider, normalize_decision
from tradebot.models.context import BotContext


class RuleBasedDecider(BaseDecider):
    def decide(self, context: BotContext) -> dict:
        ema_fast = context.indicators.get("ema_9", 0)
        ema_slow = context.indicators.get("ema_21", 0)
        rsi_v = context.indicators.get("rsi_14", 50)
        action = "hold"
        reason = "No strong signal"
        size = 0.0

        if ema_fast > ema_slow and rsi_v < 70:
            action = "buy"
            reason = "EMA bullish and RSI below overbought"
            size = 0.1
        elif ema_fast < ema_slow and context.position.qty > 0:
            action = "close"
            reason = "Trend weakening while in position"
            size = 1.0
        elif rsi_v > 75 and context.position.qty > 0:
            action = "sell"
            reason = "RSI overbought"
            size = 0.5

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
