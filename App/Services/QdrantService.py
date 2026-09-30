from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import uuid
from App.Services.EmbeddingService import create_embeddings

client = QdrantClient(
    url="http://localhost:6333"
)

COLLECTION_NAME = "documents"


if not client.collection_exists(COLLECTION_NAME):
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=768,
            distance=Distance.COSINE
        )
    )


def store_embeddings(
    chunks: list[str],
    embeddings,
    filename: str,
    strategy: str
):
    points = []

    for i, (chunk, embedding) in enumerate(
        zip(chunks, embeddings)
    ):

        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding.tolist(),
            payload={
                "filename": filename,
                "chunk_index": i,
                "text": chunk,
                "strategy": strategy
            }
        )

        points.append(point)

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )


def search_embeddings(
    query: str,
    limit: int = 5
):
    query_embedding = create_embeddings([query])[0]

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding.tolist(),
        limit=limit,
        with_payload=True
    )

    return results.points