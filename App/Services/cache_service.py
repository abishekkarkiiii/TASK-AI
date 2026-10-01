import json
from functools import lru_cache

import redis

from App.config import get_settings

settings = get_settings()


@lru_cache
def get_client() -> "redis.Redis[str]":
    return redis.Redis.from_url(settings.redis_url, decode_responses=True)


def _history_key(session_id: str) -> str:
    return f"chat:{session_id}"


def _draft_key(session_id: str) -> str:
    return f"booking_draft:{session_id}"


def get_chat_history(session_id: str) -> list[dict[str, str]]:
    raw = get_client().get(_history_key(session_id))
    return json.loads(raw) if raw else []


def save_chat_history(session_id: str, history: list[dict[str, str]]) -> None:
    trimmed = history[-settings.max_history_messages :]
    get_client().set(
        _history_key(session_id),
        json.dumps(trimmed),
        ex=settings.chat_ttl_seconds,
    )


def get_booking_draft(session_id: str) -> dict[str, str] | None:
    raw = get_client().get(_draft_key(session_id))
    return json.loads(raw) if raw else None


def save_booking_draft(session_id: str, draft: dict[str, str]) -> None:
    get_client().set(
        _draft_key(session_id), json.dumps(draft), ex=settings.chat_ttl_seconds
    )


def clear_booking_draft(session_id: str) -> None:
    get_client().delete(_draft_key(session_id))
