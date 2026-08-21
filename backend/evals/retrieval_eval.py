"""
Retrieval eval: Hit Rate@k and MRR against the golden Q&A set (`golden_qa.py`).

For each (question, expected_source) pair, runs the same `retrieve()` used by
the app against the 'bundled' collection and checks whether — and how highly —
a chunk from the expected source document was returned.

    Hit Rate@k — fraction of questions where the expected source appears
                 somewhere in the top-k retrieved chunks.
    MRR        — mean reciprocal rank of the first chunk from the expected
                 source (0 if it never appears in the retrieved set).

Requires the bundled corpus to already be indexed (run the backend once, or
`python -m backend.scripts.ingest_corpus`, from the repo root).

Usage (from the repo root):
    python -m backend.evals.retrieval_eval
"""
from dataclasses import dataclass

from backend.config.settings import settings
from backend.rag.retriever import retrieve
from backend.evals.golden_qa import GOLDEN_QA, GoldenQA

K_CUTOFFS = [1, 3, 5]
MAX_K = max(K_CUTOFFS)


@dataclass
class QueryResult:
    item: GoldenQA
    retrieved_sources: list[str]
    rank: int | None  # 1-indexed rank of first chunk from expected_source, None if absent


def evaluate_query(item: GoldenQA) -> QueryResult:
    chunks = retrieve(item.question, [settings.bundled_collection], top_k=MAX_K)
    retrieved_sources = [c.source for c in chunks]
    rank = next(
        (i + 1 for i, source in enumerate(retrieved_sources) if source == item.expected_source),
        None,
    )
    return QueryResult(item=item, retrieved_sources=retrieved_sources, rank=rank)


def hit_rate_at_k(results: list[QueryResult], k: int) -> float:
    hits = sum(1 for r in results if r.rank is not None and r.rank <= k)
    return hits / len(results)


def mrr(results: list[QueryResult]) -> float:
    return sum(1 / r.rank for r in results if r.rank is not None) / len(results)


def print_report(results: list[QueryResult]) -> None:
    print(f"{'Question':<75} {'Expected source':<32} {'Rank':<6}")
    print("-" * 115)
    for r in results:
        rank_str = str(r.rank) if r.rank is not None else "miss"
        flag = " *" if r.item.confusable else ""
        print(f"{r.item.question[:73]:<75} {r.item.expected_source:<32} {rank_str:<6}{flag}")

    print("\n--- Summary (n={}) ---".format(len(results)))
    for k in K_CUTOFFS:
        print(f"Hit Rate@{k}: {hit_rate_at_k(results, k):.1%}")
    print(f"MRR: {mrr(results):.3f}")

    confusable = [r for r in results if r.item.confusable]
    if confusable:
        print(f"\n--- Confusable subset (n={len(confusable)}, marked with *) ---")
        for k in K_CUTOFFS:
            print(f"Hit Rate@{k}: {hit_rate_at_k(confusable, k):.1%}")
        print(f"MRR: {mrr(confusable):.3f}")

    misses = [r for r in results if r.rank is None]
    if misses:
        print(f"\n--- {len(misses)} complete misses (expected source never retrieved in top {MAX_K}) ---")
        for r in misses:
            print(f"  Q: {r.item.question}")
            print(f"     expected: {r.item.expected_source} | got: {r.retrieved_sources}")


def run() -> list[QueryResult]:
    results = [evaluate_query(item) for item in GOLDEN_QA]
    print_report(results)
    return results


if __name__ == "__main__":
    run()
