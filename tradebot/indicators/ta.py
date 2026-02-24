from __future__ import annotations

import pandas as pd


def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss.replace(0, 1e-9)
    return 100 - (100 / (1 + rs))


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high_low = (df["high"] - df["low"]).abs()
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(period).mean()


def compute_indicator_snapshot(df: pd.DataFrame) -> dict[str, float]:
    work = df.copy()
    work["ema_9"] = ema(work["close"], 9)
    work["ema_21"] = ema(work["close"], 21)
    work["rsi_14"] = rsi(work["close"], 14)
    work["atr_14"] = atr(work, 14)
    latest = work.iloc[-1]
    return {
        "ema_9": float(latest["ema_9"]),
        "ema_21": float(latest["ema_21"]),
        "rsi_14": float(latest["rsi_14"]),
        "atr_14": float(latest["atr_14"]),
    }
