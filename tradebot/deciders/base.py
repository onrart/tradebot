from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict
from typing import Any

from tradebot.models.context import BotContext, Decision


class BaseDecider(ABC):
    @abstractmethod
    def decide(self, context: BotContext) -> dict[str, Any]:
        raise NotImplementedError


DEFAULT_DECISION = asdict(Decision())


def normalize_decision(data: dict[str, Any]) -> dict[str, Any]:
    action = str(data.get("action", "hold")).lower()
    if action not in {"buy", "sell", "hold", "close"}:
        action = "hold"
    confidence = float(data.get("confidence", 0.0))
    confidence = max(0.0, min(1.0, confidence))
    size = float(data.get("position_size_pct", 0.0))
    return {
        "action": action,
        "confidence": confidence,
        "reason": str(data.get("reason", ""))[:500],
        "position_size_pct": max(0.0, min(1.0, size)),
        "stop_loss": data.get("stop_loss"),
        "take_profit": data.get("take_profit"),
    }
