from __future__ import annotations

from tradebot.config.settings import BotConfig
from tradebot.data.market_data import fetch_ohlcv
from tradebot.deciders.base import DEFAULT_DECISION, normalize_decision
from tradebot.deciders.factory import create_decider
from tradebot.exchange.binance_client import BinanceClient
from tradebot.execution.paper import PaperWallet
from tradebot.execution.service import ExecutionService
from tradebot.history.store import InMemoryHistory
from tradebot.indicators.ta import compute_indicator_snapshot
from tradebot.loggingx.logger import get_logger, get_recent_logs
from tradebot.models.context import BotContext
from tradebot.portfolio.service import PortfolioService
from tradebot.risk.manager import RiskManager


class BotService:
    def __init__(self, cfg: BotConfig) -> None:
        self.cfg = cfg
        self.logger = get_logger("tradebot.service")
        self.history = InMemoryHistory(cfg.state_file)
        self.wallet = PaperWallet(wallet_balance=cfg.paper_starting_balance, available_balance=cfg.paper_starting_balance)
        self.exchange = BinanceClient(cfg.market_type, cfg.binance_testnet)
        self.execution = ExecutionService(cfg, self.history, self.wallet, self.exchange)
        self.risk = RiskManager(cfg)
        self.portfolio = PortfolioService()
        self.decider = create_decider(cfg)
        self.emergency_stop = cfg.emergency_stop
        self.last_decision = DEFAULT_DECISION.copy()

    def set_emergency_stop(self, enabled: bool) -> None:
        self.emergency_stop = enabled

    def refresh_only(self) -> dict:
        return self._snapshot(error=None)

    def run_once(self) -> dict:
        try:
            c1 = fetch_ohlcv(self.exchange.base_url, self.cfg.market_type, self.cfg.default_symbol, self.cfg.timeframe_fast, self.cfg.lookback)
            c5 = fetch_ohlcv(self.exchange.base_url, self.cfg.market_type, self.cfg.default_symbol, self.cfg.timeframe_slow, self.cfg.lookback)
            self.logger.info("tick.data_fetched", extra={"extra_data": {"symbol": self.cfg.default_symbol, "rows": len(c1)}})
            indicators = compute_indicator_snapshot(c1)
            latest_price = float(c1.iloc[-1]["close"])
            positions = []
            if self.wallet.base_qty > 0:
                positions.append(self.portfolio.build_position(self.cfg.default_symbol, self.wallet.base_qty, self.wallet.entry_price, latest_price))

            context = BotContext(
                symbol=self.cfg.default_symbol,
                market_type=self.cfg.market_type,
                latest_price=latest_price,
                indicators=indicators,
                balances={"wallet": self.wallet.wallet_balance, "available": self.wallet.available_balance},
                positions=positions,
                recent_orders=self.history.list_orders(10),
                candles_1m=c1.tail(20).to_dict("records"),
                candles_5m=c5.tail(20).to_dict("records"),
            )

            decision = normalize_decision(self.decider.decide(context))
            self.last_decision = decision
            self.logger.info("tick.decision", extra={"extra_data": decision})

            ok, msg = self.risk.validate(
                self.cfg.default_symbol,
                decision,
                self.wallet.available_balance,
                open_positions=1 if self.wallet.base_qty > 0 else 0,
                session_realized_pnl=self.portfolio.session_realized_pnl,
            )
            self.logger.info("tick.risk", extra={"extra_data": {"ok": ok, "reason": msg}})
            if not ok:
                return self._snapshot(order_result={"status": "blocked", "reason": msg}, error=None)

            order_result = self.execution.execute(self.cfg.default_symbol, latest_price, decision, self.emergency_stop)
            if "realized_pnl" in order_result:
                self.portfolio.session_realized_pnl += float(order_result["realized_pnl"])
            if order_result.get("status") in {"filled", "simulated"}:
                self.risk.register_trade(self.cfg.default_symbol)
            self.logger.info("tick.execution", extra={"extra_data": order_result})
            return self._snapshot(order_result=order_result, error=None)
        except Exception as exc:
            self.logger.exception("tick.failed")
            return self._snapshot(order_result={"status": "error"}, error=str(exc))

    def close_all_positions(self) -> dict:
        price = self.exchange.get_latest_price(self.cfg.default_symbol)
        result = self.execution.close_all(self.cfg.default_symbol, price)
        if "realized_pnl" in result:
            self.portfolio.session_realized_pnl += float(result["realized_pnl"])
        return self._snapshot(order_result=result, error=None)

    def _snapshot(self, order_result: dict | None = None, error: str | None = None) -> dict:
        try:
            price = self.exchange.get_latest_price(self.cfg.default_symbol)
        except Exception:
            price = self.wallet.entry_price
        positions = []
        if self.wallet.base_qty > 0:
            positions.append(self.portfolio.build_position(self.cfg.default_symbol, self.wallet.base_qty, self.wallet.entry_price, price))
        cards = self.portfolio.account_cards(self.wallet.wallet_balance, self.wallet.available_balance, positions)
        return {
            "symbol": self.cfg.default_symbol,
            "mode": self.cfg.bot_mode,
            "market_type": self.cfg.market_type,
            "account_cards": cards,
            "positions": self.portfolio.position_table(positions),
            "recent_orders": self.history.list_orders(20),
            "last_decision": self.last_decision,
            "order_result": order_result or {"status": "hold"},
            "emergency_stop": self.emergency_stop,
            "logs": get_recent_logs(80),
            "error": error,
        }
