from fastapi import APIRouter
from backend.config.settings import settings

router = APIRouter()


@router.get("/health")
def health():
    return {
        "status": "ok",
        "providers": settings.available_providers(),
    }
