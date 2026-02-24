from __future__ import annotations

import json

from tradebot.deciders.base import DEFAULT_DECISION, normalize_decision
from tradebot.models.context import BotContext


def build_prompt(context: BotContext) -> str:
    return (
        "Return only strict JSON: action, confidence, reason, position_size_pct, stop_loss, take_profit. "
        f"symbol={context.symbol}, market={context.market_type}, price={context.latest_price}, "
        f"indicators={context.indicators}, balances={context.balances}, positions={len(context.positions)}"
    )


def parse_decision_json(text: str) -> dict:
    try:
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end == -1:
            return DEFAULT_DECISION.copy()
        parsed = json.loads(text[start : end + 1])
        if not isinstance(parsed, dict):
            return DEFAULT_DECISION.copy()
        return normalize_decision(parsed)
    except Exception:
        return DEFAULT_DECISION.copy()
