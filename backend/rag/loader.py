import os
from pathlib import Path
from dataclasses import dataclass
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.config.settings import settings


@dataclass
class ParsedChunk:
    text: str
    source: str      # filename relative to corpus root
    title: str       # derived from filename
    chunk_index: int


def _text_from_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _text_from_pdf(path: Path) -> str:
    import pypdf
    reader = pypdf.PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _text_from_docx(path: Path) -> str:
    import docx
    doc = docx.Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs)


def _text_from_md(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


_PARSERS = {
    ".txt": _text_from_txt,
    ".pdf": _text_from_pdf,
    ".docx": _text_from_docx,
    ".md": _text_from_md,
}


def load_and_chunk(path: Path, source_root: Path | None = None) -> list[ParsedChunk]:
    suffix = path.suffix.lower()
    parser = _PARSERS.get(suffix)
    if parser is None:
        return []

    raw_text = parser(path)
    if not raw_text.strip():
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    chunks = splitter.split_text(raw_text)

    rel_source = str(path.relative_to(source_root)) if source_root else path.name
    title = path.stem.replace("_", " ").replace("-", " ").title()

    return [
        ParsedChunk(
            text=chunk,
            source=rel_source,
            title=title,
            chunk_index=i,
        )
        for i, chunk in enumerate(chunks)
    ]


def load_directory(directory: Path) -> list[ParsedChunk]:
    """Recursively load and chunk all supported files in a directory."""
    all_chunks: list[ParsedChunk] = []
    for ext in _PARSERS:
        for file_path in sorted(directory.rglob(f"*{ext}")):
            all_chunks.extend(load_and_chunk(file_path, source_root=directory))
    return all_chunks
