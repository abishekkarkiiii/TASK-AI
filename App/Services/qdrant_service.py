import uuid
from functools import lru_cache

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, ScoredPoint, VectorParams

from App.config import get_settings
from App.Services.embedding_service import create_embeddings

settings = get_settings()


@lru_cache
def get_client() -> QdrantClient:
    client = QdrantClient(url=settings.qdrant_url)
    if not client.collection_exists(settings.collection_name):
        client.create_collection(
            collection_name=settings.collection_name,
            vectors_config=VectorParams(
                size=settings.vector_size, distance=Distance.COSINE
            ),
        )
    return client


def store_embeddings(
    chunks: list[str],
    embeddings: np.ndarray,
    document_id: int,
    filename: str,
    strategy: str,
) -> None:
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding.tolist(),
            payload={
                "document_id": document_id,
                "filename": filename,
                "chunk_index": i,
                "text": chunk,
                "strategy": strategy,
            },
        )
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
    ]
    get_client().upsert(collection_name=settings.collection_name, points=points)


def search_embeddings(query: str, limit: int = 5) -> list[ScoredPoint]:
    query_vector = create_embeddings([query])[0]
    response = get_client().query_points(
        collection_name=settings.collection_name,
        query=query_vector.tolist(),
        limit=limit,
        with_payload=True,
    )
    return response.points
