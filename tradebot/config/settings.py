from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
from typing import Literal

from dotenv import load_dotenv


Mode = Literal["paper", "demo", "live"]
Provider = Literal["RuleBased", "OpenAI", "Gemini", "Ollama"]


@dataclass(slots=True)
class BotConfig:
    symbol: str = "BTCUSDT"
    interval_seconds: int = 10
    mode: Mode = "paper"
    provider: Provider = "RuleBased"
    model: str = "rule-v1"
    timeframe_fast: str = "1m"
    timeframe_slow: str = "5m"
    lookback: int = 200
    starting_balance: float = 10_000.0
    position_size_pct: float = 0.1
    max_positions: int = 1
    max_position_size_pct: float = 0.25
    cooldown_seconds: int = 0
    binance_testnet: bool = True
    live_trading_enabled: bool = False
    openai_api_key: str | None = None
    gemini_api_key: str | None = None
    ollama_base_url: str = "http://localhost:11434"
    binance_api_key: str | None = None
    binance_api_secret: str | None = None


def load_config(env_path: str | Path = ".env") -> BotConfig:
    load_dotenv(dotenv_path=env_path, override=False)
    mode = os.getenv("BOT_MODE", "paper").lower()
    if mode not in {"paper", "demo", "live"}:
        mode = "paper"
    return BotConfig(
        symbol=os.getenv("BOT_SYMBOL", "BTCUSDT").upper(),
        interval_seconds=int(os.getenv("BOT_INTERVAL_SECONDS", "10")),
        mode=mode,  # type: ignore[arg-type]
        provider=os.getenv("DECIDER_PROVIDER", "RuleBased"),  # type: ignore[arg-type]
        model=os.getenv("DECIDER_MODEL", "rule-v1"),
        starting_balance=float(os.getenv("PAPER_STARTING_BALANCE", "10000")),
        position_size_pct=float(os.getenv("POSITION_SIZE_PCT", "0.1")),
        max_positions=int(os.getenv("MAX_POSITIONS", "1")),
        max_position_size_pct=float(os.getenv("MAX_POSITION_SIZE_PCT", "0.25")),
        cooldown_seconds=int(os.getenv("COOLDOWN_SECONDS", "0")),
        binance_testnet=os.getenv("BINANCE_TESTNET", "true").lower() == "true",
        live_trading_enabled=os.getenv("LIVE_TRADING_ENABLED", "false").lower() == "true",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        binance_api_key=os.getenv("BINANCE_API_KEY"),
        binance_api_secret=os.getenv("BINANCE_API_SECRET"),
    )
