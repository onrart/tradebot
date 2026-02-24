from __future__ import annotations

from tradebot.config.settings import BotConfig
from tradebot.deciders.base import BaseDecider
from tradebot.deciders.gemini_decider import GeminiDecider
from tradebot.deciders.ollama_decider import OllamaDecider
from tradebot.deciders.openai_decider import OpenAIDecider
from tradebot.deciders.rule_based import RuleBasedDecider
from tradebot.utils.logger import get_logger


def create_decider(cfg: BotConfig) -> BaseDecider:
    logger = get_logger("tradebot.decider")
    provider = cfg.provider
    if provider == "OpenAI":
        if not cfg.openai_api_key:
            logger.warning("OpenAI key missing, falling back to RuleBased")
            return RuleBasedDecider()
        return OpenAIDecider(cfg.openai_api_key, cfg.model)
    if provider == "Gemini":
        if not cfg.gemini_api_key:
            logger.warning("Gemini key missing, falling back to RuleBased")
            return RuleBasedDecider()
        return GeminiDecider(cfg.gemini_api_key, cfg.model)
    if provider == "Ollama":
        return OllamaDecider(cfg.ollama_base_url, cfg.model)
    return RuleBasedDecider()
