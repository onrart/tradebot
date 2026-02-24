from __future__ import annotations

from tradebot.config.settings import BotConfig
from tradebot.data.market_data import fetch_ohlcv
from tradebot.deciders.base import DEFAULT_DECISION, normalize_decision
from tradebot.deciders.factory import create_decider
from tradebot.exchange.binance_client import BinanceSpotClient
from tradebot.execution.paper import PaperWallet
from tradebot.execution.service import ExecutionService
from tradebot.history.store import InMemoryHistory
from tradebot.indicators.ta import compute_indicator_snapshot
from tradebot.models.context import BotContext
from tradebot.risk.manager import RiskManager
from tradebot.utils.logger import get_logger


class BotService:
    def __init__(self, cfg: BotConfig) -> None:
        self.cfg = cfg
        self.logger = get_logger("tradebot.service")
        self.history = InMemoryHistory(maxlen=200)
        self.wallet = PaperWallet(quote_balance=cfg.starting_balance)
        self.exchange_client = BinanceSpotClient(testnet=cfg.binance_testnet)
        self.execution = ExecutionService(cfg, self.history, self.wallet, self.exchange_client)
        self.risk = RiskManager(cfg)
        self.decider = create_decider(cfg)

    def run_once(self) -> dict:
        try:
            c1 = fetch_ohlcv(self.cfg.symbol, self.cfg.timeframe_fast, self.cfg.lookback, self.cfg.binance_testnet)
            c5 = fetch_ohlcv(self.cfg.symbol, self.cfg.timeframe_slow, self.cfg.lookback, self.cfg.binance_testnet)
            self.logger.info("tick.data_fetched", extra={"extra_data": {"symbol": self.cfg.symbol, "rows": len(c1)}})

            indicators = compute_indicator_snapshot(c1)
            latest_price = float(c1.iloc[-1]["close"])
            self.logger.info("tick.indicators", extra={"extra_data": indicators})

            ctx = BotContext(
                symbol=self.cfg.symbol,
                latest_price=latest_price,
                indicators=indicators,
                balances={"USDT": self.wallet.quote_balance},
                position=self.execution.position(self.cfg.symbol),
                candles_1m=c1.tail(20).to_dict("records"),
                candles_5m=c5.tail(20).to_dict("records"),
                recent_orders=self.history.list_orders(10),
            )

            decision = self.decider.decide(ctx) if self.decider else DEFAULT_DECISION.copy()
            decision = normalize_decision(decision)
            self.logger.info("tick.decision", extra={"extra_data": decision})

            ok, msg = self.risk.validate(
                self.cfg.symbol,
                decision,
                latest_price,
                self.wallet.quote_balance,
                open_positions=1 if self.wallet.base_qty > 0 else 0,
            )
            self.logger.info("tick.risk", extra={"extra_data": {"ok": ok, "msg": msg}})
            if not ok:
                return self._snapshot(decision=decision, order_result={"status": "blocked", "details": msg}, error=None)

            order_result = self.execution.execute(self.cfg.symbol, latest_price, decision)
            if order_result.get("status") in {"filled", "simulated"}:
                self.risk.register_trade(self.cfg.symbol)
            self.logger.info("tick.execution", extra={"extra_data": order_result})
            return self._snapshot(decision=decision, order_result=order_result, error=None)
        except Exception as exc:
            self.logger.exception("tick.failed")
            return self._snapshot(decision=DEFAULT_DECISION.copy(), order_result={"status": "error"}, error=str(exc))

    def _snapshot(self, decision: dict, order_result: dict, error: str | None) -> dict:
        try:
            last_price = self.exchange_client.get_latest_price(self.cfg.symbol)
        except Exception:
            last_price = self.wallet.entry_price if self.wallet.entry_price > 0 else 0.0
        return {
            "symbol": self.cfg.symbol,
            "mode": self.cfg.mode,
            "quote_balance": self.wallet.quote_balance,
            "base_qty": self.wallet.base_qty,
            "equity": self.wallet.equity(last_price),
            "position": self.execution.position(self.cfg.symbol),
            "decision": decision,
            "order_result": order_result,
            "recent_orders": self.history.list_orders(10),
            "error": error,
        }
