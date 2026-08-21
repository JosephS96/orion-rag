"""
Answer correctness + faithfulness evals, against the golden Q&A set (`golden_qa.py`).

Runs the full Simple RAG pipeline (retrieve + generate, via `run_simple_rag`) for
each golden question, then uses an LLM judge to score two independent things:

    Answer Accuracy — does the generated answer correctly convey the golden set's
                      reference answer (`expected_answer`)? Needs ground truth.
    Faithfulness    — does the generated answer only assert things supported by
                      the chunks retrieve() actually returned? Reference-free —
                      judged only against the sources the pipeline used.

These axes are independent on purpose: bad retrieval can still produce a
faithful-but-wrong answer (an accurate summary of the wrong sources), and good
retrieval can still produce an unfaithful answer if the LLM embellishes beyond
what the sources say. Collapsing them into one score would hide which stage —
retrieval or generation — needs the fix.

This eval makes real LLM calls (one generation + up to two judge calls per
question) and will incur API cost on whichever provider you point it at.
Requires the bundled corpus to already be indexed, same as retrieval_eval.py.

Usage (from the repo root):
    python -m backend.evals.answer_eval --provider anthropic
    python -m backend.evals.answer_eval --provider anthropic --judge-provider openai --limit 10
"""
import argparse
from dataclasses import dataclass

from backend.config.settings import settings
from backend.rag.simple_chain import run_simple_rag
from backend.evals.golden_qa import GOLDEN_QA, GoldenQA
from backend.evals.judge import call_llm, parse_verdict

CORRECTNESS_SYSTEM = """You are grading whether a generated answer correctly conveys a reference answer's key fact.
Respond on the first line with exactly one word: CORRECT or INCORRECT.
On the second line, give a one-sentence reason.
Minor differences in phrasing, extra detail, or citation formatting are fine — only mark INCORRECT if the key fact is wrong, missing, or contradicted."""

CORRECTNESS_USER_TEMPLATE = """Question: {question}
Reference answer (key fact that must be present): {expected_answer}
Generated answer: {generated_answer}"""

FAITHFULNESS_SYSTEM = """You are checking whether a generated answer is fully supported by the provided source passages \
(a faithfulness/groundedness check for a RAG system).
Respond on the first line with exactly one word: FAITHFUL or UNFAITHFUL.
On the second line: if UNFAITHFUL, name the specific unsupported claim(s); if FAITHFUL, write "none".
An answer that appropriately says the sources don't contain enough information is FAITHFUL. Mark UNFAITHFUL only
for claims the sources do not support — not for imperfect phrasing."""

FAITHFULNESS_USER_TEMPLATE = """Sources:
{sources_block}

Generated answer:
{generated_answer}"""


@dataclass
class AnswerResult:
    item: GoldenQA
    generated_answer: str
    correctness: str  # "CORRECT" | "INCORRECT" | "unknown"
    correctness_reason: str
    faithfulness: str  # "FAITHFUL" | "UNFAITHFUL" | "unknown"
    faithfulness_reason: str


def _sources_block(citations: list[dict]) -> str:
    return "\n\n".join(f"[{c['id']}] ({c['title']}) {c['full_text']}" for c in citations)


def evaluate_item(
    item: GoldenQA,
    provider: str,
    model: str | None,
    judge_provider: str,
    judge_model: str | None,
) -> AnswerResult:
    result = run_simple_rag(item.question, [settings.bundled_collection], provider, model)
    answer = result["answer"]
    citations = result["citations"]

    correctness_raw = call_llm(
        CORRECTNESS_SYSTEM,
        CORRECTNESS_USER_TEMPLATE.format(
            question=item.question,
            expected_answer=item.expected_answer,
            generated_answer=answer,
        ),
        judge_provider, judge_model,
    )
    correctness, correctness_reason = parse_verdict(correctness_raw, "CORRECT", "INCORRECT")

    if citations:
        faithfulness_raw = call_llm(
            FAITHFULNESS_SYSTEM,
            FAITHFULNESS_USER_TEMPLATE.format(
                sources_block=_sources_block(citations),
                generated_answer=answer,
            ),
            judge_provider, judge_model,
        )
        faithfulness, faithfulness_reason = parse_verdict(faithfulness_raw, "FAITHFUL", "UNFAITHFUL")
    else:
        faithfulness, faithfulness_reason = "unknown", "no sources were retrieved"

    return AnswerResult(
        item=item,
        generated_answer=answer,
        correctness=correctness,
        correctness_reason=correctness_reason,
        faithfulness=faithfulness,
        faithfulness_reason=faithfulness_reason,
    )


def print_report(results: list[AnswerResult]) -> None:
    print(f"{'Question':<70} {'Correct':<10} {'Faithful':<10}")
    print("-" * 92)
    for r in results:
        print(f"{r.item.question[:68]:<70} {r.correctness:<10} {r.faithfulness:<10}")

    n = len(results)
    correct = sum(1 for r in results if r.correctness == "CORRECT")
    faithful = sum(1 for r in results if r.faithfulness == "FAITHFUL")
    unknown_c = sum(1 for r in results if r.correctness == "unknown")
    unknown_f = sum(1 for r in results if r.faithfulness == "unknown")

    print(f"\n--- Summary (n={n}) ---")
    accuracy_note = f"  [{unknown_c} unparseable judge responses]" if unknown_c else ""
    faithfulness_note = f"  [{unknown_f} unparseable judge responses]" if unknown_f else ""
    print(f"Answer Accuracy: {correct}/{n} ({correct / n:.1%}){accuracy_note}")
    print(f"Faithfulness:    {faithful}/{n} ({faithful / n:.1%}){faithfulness_note}")

    incorrect = [r for r in results if r.correctness == "INCORRECT"]
    if incorrect:
        print(f"\n--- {len(incorrect)} incorrect answers ---")
        for r in incorrect:
            print(f"  Q: {r.item.question}")
            print(f"     expected: {r.item.expected_answer}")
            print(f"     got: {r.generated_answer[:200]}")
            print(f"     judge: {r.correctness_reason}")

    unfaithful = [r for r in results if r.faithfulness == "UNFAITHFUL"]
    if unfaithful:
        print(f"\n--- {len(unfaithful)} unfaithful answers ---")
        for r in unfaithful:
            print(f"  Q: {r.item.question}")
            print(f"     unsupported claim(s): {r.faithfulness_reason}")


def run(
    provider: str,
    model: str | None,
    judge_provider: str,
    judge_model: str | None,
    limit: int | None,
) -> list[AnswerResult]:
    items = GOLDEN_QA[:limit] if limit else GOLDEN_QA
    results = [
        evaluate_item(item, provider, model, judge_provider, judge_model)
        for item in items
    ]
    print_report(results)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run answer correctness + faithfulness evals against the golden Q&A set."
    )
    parser.add_argument("--provider", required=True, help="LLM provider to generate answers with (openai, anthropic, gemini, mistral)")
    parser.add_argument("--model", default=None, help="Override the default model for --provider")
    parser.add_argument("--judge-provider", default=None, help="Provider to use for judging (defaults to --provider)")
    parser.add_argument("--judge-model", default=None, help="Override the default model for --judge-provider")
    parser.add_argument("--limit", type=int, default=None, help="Only evaluate the first N golden questions (for a quick/cheap run)")
    args = parser.parse_args()

    available = settings.available_providers()
    if args.provider not in available:
        parser.error(f"Provider '{args.provider}' is not configured. Available: {list(available.keys())}")

    judge_provider = args.judge_provider or args.provider
    if judge_provider not in available:
        parser.error(f"Judge provider '{judge_provider}' is not configured. Available: {list(available.keys())}")

    run(args.provider, args.model, judge_provider, args.judge_model, args.limit)


if __name__ == "__main__":
    main()
