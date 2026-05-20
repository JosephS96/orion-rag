from pydantic import BaseModel
from datetime import datetime


class DocumentMetadata(BaseModel):
    id: str
    filename: str
    title: str
    chunk_count: int
    uploaded_at: datetime
    size_bytes: int
