# Agent B — Workload Decomposition Notes

Scope: SERVING-ROUTING only. No claims about model accuracy. This file documents,
per dimension, which values in `02_workload_decomposition.csv` are MEASURED from
data/schema and which are ESTIMATED from task shape, plus the estimation method
and source URL(s).

Token-count convention: where token counts are needed but only character or
whitespace-token counts are available, we use the standard `ceil(chars/4)`
heuristic (same as Agent C's `03_sample_payloads.jsonl`). Whitespace-token counts
are labeled "ws-tok" and are roughly 0.75x the BPE token count for English text;
they are reported as-is from the source. Every numeric range labeled MEASURED is
copied from the cited source; ranges labeled ESTIMATE are reasoned from task
schema and example payloads.

---

## Per-dimension methodology

### `input_token_range` / `output_token_range`
- **MEASURED** when a dataset card, paper abstract, or repo README states an
  explicit length distribution (count of words/tokens) or when a sample row
  exposes the raw payload text/field.
- **ESTIMATE** when the value is inferred from task shape (e.g. "function
  completion → ~50-500 output tokens"), from sample payloads (`03_sample_payloads.jsonl`),
  or from agentic-loop step counts.
- For production traces (Azure, BurstGPT, Mooncake): "varies-MEASURED" means the
  trace ships per-request integer counts (`ContextTokens` / `Request tokens` /
  `input_length`) so the *distribution* is in the data; we did not compute a
  numeric range in this run because the CSVs are not bundled in this repo.

Per-benchmark sources for MEASURED entries:
- **HumanEval input**: 50-300 tok ESTIMATE from JSONL prompts in
  https://github.com/openai/human-eval/tree/master/data
- **MBPP input**: 30-200 tok from short NL prompt field (HF card features
  list `text` <200 chars typical) — https://huggingface.co/datasets/google-research-datasets/mbpp
- **LongBench**: avg 5k-15k words; LSHT subtask up to 22,337 words — stated on
  https://huggingface.co/datasets/THUDM/LongBench (used as MEASURED-from-card)
- **LongBench v2**: 8k-2M words context, MCQ answer = 1 letter — stated on
  https://huggingface.co/datasets/THUDM/LongBench-v2 and
  https://arxiv.org/abs/2412.15204 (used as MEASURED)
- **L-Eval**: 3k-200k tokens per input, 71.6k-116k chars — stated on
  https://github.com/OpenLMLab/LEval / https://huggingface.co/datasets/L4NLP/LEval
- **NarrativeQA**: word_count e.g. 41,000 per example — stated on
  https://huggingface.co/datasets/deepmind/narrativeqa
- **arXiv summarization**: avg article ~6038 ws-tokens / abstract ~299 ws-tokens
  — stated on https://huggingface.co/datasets/ccdv/arxiv-summarization
- **PubMed summarization**: avg article ~3043 / abstract ~215 ws-tokens — stated
  on https://huggingface.co/datasets/ccdv/pubmed-summarization
- **RAGBench `response` field**: MEASURED via sample rows
  (`03_sample_payloads.jsonl` rows 9-10, covidqa_train_358 / _457 — output_tokens_estimate 29 / 23)
- **AppWorld `num_api_calls`**: 30 (sample 83a7951_2) and 101 (sample 692c77d_2)
  per `03_sample_payloads.jsonl` rows 13-14 — these are MEASURED tool-call
  cardinalities, source HF mirror https://huggingface.co/datasets/LukaszTP/AppWorld-Tasks
- **Production traces (Azure 2023/2024, BurstGPT, Mooncake)**: every per-request
  field is MEASURED in the trace — see `01b_production_traces.md` for column lists.
- All other token ranges in the CSV are ESTIMATE, derived as follows:

| Estimation method | Where applied |
|---|---|
| `ceil(chars/4)` on sample text in `03_sample_payloads.jsonl` | LMSYS-Chat-1M, WildChat-1M, ShareGPT, OpenAssistant, SWE-bench, ToolBench, tau-bench, AppWorld, WebArena, GAIA |
| Reasoned from agentic harness step count (input grows monotonically per turn ~1-8k DOM/AX-tree obs; output ~click/type/edit action) | WebArena, VisualWebArena, OSWorld, WorkArena, Terminal-Bench, AgentBench |
| Reasoned from competitive-programming statement shape (problem statement 500-3000 tok, generated solution 100-1500 tok) | LiveCodeBench |
| Reasoned from MCQ shape (short stem + short letter answer) | MMLU, MMLU-Pro, GPQA, BBH |
| Reasoned from CoT decode (short prompt, 100-1500 tok step-by-step solution) | GSM8K, MATH, MMLU-Pro |
| Reasoned from multi-passage RAG shape (Q + N passages, short extractive answer) | HotpotQA, MuSiQue, 2WikiMultihopQA, TriviaQA |
| Reasoned from full-document QA shape (Wikipedia page / paper / book + short answer) | Natural Questions, Qasper, NarrativeQA |
| Reasoned from long-doc summarization shape (long input, multi-paragraph summary) | GovReport, MultiNews, BookSum |
| Reasoned from heterogeneous orchestration | HELM, EleutherAI lm-evaluation-harness, Big-Bench |

### `io_ratio`
Derived directly from the (estimated or measured) input/output ranges. For
"varies-MEASURED" production traces, the actual ratio distribution lives in the
shipped CSV — see Agent A's `01_benchmark_validation_table.csv` row + Agent G's
`01b_production_traces.md` for the field schema.

### `prefill_pressure`
ESTIMATED per-row from the input range:
- low: typical input < ~512 tok
- medium: typical input ~512-4k tok
- high: typical input ~4k-32k tok
- extreme: typical input > 32k tok

### `decode_residency`
ESTIMATED per-row from the output range:
- low: output < ~128 tok
- medium: output ~128-1k tok
- high: output ~1k-4k tok
- extreme: output > 4k tok

### `kv_lifetime`
- short: single-shot request, KV freeable after final token
- medium: short multi-turn chat (a few turns), KV reused across turns minutes-scale
- long: agentic loop or multi-step harness (many steps in one task), KV reused for the entire task
- session-persistent: explicit session ID in the trace (BurstGPT) or per-IP
  conversation grouping (WildChat-1M); KV reuse spans hours-days

Sources for `session-persistent`:
- WildChat-1M: `conversation_hash`, per-turn `timestamp`, `hashed_ip` per
  https://huggingface.co/datasets/allenai/WildChat-1M (Agent C row).
- BurstGPT: `Session ID` field per https://github.com/HPMLL/BurstGPT (Agent A,
  Agent G #2).

### `multi_turn_growth`
- none: dataset shape is single-request (single-shot eval, summarization, RAG QA)
- small: turn-bounded chat with low typical turn count (e.g. MiniWoB++)
- large: multi-turn chat (LMSYS, WildChat, OpenAssistant) OR agentic harness
  (SWE-bench, ToolBench, WebArena, etc.) producing many monotonic-growth turns

### `tool_call_frequency`
- none: text-only benchmark (chat, QA, summarization, MCQ, single-shot coding)
- low: occasional tool use (DevEval)
- medium: per-task tool actions (MiniWoB++)
- high: extensive tool/API loops (ToolBench, AppWorld 30-100+ calls MEASURED,
  WebArena, OSWorld, AgentBench, tau-bench, GAIA-agent-harness, SWE-bench-agent)

### `prefix_reuse_potential`
- none: each request fully independent (HumanEval, MBPP)
- low: occasional incidental reuse (single-shot eval benchmarks)
- medium: shared prefix across rows by structure (RepoBench shares repo, Qasper
  shares paper across questions, BBH shares CoT exemplar) OR multi-passage RAG
  with overlapping documents
- high: deliberate multi-turn or session reuse (WildChat conversation_hash,
  BurstGPT Session ID); explicit prefix-cache hashes (Mooncake, ~50% hit ratio)

The Mooncake trace is the ONLY public catalog entry with explicit per-request
prefix-cache hash ids (`hash_ids` array). All other "high" values are inferred
from session/conversation structure.

### `arrival_pattern`
- interactive: real human users posting requests (LMSYS, WildChat, tau-bench
  via user-sim)
- steady: continuous production traffic without strong burstiness (Mooncake
  inferred from prod-serving nature, not separately quantified)
- bursty: production trace with KDD25/HPCA25-class burstiness analysis
  (BurstGPT, Azure traces)
- batch: offline eval, all requests fired together at start (most eval benchmarks)
- batch (synthesized): synthetic arrival process required because dataset has
  no timestamps (ShareGPT)
- batch (orchestrated): scenario-set scheduler (HELM)
- batch (synthetic, no arrivals): synthetic corpus with no real timestamps
  (UltraChat)
- phase-shift / synchronized: not explicitly assigned in this catalog; reserved
  for traces that exhibit distinct workload regimes (e.g., BurstGPT 110-day span
  contains diurnal phase-shifts but we did not measure them)

### `concurrency_pattern`
- low: per-request memory or VM-bound (LongBench v2 2M-word context, OSWorld
  per-VM, Natural Questions full Wikipedia page, BookSum)
- medium: typical batch-eval default
- high: small request size enables many in-flight (MMLU, HumanEval,
  WildChat-style chat)
- batch-synchronized: eval harness launches all at once with bounded parallel
  workers (HELM, SWE-bench harness, EleutherAI lm-eval-harness)

### `slo_sensitivity`
- strict-TTFT: interactive chat, RAG QA where users wait for first token (LMSYS,
  WildChat, Azure prod, BurstGPT, RAGBench, LongBench, IDE-like RepoBench)
- strict-TPOT: streaming long-output (chat with long completion, long-doc
  summarization where users read as it generates: arXiv/PubMed/GovReport)
- relaxed: long-horizon agentic background runs (SWE-bench, ToolBench,
  AppWorld, OSWorld)
- background: offline batch eval (MMLU, MBPP, HumanEval, GSM8K, Big-Bench,
  lm-eval-harness)

Assignment is from task UX, not measured. Where the harness exposes both an
interactive and a batch mode (e.g. WebArena), we picked the dominant mode.

### `likely_router_failure_mode`
ESTIMATED from joining (input/output size) × (concurrency_pattern) × (kv_lifetime):
- `head-of-line-blocking`: bursty + interactive + variable input size
- `prefill-starvation-of-decode`: high prefill_pressure + medium/long decode
- `decode-backlog-overload`: high concurrency + medium decode (batch eval CoT)
- `kv-cache-pressure`: long kv_lifetime + medium/high input
- `prefix-cache-miss-penalty`: high prefix_reuse_potential but no router awareness
- `session-affinity-failure`: session-persistent kv_lifetime or large
  multi_turn_growth without sticky routing
- `OOM`: extreme prefill_pressure individual requests
- `tail-latency-explosion`: bursty arrivals with very-long-tail input
- `unfair-tenant-starvation`: heterogeneous tenants (HELM, WorkArena)
- `cancellation-waste`: long-horizon agentic with user-side cancellation
  (SWE-Lancer, tau-bench user-sim, ToolBench, GAIA)

Each row gets the most plausible 1-3 failure modes for its profile. These are
*hypotheses* the benchmark could be used to test, not measured outcomes.

### `suitability` (yes / maybe / no)
Decision rule used:
- **yes** if (a) data is publicly accessible (or accessibly gated with reasonable
  approval), AND (b) at least one of the routing dimensions is uniquely
  illuminating, AND (c) reproducibility is not blocked by deprecation/data-loss.
- **maybe** if data is gated/synthetic/needs-live-env, OR routing signal
  overlaps fully with another `yes` entry, OR data assembly is heavy.
- **no** if the benchmark cannot be reproduced from public sources (only
  BrowserArena qualifies — its GitHub repo returns 404 per Agent A).

Tally: 46 yes / 10 maybe / 1 no across the 57 catalogued entries.

---

## Cross-cutting observations (cited)

1. **Only one public trace has prefix-cache hashes.** Mooncake's `hash_ids`
   field is unique in this catalog. Source:
   https://github.com/kvcache-ai/Mooncake (Agent A row, Agent G #3). Every
   other "prefix_reuse_potential = high" assignment is *inferred* from
   conversation structure, not measured.
2. **Only one public trace combines bursty arrivals with session IDs.** BurstGPT
   (`Session ID` + `Timestamp` + `Request tokens` + `Response tokens` over ~110
   days) — source https://github.com/HPMLL/BurstGPT (Agent A, Agent G #2).
3. **Production traces lack tool-call structure.** None of Azure 2023/2024,
   BurstGPT, or Mooncake encode tool-call loops. Tool-call workloads must come
   from ToolBench / AppWorld / WebArena / OSWorld / Terminal-Bench / tau-bench /
   AgentBench (sources in Agent A rows). For a tool-aware router, these eight
   benchmarks are the realistic source — production traces contribute the
   arrival process, not the per-step structure.
4. **Extreme-prefill bucket is well-covered.** LongBench v2 (up to 2M words),
   Natural Questions (full Wikipedia page), NarrativeQA (~41k tok books),
   BookSum (book-chapters), SWE-bench Pro (problem_statement up to 8k chars +
   repo context), L-Eval (up to 200k tok). Source: Agent A rows for each.
5. **Decode-bound short-request bucket is well-covered.** MMLU, HumanEval, MBPP,
   GSM8K, MATH, GPQA, BBH all produce small-to-medium decode at very high
   concurrency. Together they give a wide spread of input/output ratios for
   batch-throughput testing.
6. **Chat session affinity is best-served by WildChat-1M (public)** rather than
   LMSYS-Chat-1M (gated). WildChat exposes per-turn timestamp +
   conversation_hash + hashed_ip (Agent C row); LMSYS is gated and PII-redacted
   to "NAME_1" placeholders (Agent A row).
7. **Reproducibility/freshness risk.** 4 archived/deprecated repos in catalog:
   GSM8K (archived Apr 2026), Big-Bench (archived Apr 2026), HELM (entered
   maintenance Jun 2026), SWE-Lancer original (archived Jul 2025). All sourced
   from Agent A rows. Data files remain fetchable but no new fixes will land.
8. **The only "no" is BrowserArena.** github.com/web-arena-x/BrowserArena → 404
   (Agent A). The arxiv-only Arena cannot be reproduced offline; we recorded it
   as a finding rather than dropping it silently.

---

## Open routing dimensions not directly answered by public benchmarks

These belong in HHRouting-Bench's *synthetic-trace* layer (to be built later),
because no public dataset measures them:

- **Per-tenant SLO heterogeneity** (e.g. "free tier 5s TTFT, paid 500ms TTFT").
  None of the production traces carry tenant tier; Azure 2023/2024 has no
  tenant ID at all.
- **Speculative-decoding draft-model affinity.** No public trace records
  draft-vs-target token counts.
- **Cancellation events.** Azure/BurstGPT/Mooncake do not record
  client-side cancels; SWE-bench harness does emit them but they are not in the
  static dataset.
- **Multi-region / cross-DC routing.** Hashed-IP in WildChat is the closest
  signal; geographic distribution is coarse (country/state per
  https://huggingface.co/datasets/allenai/WildChat-1M).

These are flagged here so downstream Agent D/E/F deliverables can address them.
