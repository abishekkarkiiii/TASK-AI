from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from App.Database.database import get_db
from App.Schemas.schemas import ChatRequest, ChatResponse
from App.Services import rag_service

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    return rag_service.chat(payload.session_id, payload.message, db)
