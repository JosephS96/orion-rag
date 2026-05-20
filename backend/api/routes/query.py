from fastapi import APIRouter, HTTPException
from backend.api.models.query import QueryRequest, QueryResponse
from backend.config.settings import settings
from backend.rag.simple_chain import run_simple_rag

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    available = settings.available_providers()
    if req.provider not in available:
        raise HTTPException(
            status_code=400,
            detail=f"Provider '{req.provider}' is not configured. Available: {list(available.keys())}",
        )

    result = run_simple_rag(
        query=req.query,
        collection_names=req.collections,
        provider=req.provider,
        model=req.model,
    )
    return QueryResponse(**result)
