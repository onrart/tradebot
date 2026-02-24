from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Position:
    symbol: str
    qty: float = 0.0
    entry_price: float = 0.0


@dataclass(slots=True)
class Decision:
    action: str = "hold"
    confidence: float = 0.0
    reason: str = "default hold"
    position_size_pct: float = 0.0
    stop_loss: float | None = None
    take_profit: float | None = None


@dataclass(slots=True)
class BotContext:
    symbol: str
    latest_price: float
    indicators: dict[str, float]
    balances: dict[str, float]
    position: Position
    candles_1m: list[dict[str, Any]] = field(default_factory=list)
    candles_5m: list[dict[str, Any]] = field(default_factory=list)
    recent_orders: list[dict[str, Any]] = field(default_factory=list)
