from __future__ import annotations

import time

import pandas as pd
import requests


def fetch_ohlcv(base_url: str, market_type: str, symbol: str, interval: str, limit: int = 200) -> pd.DataFrame:
    endpoint = "/fapi/v1/klines" if market_type == "futures" else "/api/v3/klines"
    params = {"symbol": symbol.upper(), "interval": interval, "limit": limit}
    for attempt in range(3):
        try:
            resp = requests.get(f"{base_url}{endpoint}", params=params, timeout=15)
            resp.raise_for_status()
            raw = resp.json()
            df = pd.DataFrame(raw, columns=[
                "open_time", "open", "high", "low", "close", "volume", "close_time", "qav", "trades", "tb", "tq", "ignore"
            ])
            for col in ["open", "high", "low", "close", "volume"]:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            return df[["open_time", "open", "high", "low", "close", "volume"]].dropna()
        except Exception:
            if attempt == 2:
                raise
            time.sleep(0.5 * (attempt + 1))
    raise RuntimeError("unreachable")
