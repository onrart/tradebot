from __future__ import annotations

from tradebot.config.settings import BotConfig
from tradebot.deciders.base import BaseDecider
from tradebot.deciders.gemini_decider import GeminiDecider
from tradebot.deciders.ollama_decider import OllamaDecider
from tradebot.deciders.openai_decider import OpenAIDecider
from tradebot.deciders.rule_based import RuleBasedDecider
from tradebot.loggingx.logger import get_logger


def create_decider(cfg: BotConfig) -> BaseDecider:
    logger = get_logger("tradebot.decider")
    provider = cfg.decider_provider
    if provider == "OpenAI":
        if not cfg.openai_api_key:
            logger.warning("OpenAI key missing -> RuleBased fallback")
            return RuleBasedDecider()
        return OpenAIDecider(cfg.openai_api_key, cfg.decider_model)
    if provider == "Gemini":
        if not cfg.gemini_api_key:
            logger.warning("Gemini key missing -> RuleBased fallback")
            return RuleBasedDecider()
        return GeminiDecider(cfg.gemini_api_key, cfg.decider_model)
    if provider == "Ollama":
        return OllamaDecider(cfg.ollama_base_url, cfg.decider_model)
    return RuleBasedDecider()
