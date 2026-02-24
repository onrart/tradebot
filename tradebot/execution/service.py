from __future__ import annotations

import math

from tradebot.config.settings import BotConfig
from tradebot.exchange.binance_client import BinanceSpotClient
from tradebot.execution.paper import PaperWallet
from tradebot.history.store import InMemoryHistory
from tradebot.models.context import Position


class ExecutionService:
    def __init__(self, cfg: BotConfig, history: InMemoryHistory, wallet: PaperWallet, exchange_client: BinanceSpotClient) -> None:
        self.cfg = cfg
        self.history = history
        self.wallet = wallet
        self.exchange_client = exchange_client

    def _round_step(self, qty: float, step: float) -> float:
        return math.floor(qty / step) * step if step > 0 else qty

    def execute(self, symbol: str, price: float, decision: dict) -> dict:
        action = decision["action"]
        size_pct = decision.get("position_size_pct", 0.0)
        if action == "hold":
            return {"status": "hold", "details": "No order"}

        if self.cfg.mode == "live" and not self.cfg.live_trading_enabled:
            return {"status": "blocked", "details": "Live mode disabled by guard"}

        rules = self.exchange_client.get_symbol_rules(symbol)
        if self.cfg.mode == "paper":
            return self._execute_paper(symbol, action, price, size_pct, rules)
        return self._execute_demo_live(symbol, action, price, size_pct, rules)

    def _execute_paper(self, symbol: str, action: str, price: float, size_pct: float, rules: dict) -> dict:
        if action == "buy":
            quote_amount = self.wallet.quote_balance * size_pct
            if quote_amount < rules["min_notional"]:
                return {"status": "rejected", "details": "min_notional"}
            qty = self._round_step(quote_amount / price, rules["step_size"])
            filled = self.wallet.buy(price, qty * price)
            self.history.add_order(symbol, "BUY", filled, price, self.cfg.mode, "FILLED")
            return {"status": "filled", "side": "BUY", "qty": filled}
        if action in {"sell", "close"}:
            qty = self.wallet.base_qty if action == "close" else self.wallet.base_qty * max(size_pct, 0.0)
            qty = self._round_step(qty, rules["step_size"])
            filled = self.wallet.sell(price, qty)
            self.history.add_order(symbol, "SELL", filled, price, self.cfg.mode, "FILLED")
            return {"status": "filled", "side": "SELL", "qty": filled}
        return {"status": "hold", "details": "unsupported action"}

    def _execute_demo_live(self, symbol: str, action: str, price: float, size_pct: float, rules: dict) -> dict:
        # TODO: signed order endpoint integration.
        if action == "buy" and self.wallet.quote_balance * size_pct < rules["min_notional"]:
            return {"status": "rejected", "details": "min_notional"}
        self.history.add_order(symbol, action.upper(), 0.0, price, self.cfg.mode, "SIMULATED")
        return {"status": "simulated", "details": "Demo/Live adapter placeholder"}

    def position(self, symbol: str) -> Position:
        return Position(symbol=symbol, qty=self.wallet.base_qty, entry_price=self.wallet.entry_price)
