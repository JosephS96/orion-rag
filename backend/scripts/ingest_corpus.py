"""
One-time script to ingest the bundled corpus into the 'bundled' ChromaDB collection.
Run from the backend/ directory: python -m scripts.ingest_corpus
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.config.settings import settings
from backend.rag.loader import load_directory
from backend.rag.vectorstore import upsert_chunks, collection_is_empty, get_collection

CORPUS_DIR = Path(__file__).resolve().parents[1] / "data" / "corpus"


def ingest():
    if not collection_is_empty(settings.bundled_collection):
        count = get_collection(settings.bundled_collection).count()
        print(f"Bundled collection already has {count} chunks — skipping ingest.")
        return

    print(f"Loading documents from {CORPUS_DIR} ...")
    chunks = load_directory(CORPUS_DIR)
    if not chunks:
        print("No documents found. Add .txt/.pdf/.md/.docx files to backend/data/corpus/")
        return

    print(f"Ingesting {len(chunks)} chunks into '{settings.bundled_collection}' collection ...")
    upsert_chunks(chunks, settings.bundled_collection)
    print("Done.")


if __name__ == "__main__":
    ingest()
