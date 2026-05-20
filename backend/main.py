from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pathlib import Path

from backend.config.settings import settings
from backend.rag.vectorstore import collection_is_empty
from backend.rag.loader import load_directory
from backend.rag.vectorstore import upsert_chunks
from backend.api.routes import health, query, documents, research

CORPUS_DIR = Path(__file__).parent / "data" / "corpus"


@asynccontextmanager
async def lifespan(app: FastAPI):
    if collection_is_empty(settings.bundled_collection):
        print("Indexing bundled corpus...")
        chunks = load_directory(CORPUS_DIR)
        upsert_chunks(chunks, settings.bundled_collection)
        print(f"Indexed {len(chunks)} chunks into '{settings.bundled_collection}'.")
    yield


app = FastAPI(title="Orion RAG API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(query.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(research.router, prefix="/api")
