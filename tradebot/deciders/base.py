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
    return {
        "action": action,
        "confidence": max(0.0, min(1.0, float(data.get("confidence", 0.0)))),
        "reason": str(data.get("reason", "")).strip()[:500],
        "position_size_pct": max(0.0, min(100.0, float(data.get("position_size_pct", 0.0)))),
        "stop_loss": float(data["stop_loss"]) if data.get("stop_loss") is not None else None,
        "take_profit": float(data["take_profit"]) if data.get("take_profit") is not None else None,
        "fallback_reason": str(data.get("fallback_reason")) if data.get("fallback_reason") else None,
    }
