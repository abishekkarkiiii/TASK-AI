# Palm Mind AI - RAG Backend

FastAPI backend with document ingestion and a custom conversational RAG API
(no LangChain RetrievalQA, no FAISS/Chroma, no UI).

## Stack
- FastAPI, Pydantic v2
- Qdrant (vector DB), `all-mpnet-base-v2` embeddings
- Redis (chat memory + in-progress booking state)
- SQLite via SQLAlchemy 2 (document metadata + bookings)
- OpenRouter LLM (OpenAI-compatible client)

## Run
```bash
docker compose up -d            # Qdrant + Redis
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # add OPENROUTER_API_KEY
uvicorn App.main:app --reload
```
Docs at http://localhost:8000/docs

## Endpoints
| Method | Path | Purpose |
|---|---|---|
| POST | `/docs/ingest?strategy=sentence\|fixed` | Upload .pdf/.txt, chunk, embed, store |
| GET | `/docs/` | List ingested document metadata |
| GET | `/search/?query=...` | Raw vector search |
| POST | `/chat/` | Conversational RAG + interview booking |
| GET | `/bookings/` | List stored bookings |

### Chat example
```json
POST /chat/
{"session_id": "abc123", "message": "Book an interview for me"}
```
The LLM classifies intent and extracts name/email/date/time, missing fields are
asked for across turns (draft kept in Redis), validated, then saved to the DB.
Any other message goes through the RAG pipeline: Redis history -> Qdrant top-k
-> prompt -> LLM -> save history.

## Structure
```
App/
  main.py  config.py
  API/       docs.py search.py chat.py booking.py
  Database/  database.py models.py
  Schemas/   schemas.py
  Services/  text_extractor chunking embedding_service qdrant_service
             cache_service llm_service booking_service rag_service
```
