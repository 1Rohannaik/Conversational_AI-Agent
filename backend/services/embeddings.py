from functools import lru_cache
import os
from typing import List
from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=1)
def _get_sbert_model() -> SentenceTransformer:
    model_name = os.getenv("SBERT_MODEL_NAME", "all-MiniLM-L6-v2")
    return SentenceTransformer(model_name)


class STEmbeddings:
    """Sentence-Transformers embeddings wrapper compatible with LangChain vectorstores."""

    def __init__(self) -> None:
        self._model = _get_sbert_model()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._model.encode(texts, normalize_embeddings=True).tolist()

    def embed_query(self, text: str) -> List[float]:
        return self._model.encode([text], normalize_embeddings=True)[0].tolist()
