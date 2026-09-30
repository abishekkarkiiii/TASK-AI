from fastapi import APIRouter

from App.Services.QdrantService import search_embeddings
from App.Services.LLMService import generate_answer
from App.Services.CacheService import (
    get_chat_history,
    save_chat_history
)
router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post("/")
def chat(question: str,session_id: str):


    history = get_chat_history(session_id)
    results = search_embeddings(
        query=question,
        limit=5
    )

    context = "\n\n".join(
        result.payload["text"]
        for result in results
    )

    answer = generate_answer(
        context=context,
        question=question,
        history=history
    )

    history.append(
        {
            "role": "user",
            "content": question
        }
    )

    history.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    save_chat_history(
        session_id=session_id,
        history=history
    )

    return {
        "question": question,
        "answer": answer
    }