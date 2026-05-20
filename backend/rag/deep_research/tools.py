from backend.rag.retriever import retrieve


def search_documents(query: str, collections: list[str], top_k: int = 5) -> list[dict]:
    chunks = retrieve(query, collections, top_k=top_k)
    return [
        {
            "id": c.id,
            "title": c.title,
            "text": c.text,
            "source": c.source,
            "score": c.score,
        }
        for c in chunks
    ]
