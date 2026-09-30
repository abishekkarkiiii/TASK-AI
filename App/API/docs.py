from fastapi import APIRouter, UploadFile, File
from pypdf import PdfReader
from App.Services.EmbeddingService import create_embeddings
from App.Services import SentenceService as st
from App.Services.QdrantService import store_embeddings

router = APIRouter(
    prefix="/docs",
    tags=["Document"]
)


@router.post("/ingest")
async def ingest_document(
    file: UploadFile = File(...),
    strategy: str = "sentence"
):

    reader = PdfReader(file.file)

    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    if strategy == "sentence":
        chunks = st.sentence_chunking(text)

    elif strategy == "fixed":
        chunks = st.fixed_size_chunking(text)

    else:
        return {
            "error": "Invalid strategy. Use 'sentence' or 'fixed'"
        }

    embeddings = create_embeddings(chunks)

    store_embeddings(
        chunks=chunks,
        embeddings=embeddings,
        filename=file.filename,
        strategy=strategy
    )

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "strategy": strategy,
        "total_chunks": len(chunks),
        "chunk_sizes": [len(chunk) for chunk in chunks],
        "embedding_shape": embeddings.shape
    }


