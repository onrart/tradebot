from __future__ import annotations

from tradebot.deciders.base import BaseDecider, DEFAULT_DECISION
from tradebot.deciders.llm_utils import build_prompt, parse_decision_json
from tradebot.models.context import BotContext


class OpenAIDecider(BaseDecider):
    def __init__(self, api_key: str | None, model: str = "gpt-4o-mini") -> None:
        self.api_key = api_key
        self.model = model

    def decide(self, context: BotContext) -> dict:
        if not self.api_key:
            return {**DEFAULT_DECISION, "fallback_reason": "OPENAI_API_KEY missing"}
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": build_prompt(context)}],
                temperature=0,
            )
            return parse_decision_json(response.choices[0].message.content or "")
        except Exception as exc:
            return {**DEFAULT_DECISION, "fallback_reason": f"OpenAI error: {exc}"}
