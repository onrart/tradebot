from tradebot.config.settings import load_config
from tradebot.deciders.rule_based import RuleBasedDecider
from tradebot.execution.paper import PaperWallet
from tradebot.indicators.ta import compute_indicator_snapshot
from tradebot.models.context import BotContext, Position
import pandas as pd


def test_config_load_defaults():
    cfg = load_config(".env.missing")
    assert cfg.mode in {"paper", "demo", "live"}


def test_decider_output_standard():
    decider = RuleBasedDecider()
    ctx = BotContext(
        symbol="BTCUSDT",
        latest_price=100,
        indicators={"ema_9": 102, "ema_21": 100, "rsi_14": 60, "atr_14": 1.2},
        balances={"USDT": 1000},
        position=Position(symbol="BTCUSDT", qty=0),
    )
    d = decider.decide(ctx)
    assert set(d.keys()) == {"action", "confidence", "reason", "position_size_pct", "stop_loss", "take_profit"}


def test_indicator_pipeline():
    df = pd.DataFrame({
        "open": [1 + i * 0.1 for i in range(60)],
        "high": [1.1 + i * 0.1 for i in range(60)],
        "low": [0.9 + i * 0.1 for i in range(60)],
        "close": [1 + i * 0.1 for i in range(60)],
        "volume": [100] * 60,
    })
    out = compute_indicator_snapshot(df)
    assert "ema_9" in out and "rsi_14" in out and "atr_14" in out


def test_paper_execution_flow():
    wallet = PaperWallet(quote_balance=1000)
    bought = wallet.buy(price=100, quote_amount=100)
    assert bought > 0
    sold = wallet.sell(price=110, qty=bought)
    assert sold == bought
    assert wallet.quote_balance > 1000
