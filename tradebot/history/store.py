from __future__ import annotations

from collections import deque
from dataclasses import dataclass, asdict
from datetime import datetime, timezone


@dataclass(slots=True)
class OrderRecord:
    symbol: str
    side: str
    qty: float
    price: float
    mode: str
    status: str
    ts: str


class InMemoryHistory:
    def __init__(self, maxlen: int = 100) -> None:
        self._orders: deque[OrderRecord] = deque(maxlen=maxlen)

    def add_order(self, symbol: str, side: str, qty: float, price: float, mode: str, status: str) -> None:
        self._orders.appendleft(
            OrderRecord(symbol=symbol, side=side, qty=qty, price=price, mode=mode, status=status, ts=datetime.now(timezone.utc).isoformat())
        )

    def list_orders(self, limit: int = 20) -> list[dict]:
        return [asdict(x) for x in list(self._orders)[:limit]]
