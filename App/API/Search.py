from fastapi import APIRouter
from App.Services.QdrantService import search_embeddings

router = APIRouter(
    prefix="/search",
    tags=["Searching"]
)


@router.get("/")
def search(query: str, limit: int = 5):

    results = search_embeddings(
        query=query,
        limit=limit
    )

    return {
        "query": query,
        "results": [
            {
                "score": result.score,
                "text": result.payload["text"],
                "filename": result.payload["filename"],
                "chunk_index": result.payload["chunk_index"]
            }
            for result in results
        ]
    }