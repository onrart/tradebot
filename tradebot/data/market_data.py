from __future__ import annotations

import pandas as pd
import requests


BINANCE_BASE = "https://api.binance.com"
BINANCE_TESTNET_BASE = "https://testnet.binance.vision"


def fetch_ohlcv(symbol: str, interval: str, limit: int = 200, testnet: bool = False) -> pd.DataFrame:
    base_url = BINANCE_TESTNET_BASE if testnet else BINANCE_BASE
    resp = requests.get(
        f"{base_url}/api/v3/klines",
        params={"symbol": symbol.upper(), "interval": interval, "limit": limit},
        timeout=15,
    )
    resp.raise_for_status()
    raw = resp.json()
    df = pd.DataFrame(raw, columns=[
        "open_time", "open", "high", "low", "close", "volume", "close_time", "qav",
        "trades", "taker_base", "taker_quote", "ignore"
    ])
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df[["open_time", "open", "high", "low", "close", "volume"]].dropna()
