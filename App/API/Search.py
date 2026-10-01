from fastapi import APIRouter, Query

from App.Schemas.schemas import SearchResponse, SearchResult
from App.Services.qdrant_service import search_embeddings

router = APIRouter(prefix="/search", tags=["Searching"])


@router.get("/", response_model=SearchResponse)
def search(query: str, limit: int = Query(5, ge=1, le=20)) -> SearchResponse:
    results = search_embeddings(query=query, limit=limit)
    return SearchResponse(
        query=query,
        results=[
            SearchResult(
                score=r.score,
                text=str(r.payload["text"]),
                filename=str(r.payload["filename"]),
                chunk_index=int(r.payload["chunk_index"]),
            )
            for r in results
            if r.payload
        ],
    )
