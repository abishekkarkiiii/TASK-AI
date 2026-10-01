from sqlalchemy.orm import Session

from App.Schemas.schemas import ChatResponse
from App.Services import booking_service, cache_service, llm_service
from App.Services.qdrant_service import search_embeddings

TOP_K = 5


def chat(session_id: str, message: str, db: Session) -> ChatResponse:

    history = cache_service.get_chat_history(session_id)

    booking = booking_service.handle_booking(session_id, message, history, db)

    if booking is not None:
        answer, intent, sources = booking.reply, "booking", []
        booking_id = booking.booking_id
    else:
        results = search_embeddings(query=message, limit=TOP_K)
        context = "\n\n".join(str(r.payload["text"]) for r in results if r.payload)
        answer = llm_service.generate_answer(
            context=context, question=message, history=history
        )
        intent, booking_id = "question", None
        sources = sorted({str(r.payload["filename"]) for r in results if r.payload})

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": answer})
    cache_service.save_chat_history(session_id, history)

    return ChatResponse(
        session_id=session_id,
        answer=answer,
        intent=intent,
        sources=sources,
        booking_id=booking_id,
    )
