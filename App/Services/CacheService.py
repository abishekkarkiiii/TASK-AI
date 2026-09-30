import json

import redis


REDIS_URL = "redis://localhost:6379"

client = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True
)


def get_chat_history(
    session_id: str
) -> list[dict[str, str]]:

    history = client.get(
        f"chat:{session_id}"
    )

    if not history:
        return []

    return json.loads(history)


def save_chat_history(
    session_id: str,
    history: list[dict[str, str]]
) -> None:

    client.set(
        f"chat:{session_id}",
        json.dumps(history)
    )