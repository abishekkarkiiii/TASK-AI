from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from App.API.booking import router as booking_router
from App.API.chat import router as chat_router
from App.API.docs import router as docs_router
from App.API.search import router as search_router
from App.Database.database import init_db


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


app = FastAPI(title="Palm Mind AI RAG API", lifespan=lifespan)

app.include_router(docs_router)
app.include_router(search_router)
app.include_router(chat_router)
app.include_router(booking_router)


@app.get("/", tags=["Main"])
def root() -> dict[str, str]:
    return {"message": "Palm Mind AI RAG API is running"}
