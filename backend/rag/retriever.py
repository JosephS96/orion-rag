from dataclasses import dataclass
from backend.config.settings import settings
from backend.rag.embeddings import embed_query
from backend.rag.vectorstore import get_collection


@dataclass
class RetrievedChunk:
    id: str
    text: str
    source: str
    title: str
    score: float


def retrieve(
    query: str,
    collection_names: list[str],
    top_k: int | None = None,
) -> list[RetrievedChunk]:
    k = top_k or settings.retrieval_top_k
    query_embedding = embed_query(query)
    results: list[RetrievedChunk] = []

    for col_name in collection_names:
        collection = get_collection(col_name)
        if collection.count() == 0:
            continue
        raw = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(k, collection.count()),
            include=["documents", "metadatas", "distances"],
        )
        for doc, meta, dist in zip(
            raw["documents"][0],
            raw["metadatas"][0],
            raw["distances"][0],
        ):
            results.append(RetrievedChunk(
                id=f"{meta['source']}::chunk::{meta['chunk_index']}",
                text=doc,
                source=meta["source"],
                title=meta["title"],
                score=1.0 - dist,  # cosine distance → similarity
            ))

    results.sort(key=lambda r: r.score, reverse=True)
    return results[:k]
