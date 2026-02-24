from pathlib import Path

import pandas as pd

from tradebot.config.settings import load_config
from tradebot.deciders.rule_based import RuleBasedDecider
from tradebot.execution.paper import PaperWallet
from tradebot.indicators.ta import compute_indicator_snapshot
from tradebot.models.context import BotContext
from tradebot.portfolio.service import PortfolioService


def test_config_load_defaults(monkeypatch):
    monkeypatch.delenv("DECISION_INTERVAL_SECONDS", raising=False)
    cfg = load_config(".env.missing")
    assert cfg.bot_mode in {"paper", "demo", "live"}
    assert cfg.decision_interval_seconds == 10


def test_config_interval_override(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("DECISION_INTERVAL_SECONDS", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text("DECISION_INTERVAL_SECONDS=12\n")
    cfg = load_config(env_file)
    assert cfg.decision_interval_seconds == 12


def test_decider_schema_output():
    decider = RuleBasedDecider()
    ctx = BotContext(
        symbol="DOGEUSDT",
        market_type="futures",
        latest_price=0.1,
        indicators={"ema_9": 0.11, "ema_21": 0.1, "rsi_14": 50, "atr_14": 0.001},
        balances={"wallet": 1000, "available": 1000},
        positions=[],
        recent_orders=[],
    )
    decision = decider.decide(ctx)
    assert set(decision.keys()) == {"action", "confidence", "reason", "position_size_pct", "stop_loss", "take_profit", "fallback_reason"}


def test_indicator_pipeline():
    df = pd.DataFrame({
        "open": [1 + i * 0.1 for i in range(80)],
        "high": [1.1 + i * 0.1 for i in range(80)],
        "low": [0.9 + i * 0.1 for i in range(80)],
        "close": [1 + i * 0.1 for i in range(80)],
        "volume": [100] * 80,
    })
    out = compute_indicator_snapshot(df)
    assert {"ema_9", "ema_21", "rsi_14", "atr_14"}.issubset(out)


def test_paper_execution_core():
    wallet = PaperWallet(wallet_balance=1000, available_balance=1000)
    qty = wallet.buy(price=100, quote_amount=100)
    assert qty > 0
    sold, realized = wallet.sell(price=120, qty=qty)
    assert sold == qty
    assert realized > 0


def test_portfolio_normalization():
    svc = PortfolioService()
    pos = svc.build_position("DOGEUSDT", qty=100, entry_price=0.1, mark_price=0.11)
    cards = svc.account_cards(wallet_balance=1000, available_balance=900, positions=[pos])
    assert pos.unrealized_pnl > 0
    assert cards["equity"] >= cards["wallet_balance"]
