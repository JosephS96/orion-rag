from typing import Optional
from sentence_transformers import SentenceTransformer
from backend.config.settings import settings

_model: Optional[SentenceTransformer] = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.embedding_model)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    return get_model().encode(texts, show_progress_bar=False).tolist()


def embed_query(query: str) -> list[float]:
    return get_model().encode([query], show_progress_bar=False)[0].tolist()
