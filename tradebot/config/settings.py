from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
from typing import Literal

from dotenv import load_dotenv

Mode = Literal["paper", "demo", "live"]
Provider = Literal["RuleBased", "OpenAI", "Gemini", "Ollama"]
MarketType = Literal["spot", "futures"]


@dataclass(slots=True)
class BotConfig:
    python_version: str = "3.11"
    bot_mode: Mode = "paper"
    market_type: MarketType = "spot"
    default_symbol: str = "DOGEUSDT"
    decision_interval_seconds: int = 10
    ui_refresh_interval_seconds: int = 2
    binance_testnet: bool = True
    live_trading_enabled: bool = False

    decider_provider: Provider = "RuleBased"
    decider_model: str = "rule-v1"
    openai_api_key: str | None = None
    gemini_api_key: str | None = None
    ollama_base_url: str = "http://localhost:11434"

    binance_api_key: str | None = None
    binance_api_secret: str | None = None
    binance_test_api_key: str | None = None
    binance_test_api_secret: str | None = None

    max_positions: int = 3
    max_position_size_pct: float = 20.0
    max_daily_loss_usdt: float = 5.0
    cooldown_seconds: int = 30
    allow_pyramiding: bool = False
    emergency_stop: bool = False
    paper_starting_balance: float = 1000.0

    timeframe_fast: str = "1m"
    timeframe_slow: str = "5m"
    lookback: int = 200

    state_file: str = "tradebot_state.json"


def _getenv_bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default).lower()).lower() == "true"


def load_config(env_path: str | Path = ".env") -> BotConfig:
    load_dotenv(dotenv_path=env_path, override=False)
    mode = os.getenv("BOT_MODE", "paper").lower()
    if mode not in {"paper", "demo", "live"}:
        mode = "paper"

    market_type = os.getenv("MARKET_TYPE", "spot").lower()
    if market_type not in {"spot", "futures"}:
        market_type = "spot"

    provider = os.getenv("DECIDER_PROVIDER", "RuleBased")
    if provider not in {"RuleBased", "OpenAI", "Gemini", "Ollama"}:
        provider = "RuleBased"

    return BotConfig(
        python_version=os.getenv("PYTHON_VERSION", "3.11"),
        bot_mode=mode,  # type: ignore[arg-type]
        market_type=market_type,  # type: ignore[arg-type]
        default_symbol=os.getenv("DEFAULT_SYMBOL", "DOGEUSDT").upper(),
        decision_interval_seconds=int(os.getenv("DECISION_INTERVAL_SECONDS", "10")),
        ui_refresh_interval_seconds=int(os.getenv("UI_REFRESH_INTERVAL_SECONDS", "2")),
        binance_testnet=_getenv_bool("BINANCE_TESTNET", True),
        live_trading_enabled=_getenv_bool("LIVE_TRADING_ENABLED", False),
        decider_provider=provider,  # type: ignore[arg-type]
        decider_model=os.getenv("DECIDER_MODEL", "rule-v1"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        binance_api_key=os.getenv("BINANCE_API_KEY"),
        binance_api_secret=os.getenv("BINANCE_API_SECRET"),
        binance_test_api_key=os.getenv("BINANCE_TEST_API_KEY"),
        binance_test_api_secret=os.getenv("BINANCE_TEST_API_SECRET"),
        max_positions=int(os.getenv("MAX_POSITIONS", "3")),
        max_position_size_pct=float(os.getenv("MAX_POSITION_SIZE_PCT", "20")),
        max_daily_loss_usdt=float(os.getenv("MAX_DAILY_LOSS_USDT", "5")),
        cooldown_seconds=int(os.getenv("COOLDOWN_SECONDS", "30")),
        allow_pyramiding=_getenv_bool("ALLOW_PYRAMIDING", False),
        emergency_stop=_getenv_bool("EMERGENCY_STOP", False),
        paper_starting_balance=float(os.getenv("PAPER_STARTING_BALANCE", "1000")),
        state_file=os.getenv("STATE_FILE", "tradebot_state.json"),
    )
