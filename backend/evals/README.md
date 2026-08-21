# Evals

This directory holds Orion RAG's evaluation suite — automated checks that measure
pipeline quality against a fixed, hand-labeled dataset, so changes to chunking,
embeddings, or retrieval can be judged by numbers instead of vibes.

Currently implemented:

| Eval | File | What it measures |
|---|---|---|
| Retrieval quality | `retrieval_eval.py` | Does `retrieve()` surface the right source document for a known question, and how highly does it rank it? |
| Answer correctness & faithfulness | `answer_eval.py` | Does the full pipeline's generated answer state the right fact, and does it only assert things the retrieved sources actually support? |

The golden question set both evals draw from lives in `golden_qa.py`. The
LLM-judge helper shared by the answer-quality checks lives in `judge.py`.

---

## Golden Q&A set (`golden_qa.py`)

A hand-written set of 45 questions over the bundled space-exploration corpus
(`backend/data/corpus/`) — 3 per document, covering all 15 bundled files. Each
entry is a `GoldenQA`:

```python
GoldenQA(
    question="What was the name of the lunar module that Apollo 11 used to land on the Moon?",
    expected_source="apollo_11.txt",   # which corpus file contains the answer
    expected_answer="Eagle",           # short reference answer, for future answer-quality evals
    confusable=True,                  # see below
)
```

- **`expected_source`** is the ground truth the retrieval eval checks against — it
  must match `RetrievedChunk.source`, i.e. the corpus filename.
- **`expected_answer`** isn't used by the retrieval eval — it's the reference
  fact `answer_eval.py` checks generated answers against, so both evals share
  one labeled dataset instead of needing two.
- **`confusable`** flags ~a dozen questions written to be hard on purpose — they
  ask about a document that shares topic or entities with a sibling document
  (Apollo 11 vs. Apollo 13 vs. the Apollo program; Hubble vs. JWST; NASA's
  overview page vs. the mission-specific pages it summarizes). A retriever that's
  leaning on generic keyword overlap rather than real semantic matching is far
  more likely to return the wrong source on these than on the rest of the set, so
  they're reported as a separate breakdown rather than averaged away.

When the corpus changes (new bundled document added or removed), update this
file to match — add 2-3 questions for a new document, remove entries for a
deleted one.

---

## Retrieval eval (`retrieval_eval.py`)

Runs the same `retrieve()` function the app uses (against the `bundled`
ChromaDB collection) for every question in the golden set, and checks whether —
and how highly — a chunk from the expected source document comes back.

### Metrics

**Hit Rate@k** — the fraction of questions where the expected source document
appears *somewhere* in the top-k retrieved chunks.

```
Hit Rate@k = (# questions where expected source is in the top k results) / (total questions)
```

Reported at k = 1, 3, and 5. Hit Rate@1 is the strictest — it only counts a
question as a "hit" if the correct source came back *first*. Hit Rate@5 is more
forgiving: since the LLM generation step sees all 5 retrieved chunks (the
default `retrieval_top_k`), a source that shows up anywhere in that set still
has a chance to inform the answer. A large gap between Hit Rate@1 and Hit
Rate@5 means the right chunk is usually in the context window, but not ranked
first — worth knowing since generation quality tends to degrade as relevant
context gets buried lower in the prompt.

**MRR (Mean Reciprocal Rank)** — the average of `1 / rank` across all
questions, where `rank` is the position of the first chunk from the expected
source (and the term is `0` if it never appears in the retrieved set).

```
MRR = (1/n) * sum(1 / rank_i)   for each question i, where rank_i = 0 if never found
```

Unlike Hit Rate, MRR is sensitive to *where* in the ranking the right answer
lands, not just whether it cleared the cutoff — a retriever that always ranks
the correct source #1 scores 1.0; always #2 scores 0.5; a retriever that misses
entirely scores 0 for that question. It's a single number to track for
regressions over time (e.g. after changing the embedding model or chunk size),
where Hit Rate@k alone might not move if the correct chunk just shuffles
between rank 2 and rank 3.

### Running it

Requires the bundled corpus to already be indexed (this happens automatically
on backend startup, or run `python -m backend.scripts.ingest_corpus`).

```bash
# from the repo root
python -m backend.evals.retrieval_eval
```

### Reading the output

Illustrative example (actual numbers depend on the embedding model and corpus
at the time you run it):

```
Question                                                    Expected source        Rank
--------------------------------------------------------------------------------------
What was the name of the lunar module that Apollo 11...     apollo_11.txt          1     *
...

--- Summary (n=45) ---
Hit Rate@1: 84.4%
Hit Rate@3: 95.6%
Hit Rate@5: 97.8%
MRR: 0.891

--- Confusable subset (n=12, marked with *) ---
Hit Rate@1: 75.0%
Hit Rate@3: 91.7%
Hit Rate@5: 100.0%
MRR: 0.826

--- 1 complete misses (expected source never retrieved in top 5) ---
  Q: ...
     expected: some_doc.txt | got: [...]
```

- Per-question rows marked `*` are the confusable subset; `miss` means the
  expected source never appeared in the top 5 retrieved chunks at all.
- The confusable subset's metrics are broken out separately from the overall
  numbers precisely so a strong overall score can't hide a retriever that's
  weak on the harder, topically-overlapping questions.
- The "complete misses" section is the most actionable output when a change
  regresses retrieval — it shows exactly which document never got its due and
  what has been drowning it out instead.

There's no fixed pass/fail threshold enforced yet — read the summary numbers
and the misses list, and use your judgment on whether a change made retrieval
better or worse. A CI gate with fixed thresholds is a natural next step (see
Roadmap).

---

## Answer correctness & faithfulness eval (`answer_eval.py`)

Runs the full Simple RAG pipeline (`run_simple_rag` — retrieve *and* generate)
for every golden question, then uses an LLM judge to score two independent
things about the generated answer:

**Answer Accuracy** — does the generated answer correctly convey
`expected_answer`'s key fact? This needs ground truth, so it's checked against
the golden set's reference answer.

**Faithfulness** — does the generated answer only assert things the retrieved
chunks actually support? This is reference-free: it's judged only against the
sources `retrieve()` returned for that question, not against
`expected_answer`. An answer can be faithful and still wrong (an accurate
summary of chunks retrieval got wrong), and it can be unfaithful despite
perfect retrieval (the LLM embellishes past what the sources say). Keeping
these as two separate scores, instead of one blended "quality" number, is
what tells you whether a bad result traces back to retrieval or to
generation.

Both are scored by a second LLM call (an "LLM-as-judge"): the judge is given
the question, the reference answer or the sources, and the generated answer,
and asked to respond with a one-word verdict (`CORRECT`/`INCORRECT` or
`FAITHFUL`/`UNFAITHFUL`) plus a one-line rationale. `judge.py` parses that
verdict with word-boundary matching rather than a plain substring check —
`INCORRECT` contains `CORRECT` as a substring, so a naive check would
misclassify a compliant negative response as positive. A judge response that
doesn't follow the one-word-first-line format at all is reported as
`unknown` rather than silently guessed at.

### Running it

Makes real LLM calls — one generation plus up to two judge calls per
question — so it costs API credits and needs a configured provider (see
`backend/config/settings.py` / `.env`). Requires the bundled corpus to already
be indexed, same as `retrieval_eval.py`.

```bash
# from the repo root
python -m backend.evals.answer_eval --provider anthropic

# use a different (ideally stronger, or at least different) model to judge
# than the one being evaluated, to reduce self-preference bias
python -m backend.evals.answer_eval --provider anthropic --judge-provider openai

# quick/cheap smoke run over just the first N questions
python -m backend.evals.answer_eval --provider anthropic --limit 10
```

### Reading the output

Illustrative example:

```
Question                                                              Correct    Faithful
--------------------------------------------------------------------------------------------
What was the name of the lunar module that Apollo 11 used to land...  CORRECT    FAITHFUL
...

--- Summary (n=45) ---
Answer Accuracy: 41/45 (91.1%)
Faithfulness:    43/45 (95.6%)

--- 4 incorrect answers ---
  Q: ...
     expected: Eagle
     got: The lunar module was named Columbia...
     judge: Names the command module, not the lunar module.

--- 2 unfaithful answers ---
  Q: ...
     unsupported claim(s): States the mission launched in 1979; sources say 1977.
```

As with retrieval, there's no enforced pass/fail threshold — read the
incorrect/unfaithful breakdowns, since they name the specific claim that was
wrong or unsupported, which is far more actionable than the summary
percentage alone.

---

## Roadmap

Not yet implemented, but designed for using this same golden set:

- **Deep Research evals** — decomposition quality, and whether the reflect
  step's confidence score actually correlates with answer correctness.
- **CI integration** — run the retrieval eval (cheap, no LLM cost) on every
  PR with a minimum Hit Rate@5 / MRR threshold; run the answer-quality eval
  less frequently given its API cost, e.g. nightly or pre-release.
