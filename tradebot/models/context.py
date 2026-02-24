from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class NormalizedPosition:
    symbol: str
    side: str
    qty: float
    entry_price: float
    mark_price: float
    leverage: float | None = None
    liquidation_price: float | None = None
    unrealized_pnl: float = 0.0
    pnl_pct: float = 0.0
    position_notional: float = 0.0
    opened_at: str | None = None


@dataclass(slots=True)
class Decision:
    action: str = "hold"
    confidence: float = 0.0
    reason: str = "default hold"
    position_size_pct: float = 0.0
    stop_loss: float | None = None
    take_profit: float | None = None
    fallback_reason: str | None = None


@dataclass(slots=True)
class BotContext:
    symbol: str
    market_type: str
    latest_price: float
    indicators: dict[str, float]
    balances: dict[str, float]
    positions: list[NormalizedPosition]
    recent_orders: list[dict[str, Any]]
    candles_1m: list[dict[str, Any]] = field(default_factory=list)
    candles_5m: list[dict[str, Any]] = field(default_factory=list)
