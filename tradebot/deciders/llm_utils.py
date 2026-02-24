from __future__ import annotations

import json
from typing import Any

from tradebot.deciders.base import DEFAULT_DECISION, normalize_decision
from tradebot.models.context import BotContext


def build_prompt(context: BotContext) -> str:
    return (
        "Return only JSON with fields action, confidence, reason, position_size_pct, stop_loss, take_profit. "
        "Action must be buy|sell|hold|close. "
        f"symbol={context.symbol}, price={context.latest_price}, indicators={context.indicators}, "
        f"position_qty={context.position.qty}, balances={context.balances}, recent_orders={context.recent_orders[:5]}"
    )


def parse_decision_json(content: str) -> dict[str, Any]:
    try:
        start = content.find("{")
        end = content.rfind("}")
        if start == -1 or end == -1:
            return DEFAULT_DECISION.copy()
        payload = json.loads(content[start : end + 1])
        if not isinstance(payload, dict):
            return DEFAULT_DECISION.copy()
        return normalize_decision(payload)
    except Exception:
        return DEFAULT_DECISION.copy()
