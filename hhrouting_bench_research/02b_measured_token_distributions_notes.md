# 02b — Measured Token Distributions (real payloads, tokenized)

**Why this exists:** Agent B's `02_workload_decomposition.csv` carries token *ranges* that are
mostly **estimates** from task schema. For routing decisions (prefill pressure, KV sizing, SLO
classes) we need **measured** input/output token distributions from the *actual* task payloads —
the full prompt as it would be sent to the model. This file provides them.

## Method
- **Tokenizer:** `tiktoken` `cl100k_base` (GPT-3.5/4 family). A reference tokenizer; counts shift
  ±10-20% for Llama/Qwen SentencePiece tokenizers, but percentile *shape* is stable. Labeled per row.
- **Input text** = the full payload sent to the model for that task (e.g. LongBench = `context`+`input`;
  SWE-bench = `problem_statement`; summarization = the full `article`/`report`/`document`).
- **Output text** = the reference completion/answer/patch/summary where present (a proxy for decode length).
- **Samples:** first N records per split (N=100-400). These are DISTRIBUTION ESTIMATES from a sample,
  not the full corpus — but measured from real data, not guessed from schema.
- **Public, ungated only.** GAIA is gated (needs HF auth) — not measured here.

## Measured distributions (cl100k_base tokens)

| dataset | n | input P50 | input P99 | input max | output P50 | output P99 |
|---|--:|--:|--:|--:|--:|--:|
| GSM8K | 400 | 54 | 123 | 132 | 91 | 222 |
| GovReport-sum | 100 | 8656 | 21751 | 22192 | 706 | 1411 |
| HotpotQA | 300 | 20 | 43 | 52 | 3 | 11 |
| HumanEval | 164 | 117 | 311 | 391 | 46 | 157 |
| LongBench-2wikimqa | 150 | 6334 | 15750 | 16142 | 6 | 14 |
| LongBench-gov_report | 120 | 8740 | 42706 | 51394 | 723 | 1406 |
| LongBench-hotpotqa | 150 | 14399 | 16341 | 16347 | 5 | 20 |
| LongBench-multifieldqa_en | 150 | 7006 | 14182 | 14962 | 15 | 53 |
| LongBench-narrativeqa | 150 | 31324 | 65288 | 65293 | 6 | 22 |
| LongBench-qasper | 150 | 4509 | 18445 | 21129 | 26 | 312 |
| MATH-500 | 400 | 49 | 343 | 756 | 150 | 818 |
| MBPP | 400 | 16 | 37 | 47 | 46 | 197 |
| MuSiQue | 300 | 15 | 27 | 31 | 4 | 16 |
| MultiNews | 150 | 1611 | 18702 | 35752 | 274 | 403 |
| NarrativeQA | 200 | 44 | 102 | 115 | 49 | 129 |
| PubMed-sum | 120 | 3598 | 12778 | 12943 | 251 | 528 |
| RAGBench-hotpotqa | 200 | 19 | 42 | 44 | 25 | 58 |
| RepoBench-py | 200 | 262 | 1085 | 1157 | 12 | 38 |
| SWE-bench-Lite | 300 | 264 | 2301 | 6939 | 206 | 886 |
| SWE-bench-Verified | 200 | 268 | 2164 | 2407 | 220 | 2275 |
| TriviaQA-rc | 300 | 14 | 25 | 26 | 166 | 1026 |
| arXiv-sum | 120 | 6516 | 21108 | 26625 | 182 | 409 |

## Key observations for routing
- **Extreme-prefill long-context** (true high TTFT pressure): LongBench-narrativeqa P50≈31K/max≈65K,
  GovReport P50≈8.7K/max≈51K, arXiv P50≈6.5K/max≈27K, LongBench-2wikimqa/hotpotqa ≈6-14K. These are
  the prefill-bound, decode-light workloads (huge input, short output).
- **Decode-heavy / balanced:** GSM8K, MATH-500 (output P99 up to 343), HumanEval — short input, real
  generation. MATH output tail (P99=343) shows reasoning-length variance.
- **Tiny-input batch QA:** HotpotQA/TriviaQA/MuSiQue/RAGBench questions are <50 tokens *without* context
  — confirming these are payload-only and need context-grafting to stress prefill (matches Agent D).
- **SWE coding:** SWE-bench-Verified input P50=268/P99=2164 (problem_statement ONLY; the full repo
  context that an agent actually sends is far larger — this is the floor, not the agent-loop input).
- **RepoBench:** P50=262/max=1157 — the cross-file code-completion input (cropped to model window).

## Measured vs Agent-B estimate (spot check)
| benchmark | Agent B estimate (input) | MEASURED (input P50 / P99) |
|---|---|---|
| GSM8K | 50-200 | 54 / 123 |
| HumanEval | ~150-300 est | 117 / 311 |
| LongBench (narrativeqa) | 5000-30000 (card) | 31324 / 65288 |
| SWE-bench Verified | 2000-30000 (repo+issue) | 268 / 2164 (problem_statement only) |
| arXiv summarization | high est | 6516 / 21108 |

**Caveat:** measured input depends on WHICH fields are sent. Agent benchmarks (SWE-bench, RepoBench)
send far more at inference time (retrieved files, repo context, agent scratchpad) than the bare task
field measured here — so those rows are LOWER BOUNDS. Single-shot benchmarks (GSM8K, LongBench,
summarization) are measured on the true full prompt and are accurate.