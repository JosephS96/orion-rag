import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
from backend.config.settings import settings
from backend.rag.deep_research.graph import get_graph

router = APIRouter()


class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    provider: str
    model: Optional[str] = None
    collections: list[str] = ["bundled"]


def _sse(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


@router.post("/research")
def research(req: ResearchRequest):
    available = settings.available_providers()
    if req.provider not in available:
        raise HTTPException(
            status_code=400,
            detail=f"Provider '{req.provider}' is not configured. Available: {list(available.keys())}",
        )

    def stream():
        graph = get_graph()
        initial_state = {
            "question": req.query,
            "provider": req.provider,
            "model": req.model,
            "collections": req.collections,
            "sub_questions": [],
            "retrieved_chunks": [],
            "draft_answer": "",
            "confidence": 0.0,
            "gaps": "",
            "needs_requery": False,
            "requeried": False,
            "final_answer": "",
            "citations": [],
            "steps": [],
        }

        last_step_count = 0
        for state in graph.stream(initial_state):
            # state is a dict of {node_name: updated_state}
            for node_name, node_state in state.items():
                steps = node_state.get("steps", [])
                new_steps = steps[last_step_count:]
                last_step_count = len(steps)
                for step in new_steps:
                    yield _sse(step)

    return StreamingResponse(stream(), media_type="text/event-stream")
