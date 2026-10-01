from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from App.Database.database import get_db
from App.Database.models import Document
from App.Schemas.schemas import ChunkStrategy, DocumentOut, IngestResponse
from App.Services.chunking import chunk_text
from App.Services.embedding_service import create_embeddings
from App.Services.qdrant_service import store_embeddings
from App.Services.text_extractor import UnsupportedFileError, extract_text

router = APIRouter(prefix="/docs", tags=["Document"])


@router.post("/ingest", response_model=IngestResponse)
def ingest_document(
    file: UploadFile = File(...),
    strategy: ChunkStrategy = ChunkStrategy.SENTENCE,
    db: Session = Depends(get_db),
) -> IngestResponse:
    filename = file.filename or "unknown"

    try:
        text = extract_text(filename, file.file.read())
    except UnsupportedFileError as exc:
        raise HTTPException(status_code=415, detail=str(exc)) from exc

    chunks = chunk_text(text, strategy)
    if not chunks:
        raise HTTPException(status_code=422, detail="No text could be extracted")

    document = Document(
        filename=filename,
        content_type=file.content_type,
        strategy=strategy.value,
        total_chunks=len(chunks),
        total_characters=len(text),
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    embeddings = create_embeddings(chunks)
    store_embeddings(
        chunks=chunks,
        embeddings=embeddings,
        document_id=document.id,
        filename=filename,
        strategy=strategy.value,
    )

    return IngestResponse(
        document_id=document.id,
        filename=filename,
        content_type=file.content_type,
        strategy=strategy,
        total_chunks=len(chunks),
        chunk_sizes=[len(c) for c in chunks],
        embedding_dimension=int(embeddings.shape[1]),
    )


@router.get("/", response_model=list[DocumentOut])
def list_documents(db: Session = Depends(get_db)) -> list[Document]:
    return list(db.scalars(select(Document).order_by(Document.id.desc())))
