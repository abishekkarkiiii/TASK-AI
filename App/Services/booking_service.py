from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from pydantic import EmailStr, TypeAdapter, ValidationError
from sqlalchemy.orm import Session

from App.Database.models import Booking
from App.Services import cache_service, llm_service

FIELDS = ("name", "email", "date", "time")
_email_adapter: TypeAdapter[str] = TypeAdapter(EmailStr)

PROMPTS = {
    "name": "your full name",
    "email": "your email address",
    "date": "the interview date (e.g. 2026-10-15)",
    "time": "the preferred time (e.g. 14:30)",
}


@dataclass
class BookingResult:
    reply: str
    booking_id: int | None = None


def _validate(field: str, value: Any) -> str | None:

    if not isinstance(value, str) or not value.strip():
        return None
    value = value.strip()
    try:
        if field == "email":
            return _email_adapter.validate_python(value)
        if field == "date":
            parsed = date.fromisoformat(value)
            return value if parsed >= date.today() else None
        if field == "time":
            return datetime.strptime(value, "%H:%M").strftime("%H:%M")
    except (ValidationError, ValueError):
        return None
    return value if len(value) <= 100 else None


def handle_booking(
    session_id: str,
    message: str,
    history: list[dict[str, str]],
    db: Session,
) -> BookingResult | None:

    draft = cache_service.get_booking_draft(session_id)
    extracted = llm_service.extract_booking_details(message, history, draft)
    intent = extracted.get("intent", "other")

    if draft is not None and intent == "cancel":
        cache_service.clear_booking_draft(session_id)
        return BookingResult("No problem, I've cancelled the booking request.")

    supplied = {
        f: v for f in FIELDS if (v := _validate(f, extracted.get(f))) is not None
    }

    if draft is None and intent != "booking":
        return None
    if draft is not None and intent != "booking" and not supplied:
        return None

    draft = {**(draft or {}), **supplied}
    missing = [f for f in FIELDS if f not in draft]

    if missing:
        cache_service.save_booking_draft(session_id, draft)
        return BookingResult(f"Got it! Could you please share {PROMPTS[missing[0]]}?")

    booking = Booking(**{f: draft[f] for f in FIELDS})
    db.add(booking)
    db.commit()
    db.refresh(booking)
    cache_service.clear_booking_draft(session_id)

    return BookingResult(
        f"Your interview is booked, {booking.name}! "
        f"{booking.date} at {booking.time}. "
        f"A confirmation will go to {booking.email}. (Booking ID: {booking.id})",
        booking_id=booking.id,
    )
