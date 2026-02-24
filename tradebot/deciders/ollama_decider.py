from __future__ import annotations

import requests

from tradebot.deciders.base import BaseDecider, DEFAULT_DECISION
from tradebot.deciders.llm_utils import build_prompt, parse_decision_json
from tradebot.models.context import BotContext


class OllamaDecider(BaseDecider):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.1") -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    def decide(self, context: BotContext) -> dict:
        try:
            resp = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": build_prompt(context), "stream": False},
                timeout=30,
            )
            resp.raise_for_status()
            content = resp.json().get("response", "")
            return parse_decision_json(content)
        except Exception:
            return DEFAULT_DECISION.copy()
