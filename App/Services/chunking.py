import re
from collections.abc import Callable

from App.Schemas.schemas import ChunkStrategy

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def sentence_chunking(text: str, chunk_size: int = 500) -> list[str]:

    sentences = [s.strip() for s in _SENTENCE_SPLIT.split(text) if s.strip()]
    chunks: list[str] = []
    current = ""

    for sentence in sentences:
        if current and len(current) + len(sentence) + 1 > chunk_size:
            chunks.append(current)
            current = sentence
        else:
            current = f"{current} {sentence}".strip()

    if current:
        chunks.append(current)
    return chunks


def fixed_size_chunking(
    text: str, chunk_size: int = 500, overlap: int = 50
) -> list[str]:

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    text = text.strip()
    step = chunk_size - overlap
    chunks = [text[i : i + chunk_size].strip() for i in range(0, len(text), step)]
    return [c for c in chunks if c]


_STRATEGIES: dict[ChunkStrategy, Callable[[str], list[str]]] = {
    ChunkStrategy.SENTENCE: sentence_chunking,
    ChunkStrategy.FIXED: fixed_size_chunking,
}


def chunk_text(text: str, strategy: ChunkStrategy) -> list[str]:
    return _STRATEGIES[strategy](text)
