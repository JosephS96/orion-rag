"""Small LLM-as-judge helper shared by the answer-quality evals."""
import re
import litellm
from backend.config.settings import settings


def call_llm(system: str, user: str, provider: str, model: str | None = None, temperature: float = 0.0) -> str:
    model_string = settings.litellm_model_string(provider, model)
    response = litellm.completion(
        model=model_string,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()


def parse_verdict(raw: str, positive: str, negative: str) -> tuple[str, str]:
    """Parses a judge response whose first line is a one-word verdict and whose
    remaining lines are the rationale. Returns (verdict, rationale), where verdict
    is `positive`, `negative`, or "unknown" if the response didn't follow the format.

    Uses word-boundary matching rather than plain substring checks: `negative` is
    often `positive` with a prefix (INCORRECT contains CORRECT, UNFAITHFUL contains
    FAITHFUL), so a naive substring check would misread a compliant negative
    response as positive.
    """
    lines = raw.strip().splitlines()
    first = lines[0].strip().upper() if lines else ""
    rationale = " ".join(line.strip() for line in lines[1:]).strip()

    has_positive = re.search(rf"\b{re.escape(positive.upper())}\b", first) is not None
    has_negative = re.search(rf"\b{re.escape(negative.upper())}\b", first) is not None

    if has_positive and not has_negative:
        return positive, rationale
    if has_negative:
        return negative, rationale
    return "unknown", raw
