"""LLM provider abstraction — swap the provider without touching product logic."""
from __future__ import annotations

import json
import logging
import re
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """All LLM providers must implement this interface."""

    @abstractmethod
    def chat(self, messages: list[dict], max_tokens: int = 600) -> str:
        """Send a messages list and return the assistant's text response."""

    @property
    @abstractmethod
    def model_name(self) -> str: ...


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini") -> None:
        from openai import OpenAI
        self._client = OpenAI(api_key=api_key)
        self._model = model

    @property
    def model_name(self) -> str:
        return self._model

    def chat(self, messages: list[dict], max_tokens: int = 600) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return response.choices[0].message.content or ""


class StubProvider(LLMProvider):
    """Keyword-based fallback when no API key is set. Keeps the endpoint alive."""

    @property
    def model_name(self) -> str:
        return "stub"

    def chat(self, messages: list[dict], max_tokens: int = 600) -> str:
        last_user = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"), ""
        ).lower()
        if any(w in last_user for w in ["desafio", "challenge", "difícil", "hard", "difficult"]):
            return "Ok. Algo pequeno: escolhe uma conversa de 2 minutos com alguém que normalmente ignoras. Não precisa de ser profunda — só real."
        if any(w in last_user for w in ["fácil", "easier", "simples", "demais", "simple"]):
            return "Justo. Vamos reduzir: em vez da ação completa, faz só a primeira parte — abre o livro, envia a mensagem, ou entra na sala. Isso conta."
        if any(w in last_user for w in ["hoje não", "not today", "não consigo", "cansado", "tired"]):
            return "Tudo bem. Hoje não é dia para forçar. Queres registar o que está a bloquear-te, ou voltar amanhã com mais calma?"
        return "Vamos tornar isto concreto. O que está sob o teu controlo agora, e qual é a ação mais pequena que podes testar nas próximas horas?"


def _build_provider() -> LLMProvider:
    from .config import settings
    key = settings.openai_api_key
    if key:
        logger.info("LLM provider: OpenAI (%s)", settings.model_name)
        return OpenAIProvider(api_key=key, model=settings.model_name)
    logger.warning("OPENAI_API_KEY not set — using StubProvider")
    return StubProvider()


_provider: LLMProvider | None = None


def get_provider() -> LLMProvider:
    global _provider
    if _provider is None:
        _provider = _build_provider()
    return _provider


# ── Rule-based insight extraction (no extra LLM call) ─────────────────────────

_TOPIC_KEYWORDS: dict[str, list[str]] = {
    "social": ["amigo", "friend", "conversa", "relação", "social", "people", "pessoa"],
    "learning": ["aprender", "study", "estudar", "escola", "school", "livro", "book", "conhecimento"],
    "health": ["saúde", "health", "dormir", "sleep", "ansiedade", "anxiety", "cansado", "tired"],
    "creative": ["criar", "creative", "arte", "art", "música", "music", "escrever", "write"],
    "projects": ["projeto", "project", "negócio", "business", "trabalho", "work", "objetivo"],
    "self_knowledge": ["identidade", "identity", "quem sou", "who am i", "propósito", "purpose"],
}

_GOAL_WORDS = ["quero", "want", "gostava", "would like", "objetivo", "goal", "planear", "plan"]
_BLOCKER_WORDS = ["medo", "fear", "difícil", "hard", "bloqueio", "block", "não consigo", "can't", "não sei", "don't know"]
_TONE_MAP = {
    "anxious": ["ansioso", "nervous", "stressed", "stress", "afraid", "medo"],
    "motivated": ["motivado", "motivated", "entusiasmado", "excited", "quero", "want"],
    "discouraged": ["cansado", "tired", "desistir", "give up", "não consigo", "can't", "frustrado"],
}


def extract_insights(user_message: str) -> dict:
    """Lightweight rule-based extraction — no extra API call needed."""
    msg = user_message.lower()

    topics = [t for t, kws in _TOPIC_KEYWORDS.items() if any(k in msg for k in kws)] or ["general"]
    has_goal = any(w in msg for w in _GOAL_WORDS)
    has_blocker = any(w in msg for w in _BLOCKER_WORDS)

    tone = "neutral"
    for t, kws in _TONE_MAP.items():
        if any(k in msg for k in kws):
            tone = t
            break

    return {
        "topics": topics[:2],
        "has_goal": has_goal,
        "has_blocker": has_blocker,
        "emotional_tone": tone,
    }
