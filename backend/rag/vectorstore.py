from typing import Optional
import chromadb
from chromadb import Collection
from chromadb.api import ClientAPI
from backend.config.settings import settings
from backend.rag.embeddings import embed_texts
from backend.rag.loader import ParsedChunk

_client: Optional[ClientAPI] = None


def get_client() -> ClientAPI:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    return _client


def get_collection(name: str) -> Collection:
    return get_client().get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
    )


def upsert_chunks(chunks: list[ParsedChunk], collection_name: str) -> None:
    if not chunks:
        return
    collection = get_collection(collection_name)
    embeddings = embed_texts([c.text for c in chunks])
    collection.upsert(
        ids=[f"{c.source}::chunk::{c.chunk_index}" for c in chunks],
        embeddings=embeddings,
        documents=[c.text for c in chunks],
        metadatas=[{"source": c.source, "title": c.title, "chunk_index": c.chunk_index} for c in chunks],
    )


def delete_by_source(source: str, collection_name: str) -> None:
    collection = get_collection(collection_name)
    collection.delete(where={"source": source})


def collection_is_empty(collection_name: str) -> bool:
    return get_collection(collection_name).count() == 0


def list_sources(collection_name: str) -> list[dict]:
    collection = get_collection(collection_name)
    if collection.count() == 0:
        return []
    results = collection.get(include=["metadatas"])
    seen: dict[str, dict] = {}
    for meta in results["metadatas"]:
        src = meta["source"]
        if src not in seen:
            seen[src] = {"source": src, "title": meta["title"]}
    return list(seen.values())
