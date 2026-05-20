import litellm
from backend.config.settings import settings
from backend.rag.retriever import retrieve, RetrievedChunk

SYSTEM_PROMPT = """You are a helpful research assistant. Answer the user's question using only the provided source passages.
Be concise and factual. For each claim, cite the source number in brackets like [1], [2].
If the passages don't contain enough information to answer, say so clearly."""

USER_PROMPT_TEMPLATE = """Sources:
{sources}

Question: {question}

Answer:"""


def _build_sources_block(chunks: list[RetrievedChunk]) -> str:
    lines = []
    for i, chunk in enumerate(chunks, 1):
        lines.append(f"[{i}] ({chunk.title}) {chunk.text}")
    return "\n\n".join(lines)


def run_simple_rag(
    query: str,
    collection_names: list[str],
    provider: str,
    model: str | None = None,
) -> dict:
    chunks = retrieve(query, collection_names)
    if not chunks:
        return {"answer": "No relevant documents found for your query.", "citations": []}

    sources_block = _build_sources_block(chunks)
    user_message = USER_PROMPT_TEMPLATE.format(sources=sources_block, question=query)

    model_string = settings.litellm_model_string(provider, model)
    response = litellm.completion(
        model=model_string,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,
    )

    answer = response.choices[0].message.content

    citations = [
        {
            "id": i,
            "title": chunk.title,
            "snippet": chunk.text[:300] + ("..." if len(chunk.text) > 300 else ""),
            "full_text": chunk.text,
            "source": chunk.source,
            "score": round(chunk.score, 3),
        }
        for i, chunk in enumerate(chunks, 1)
    ]

    return {"answer": answer, "citations": citations}
