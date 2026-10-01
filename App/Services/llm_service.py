import json
import re
from datetime import date
from functools import lru_cache
from typing import Any

from openai import OpenAI

from App.config import get_settings

settings = get_settings()

RAG_SYSTEM_PROMPT = """You are a helpful assistant.

Answer the user's question using the provided context and conversation history.

Rules:
- Use the provided context as the primary source.
- Use conversation history to resolve references such as "it", "that", "those".
- Do not invent information.
- If the answer is not available, say you don't know."""

BOOKING_EXTRACTION_PROMPT = """You extract interview-booking details from a chat.
Today's date is {today}.

Return ONLY a JSON object, no markdown, with these keys:
- "intent": "booking" if the user wants to book/schedule/reschedule an interview
  or is supplying booking details, "cancel" if they want to abort the booking,
  otherwise "other".
- "name": full name or null
- "email": email address or null
- "date": date as YYYY-MM-DD (resolve words like "tomorrow" or "next Monday") or null
- "time": 24-hour HH:MM or null

Only use values the user actually stated. Use null for anything missing.
{draft_hint}"""


@lru_cache
def _get_client() -> OpenAI:
    if not settings.openrouter_api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not configured")
    return OpenAI(
        base_url=settings.openrouter_base_url, api_key=settings.openrouter_api_key
    )


def generate_answer(
    context: str, question: str, history: list[dict[str, str]]
) -> str:
    messages: list[dict[str, str]] = [
        {"role": "system", "content": RAG_SYSTEM_PROMPT},
        *history,
        {
            "role": "user",
            "content": f"Context:\n\n{context}\n\nCurrent question:\n\n{question}",
        },
    ]
    response = _get_client().chat.completions.create(
        model=settings.llm_model, messages=messages  # type: ignore[arg-type]
    )
    return response.choices[0].message.content or ""


def extract_booking_details(
    message: str,
    history: list[dict[str, str]],
    draft: dict[str, str] | None,
) -> dict[str, Any]:
    draft_hint = (
        f"A booking is already in progress with these details: {json.dumps(draft)}."
        if draft is not None
        else ""
    )
    system = BOOKING_EXTRACTION_PROMPT.format(
        today=date.today().isoformat(), draft_hint=draft_hint
    )
    messages = [
        {"role": "system", "content": system},
        *history[-4:],
        {"role": "user", "content": message},
    ]
    try:
        response = _get_client().chat.completions.create(
            model=settings.llm_model,
            messages=messages,  # type: ignore[arg-type]
            temperature=0,
        )
        raw = response.choices[0].message.content or ""
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        data = json.loads(match.group(0)) if match else {}
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}
