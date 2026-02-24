from __future__ import annotations

import math
import time

from tradebot.config.settings import BotConfig
from tradebot.exchange.binance_client import BinanceClient
from tradebot.execution.paper import PaperWallet
from tradebot.history.store import InMemoryHistory


class ExecutionService:
    def __init__(self, cfg: BotConfig, history: InMemoryHistory, wallet: PaperWallet, exchange_client: BinanceClient) -> None:
        self.cfg = cfg
        self.history = history
        self.wallet = wallet
        self.exchange_client = exchange_client
        self.last_order_ts: dict[tuple[str, str], float] = {}

    @staticmethod
    def _round_step(qty: float, step: float) -> float:
        return math.floor(qty / step) * step if step > 0 else qty

    def execute(self, symbol: str, price: float, decision: dict, emergency_stop: bool = False) -> dict:
        action = decision["action"]
        size_pct = decision.get("position_size_pct", 0.0) / 100.0
        if action == "hold":
            return {"status": "hold", "details": "No action"}
        if emergency_stop and action in {"buy", "sell"}:
            return {"status": "blocked", "details": "Emergency stop active"}
        if action in {"buy", "sell"}:
            key = (symbol, action)
            now = time.time()
            prev_ts = self.last_order_ts.get(key, 0.0)
            if now - prev_ts < 2.0:
                return {"status": "blocked", "details": "duplicate order guard (2s)"}
        if self.cfg.bot_mode == "live" and not self.cfg.live_trading_enabled:
            return {"status": "blocked", "details": "Live guard"}

        rules = self.exchange_client.get_symbol_rules(symbol)
        result = self._execute_paper(symbol, action, price, size_pct, rules)
        if result["status"] in {"filled", "simulated"} and action in {"buy", "sell"}:
            self.last_order_ts[(symbol, action)] = time.time()
        return result

    def _execute_paper(self, symbol: str, action: str, price: float, size_pct: float, rules: dict) -> dict:
        if action == "buy":
            quote_amount = self.wallet.available_balance * size_pct
            if quote_amount < rules["min_notional"]:
                return {"status": "rejected", "details": "min_notional"}
            qty = self._round_step(quote_amount / price, rules["step_size"])
            if qty < rules["min_qty"]:
                return {"status": "rejected", "details": "min_qty"}
            filled = self.wallet.buy(price, qty * price)
            self.history.add_order(symbol, "BUY", filled, price, self.cfg.bot_mode, "FILLED")
            return {"status": "filled", "side": "BUY", "qty": filled}

        if action in {"sell", "close"}:
            qty = self.wallet.base_qty if action == "close" else self.wallet.base_qty * size_pct
            qty = self._round_step(qty, rules["step_size"])
            filled, realized = self.wallet.sell(price, qty)
            self.history.add_order(symbol, "SELL", filled, price, self.cfg.bot_mode, "FILLED")
            return {"status": "filled", "side": "SELL", "qty": filled, "realized_pnl": realized}

        return {"status": "hold", "details": "unsupported"}

    def close_all(self, symbol: str, price: float) -> dict:
        if self.wallet.base_qty <= 0:
            return {"status": "noop", "details": "No open position"}
        return self._execute_paper(symbol, "close", price, 1.0, self.exchange_client.get_symbol_rules(symbol))
