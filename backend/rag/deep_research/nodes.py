import json
import litellm
from backend.config.settings import settings
from backend.rag.deep_research.tools import search_documents

DECOMPOSE_PROMPT = """You are a research assistant. Break the following question into 2-4 specific sub-questions that together would allow a thorough answer.
Return ONLY a JSON array of strings. Example: ["sub-question 1", "sub-question 2"]

Question: {question}"""

SYNTHESIZE_PROMPT = """You are a research assistant. Using the retrieved passages below, write a comprehensive answer to the main question.
Cite sources with numbered brackets [1], [2], etc. corresponding to the passage numbers.

Main question: {question}

Retrieved passages:
{passages}

Answer:"""

REFLECT_PROMPT = """You are evaluating the quality of a research answer. Rate the answer on a scale of 0.0 to 1.0 based on:
- Does it fully address the question?
- Is it well-supported by the sources?
- Are there obvious gaps?

Return ONLY a JSON object: {{"confidence": 0.85, "gaps": "brief description of gaps or empty string"}}

Question: {question}
Answer: {answer}"""

REFINE_PROMPT = """The initial answer had gaps: {gaps}
Generate ONE refined search query to find information that fills these gaps.
Return ONLY the query string, nothing else.

Original question: {question}"""


def _llm(messages: list[dict], provider: str, model: str | None, temperature: float = 0.2) -> str:
    model_string = settings.litellm_model_string(provider, model)
    response = litellm.completion(
        model=model_string,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()


def node_decompose(state: dict) -> dict:
    question = state["question"]
    provider = state["provider"]
    model = state.get("model")

    raw = _llm(
        [{"role": "user", "content": DECOMPOSE_PROMPT.format(question=question)}],
        provider,
        model,
        temperature=0.3,
    )
    try:
        sub_questions = json.loads(raw)
        if not isinstance(sub_questions, list):
            sub_questions = [question]
    except json.JSONDecodeError:
        sub_questions = [question]

    return {**state, "sub_questions": sub_questions, "steps": state.get("steps", []) + [
        {"step": "decompose", "data": sub_questions}
    ]}


def node_retrieve(state: dict) -> dict:
    sub_questions = state["sub_questions"]
    collections = state["collections"]
    all_chunks: list[dict] = []
    seen_ids: set[str] = set()
    step_data = []

    for sub_q in sub_questions:
        chunks = search_documents(sub_q, collections, top_k=4)
        new_chunks = [c for c in chunks if c["id"] not in seen_ids]
        seen_ids.update(c["id"] for c in new_chunks)
        all_chunks.extend(new_chunks)
        step_data.append({"sub_q": sub_q, "chunk_count": len(new_chunks)})

    return {**state, "retrieved_chunks": all_chunks, "steps": state["steps"] + [
        {"step": "retrieve", "data": step_data}
    ]}


def node_synthesize(state: dict) -> dict:
    question = state["question"]
    chunks = state["retrieved_chunks"]
    provider = state["provider"]
    model = state.get("model")

    passages = "\n\n".join(
        f"[{i+1}] ({c['title']}) {c['text']}" for i, c in enumerate(chunks)
    )

    answer = _llm(
        [{"role": "user", "content": SYNTHESIZE_PROMPT.format(question=question, passages=passages)}],
        provider,
        model,
    )

    return {**state, "draft_answer": answer, "steps": state["steps"] + [
        {"step": "synthesize", "data": answer[:500]}
    ]}


def node_reflect(state: dict) -> dict:
    question = state["question"]
    answer = state["draft_answer"]
    provider = state["provider"]
    model = state.get("model")

    raw = _llm(
        [{"role": "user", "content": REFLECT_PROMPT.format(question=question, answer=answer)}],
        provider,
        model,
    )
    try:
        reflection = json.loads(raw)
        confidence = float(reflection.get("confidence", 0.8))
        gaps = reflection.get("gaps", "")
    except (json.JSONDecodeError, ValueError):
        confidence = 0.8
        gaps = ""

    needs_requery = confidence < 0.7 and gaps and not state.get("requeried")

    return {**state, "confidence": confidence, "gaps": gaps, "needs_requery": needs_requery,
            "steps": state["steps"] + [
                {"step": "reflect", "data": {"confidence": confidence, "requery": needs_requery}}
            ]}


def node_requery(state: dict) -> dict:
    question = state["question"]
    gaps = state["gaps"]
    provider = state["provider"]
    model = state.get("model")
    collections = state["collections"]

    refined_query = _llm(
        [{"role": "user", "content": REFINE_PROMPT.format(gaps=gaps, question=question)}],
        provider,
        model,
    )

    extra_chunks = search_documents(refined_query, collections, top_k=4)
    seen_ids = {c["id"] for c in state["retrieved_chunks"]}
    new_chunks = [c for c in extra_chunks if c["id"] not in seen_ids]

    updated_chunks = state["retrieved_chunks"] + new_chunks

    return {**state, "retrieved_chunks": updated_chunks, "requeried": True,
            "steps": state["steps"] + [
                {"step": "requery", "data": {"query": refined_query, "new_chunks": len(new_chunks)}}
            ]}


def node_finalize(state: dict) -> dict:
    chunks = state["retrieved_chunks"]
    citations = [
        {
            "id": i + 1,
            "title": c["title"],
            "snippet": c["text"][:300] + ("..." if len(c["text"]) > 300 else ""),
            "full_text": c["text"],
            "source": c["source"],
            "score": round(c["score"], 3),
        }
        for i, c in enumerate(chunks)
    ]
    return {**state, "final_answer": state["draft_answer"], "citations": citations,
            "steps": state["steps"] + [
                {"step": "final", "data": {"answer": state["draft_answer"], "citations": citations}}
            ]}
