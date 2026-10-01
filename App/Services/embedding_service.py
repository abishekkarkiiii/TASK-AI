from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

from App.config import get_settings


@lru_cache
def _get_model() -> SentenceTransformer:
    return SentenceTransformer(get_settings().embedding_model)


def create_embeddings(texts: list[str]) -> np.ndarray:
    return _get_model().encode(texts, show_progress_bar=False)
