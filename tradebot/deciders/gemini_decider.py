from __future__ import annotations

from tradebot.deciders.base import BaseDecider, DEFAULT_DECISION
from tradebot.deciders.llm_utils import build_prompt, parse_decision_json
from tradebot.models.context import BotContext


class GeminiDecider(BaseDecider):
    def __init__(self, api_key: str | None, model: str = "gemini-1.5-flash") -> None:
        self.api_key = api_key
        self.model = model

    def decide(self, context: BotContext) -> dict:
        if not self.api_key:
            return DEFAULT_DECISION.copy()
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model)
            response = model.generate_content(build_prompt(context))
            return parse_decision_json(response.text or "")
        except Exception:
            return DEFAULT_DECISION.copy()
