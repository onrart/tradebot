from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path


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
    def __init__(self, state_file: str = "tradebot_state.json", maxlen: int = 200) -> None:
        self._orders: deque[OrderRecord] = deque(maxlen=maxlen)
        self.state_path = Path(state_file)
        self.load_state()

    def add_order(self, symbol: str, side: str, qty: float, price: float, mode: str, status: str) -> None:
        self._orders.appendleft(OrderRecord(symbol, side, qty, price, mode, status, datetime.now(timezone.utc).isoformat()))
        self.save_state()

    def list_orders(self, limit: int = 20) -> list[dict]:
        return [asdict(order) for order in list(self._orders)[:limit]]

    def save_state(self) -> None:
        payload = {"orders": [asdict(x) for x in self._orders]}
        self.state_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))

    def load_state(self) -> None:
        if not self.state_path.exists():
            return
        try:
            raw = json.loads(self.state_path.read_text())
            for item in raw.get("orders", []):
                self._orders.append(OrderRecord(**item))
        except Exception:
            return
