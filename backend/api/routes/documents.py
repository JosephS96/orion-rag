import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.api.models.document import DocumentMetadata
from backend.config.settings import settings
from backend.rag.loader import load_and_chunk
from backend.rag.vectorstore import upsert_chunks, delete_by_source, list_sources

router = APIRouter()

UPLOAD_DIR = Path("./data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
METADATA_FILE = UPLOAD_DIR / "metadata.json"

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md", ".docx"}


def _load_metadata() -> dict:
    if METADATA_FILE.exists():
        return json.loads(METADATA_FILE.read_text())
    return {}


def _save_metadata(meta: dict) -> None:
    METADATA_FILE.write_text(json.dumps(meta, indent=2, default=str))


@router.post("/documents", response_model=DocumentMetadata)
async def upload_document(file: UploadFile = File(...)):
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {suffix}")

    content = await file.read()
    doc_id = hashlib.sha256(content).hexdigest()[:16]
    save_path = UPLOAD_DIR / f"{doc_id}{suffix}"
    save_path.write_bytes(content)

    chunks = load_and_chunk(save_path, source_root=UPLOAD_DIR)
    if not chunks:
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail="Could not extract text from this file.")

    upsert_chunks(chunks, settings.user_collection)

    meta_entry = DocumentMetadata(
        id=doc_id,
        filename=file.filename,
        title=chunks[0].title,
        chunk_count=len(chunks),
        uploaded_at=datetime.now(timezone.utc),
        size_bytes=len(content),
    )

    all_meta = _load_metadata()
    all_meta[doc_id] = meta_entry.model_dump()
    _save_metadata(all_meta)

    return meta_entry


@router.get("/documents", response_model=list[DocumentMetadata])
def list_documents():
    return [DocumentMetadata(**v) for v in _load_metadata().values()]


@router.delete("/documents/{doc_id}", status_code=204)
def delete_document(doc_id: str):
    all_meta = _load_metadata()
    if doc_id not in all_meta:
        raise HTTPException(status_code=404, detail="Document not found.")

    entry = all_meta.pop(doc_id)
    _save_metadata(all_meta)

    # Remove file from disk
    for ext in ALLOWED_EXTENSIONS:
        path = UPLOAD_DIR / f"{doc_id}{ext}"
        path.unlink(missing_ok=True)

    # Remove chunks from vectorstore (source key is relative to UPLOAD_DIR)
    delete_by_source(f"{doc_id}{Path(entry['filename']).suffix.lower()}", settings.user_collection)
