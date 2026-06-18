# 04 — Trace Feasibility Summary (Agent D)

Scope: classify which of the validated benchmarks/datasets can become **request-level
serving traces** for HHRouting-Bench, and which need synthetic augmentation. We care about
serving mechanics (arrivals, input/output token lengths, KV/prefix reuse, session/tenant
identity, tool-call loops), **not** model accuracy. Every claim below is sourced from the
peer deliverables and the cited URLs; estimates are labeled.

## Inputs read
- `01_benchmark_validation_table.csv` (Agent A) — 57 benchmarks with a
  `request_trace_extractable` column. Primary input.
- `01b_production_traces.md` (Agent A) — production serving traces; source of 3 extra rows
  not in the main table (LMSYS Chatbot Arena Conversations, Alibaba GenAI GenTD26,
  Azure Functions 2019).
- `03_payload_schema_inventory.md` + `03_sampling_blockers.md` (Agent C) — concrete field
  maps and access blockers per dataset.
- **MISSING DEPENDENCY:** `02_workload_decomposition.csv` (Agent B) was **not present** in
  the shared folder at run time (`ls` showed no `02_*` file). Token-range / burstiness
  decomposition from B could not be cross-referenced; this matrix is built from A+C only.
  Re-run recommended once B lands, to reconcile token estimates.

Total classified: **60 rows** (57 from A's table + 3 production traces from 01b).

## Classification scheme
- **direct_trace** — has timestamps AND input/output token counts (or request logs).
- **payload_only** — has prompt/output/task data but NO realistic arrival times.
- **schema_only** — has task structure but payload extraction is hard (gated / live-env / VM / archived-hosting).
- **not_suitable** — cannot reasonably support routing workload decomposition.

Counts: direct_trace = **7**, payload_only = **43**, schema_only = **8**, not_suitable = **2**.

---

## 1. Direct traces (rare, precious — use as the backbone)

These already carry real arrival timestamps + token counts; effort is *low* (mostly just
adding synthetic routing labels like SLO class, tenant, P/D annotations).

1. **Mooncake Trace** (rank 1) — `timestamp + input_length + output_length + hash_ids`. The
   `hash_ids` (remapped prefix-cache block hashes, up to ~50% cache hit) make this the
   **only** trace with a native **prefix-reuse signal** — exactly what a KV-cache-aware
   router needs. Plus toolagent/synthetic sub-traces. No prompt text (remapped).
   https://github.com/kvcache-ai/Mooncake
2. **BurstGPT** (rank 2) — `Timestamp + Session ID + Request/Response tokens + Log Type
   (conversation/API)`. Largest set ~110 days / ~5.34M rows. Native **session identity** and a
   coarse conversation-vs-API split. https://github.com/HPMLL/BurstGPT
3. **Azure LLM Inference Trace 2024** (rank 3) and **4. 2023** (rank 4) —
   `TIMESTAMP + ContextTokens + GeneratedTokens`, separate code/conv CSVs. The cleanest
   pure arrival+token traces, but no session, no prefix hash, no text (GDPR).
   https://github.com/Azure/AzurePublicDataset
5. **LMSYS Chatbot Arena Conversations** (rank 5) — `tstamp` (per-conversation) + raw
   multi-turn `conversation_a/_b` text + `turn` + `language`. Real timestamps and real text,
   so token counts are derivable by re-tokenizing (estimate). NC terms may apply.
   https://huggingface.co/datasets/lmsys/chatbot_arena_conversations
6. **WildChat** (rank 6) — per-assistant-turn timestamps (response-receipt, *not*
   request-arrival) + `hashed_ip` (~coarse tenant) + non-unique `conversation_hash` session +
   full conversation text. Tokens by re-tokenizing. Full version gated; ODC-BY.
   https://huggingface.co/datasets/allenai/WildChat-1M
7. **Alibaba GenAI Serving Trace (GenTD26)** (rank 7) — real top-down request trace incl.
   `lora_request_trace.csv` (native **LoRA adapter IDs** — unique among all sources) +
   pipeline/GPU duty-cycle data. **Caveat:** GenAI *image* (Stable Diffusion), **not** LLM
   text generation — only usable with an explicit heterogeneity label / for P/D-style
   pipeline-stage routing analogy. License unknown (no SPDX match).
   https://github.com/alibaba/clusterdata/tree/master/cluster-trace-v2026-GenAI

Note on rigor: only Mooncake, BurstGPT, and the two Azure traces are *unambiguous*
request-arrival traces. Arena/WildChat timestamps are conversation/response-completion
timestamps, marked `direct_arrivals_available = partial` in the matrix.

## 2. Payload-only (the majority — text/tasks present, arrivals must be synthesized)

43 of 60. These have prompts/outputs (or measurable gold text) but **no arrival process**.
The standard move (already implemented in vLLM `benchmark_serving.py`) is to graft a Poisson
or trace-driven arrival on top. Effort is mostly *med*. High-value sub-groups:

- **Tool-call loops (static, no harness needed):** **ToolBench** (rank 9 — 469,585 real API
  calls, 120k+ solution paths with Action/Thought nodes directly visible), **tau-bench**
  (rank 10 — `historical_trajectories/` + user-sim), **AppWorld** (rank 11 — `num_api_calls`
  + `datetime` + downloadable ReAct baseline trajectories). Best donors for the tool-call /
  multi-turn-context-growth dimension.
- **Long-context / prefill pressure:** **RAGBench** (13, multi-passage → prefix reuse),
  **LongBench** (14), **L-Eval** (15, 3k–200k tokens), **LongBench v2** (16, up to 2M words),
  **NarrativeQA** (22), **Qasper** (23), **HotpotQA** (24, shared distractor passages →
  cache-reuse), and the summarization family (arXiv/PubMed/GovReport/MultiNews/BookSum,
  36–40). These drive the input-length / KV-lifetime axes; outputs are short (QA/MCQ) or long
  (summarization).
- **Multi-turn chat:** LMSYS-Chat-1M (8), ShareGPT serving source (12, the canonical vLLM
  benchmark payload), ShareGPT (28), UltraChat (29, synthetic→caveat), OpenAssistant (30,
  tree→needs path-flatten).
- **Coding (single-shot or harness-dependent output):** SWE-bench family (17–19),
  HumanEval (41), MBPP (42), LiveCodeBench (31), RepoBench (32), DevEval (33),
  BigCodeBench (34), Terminal-Bench (35).
- **Batch eval (short prompts, ideal concurrency stressors):** HELM (43), lm-eval-harness
  (44), MMLU/MMLU-Pro (45–46), GSM8K (47), MATH (48), Big-Bench (49), BBH (50). Several are
  archived/maintenance-mode (GSM8K, Big-Bench, HELM) — usable but frozen.

## 3. Schema-only (extraction hard — gated, live-env, or VM-bound)

8 of 60. Task structure exists but you cannot get payloads/traces without clearing a
barrier, so synthetic generation dominates the effort (*high*):
- **Gated access:** GAIA (54), GPQA (58), and partly WorkArena (53)/OSWorld (52).
- **Live environment / VM / Docker fleet required to produce any trace:** AgentBench (51),
  OSWorld (52), WorkArena (53), MiniWoB++ (55).
- **Hosting/availability uncertain:** SWE-Lancer (56, archived + Git-LFS, gating unconfirmed),
  2WikiMultihopQA (57, Dropbox-only, no HF, gold answers not shown).

These are still useful *later* for agentic/tool-loop realism, but tonight they are not
cheap trace sources.

## 4. Not suitable (drop or repurpose)

- **BrowserArena (60) — DROP.** `github.com/web-arena-x/BrowserArena` returns HTTP 404;
  no repo, no downloadable dataset; exists only as arXiv 2510.02418 as a live platform. Not
  reproducible offline. https://github.com/web-arena-x/BrowserArena
- **Azure Functions Trace 2019 (59) — repurpose, don't decompose.** No token lengths / no LLM
  payload, so it is `not_suitable` as a standalone request trace. **But** it is the
  community-standard **arrival-process donor** (AlpaServe uses it for burstiness). Keep it as
  a *source of realistic arrival timestamps* to graft onto payload_only datasets.
  https://github.com/Azure/AzurePublicDataset/blob/master/AzureFunctionsDataset2019.md

---

## The single most important missing data type

**Realistic per-request arrival timestamps (the arrival process / burstiness).**

- Only **7 of 60** sources carry timestamps at all, and only **4** (Mooncake, BurstGPT,
  Azure 2023, Azure 2024) are unambiguous request-arrival traces. The other **53** are
  payload/schema sources with **no arrival information whatsoever**.
- Every routing concern that depends on *time* — concurrency level, queueing, burstiness,
  SLO attainment, P/D scheduling pressure — is therefore **unobservable** in the bulk of the
  corpus and must be synthesized.
- **Recommended strategy:** treat the 4 real arrival traces (+ Azure Functions 2019 as a
  burstiness donor) as the **arrival/timing backbone**, and graft the rich payloads
  (token-length, multi-turn, tool-loop, long-context, prefix-reuse) from the payload_only
  datasets onto those timelines. This is exactly the synthesis B/E should drive next.

Runner-up missing type: **native prefix/cache-reuse identity.** Only **Mooncake**
(`hash_ids`) exposes it directly, and only **GenTD26** exposes **LoRA adapter IDs**
(for non-LLM image traffic). Both `prefix ID` and `LoRA adapter ID` appear as
`synthetic_fields_needed` on nearly every other row.

## Caveats / unverified
- `02_workload_decomposition.csv` (Agent B) absent at run time — token ranges not reconciled.
- Several `last_update`, license, and arXiv-id fields are "insufficient evidence" in A's
  table; those caveats are carried forward, not resolved here.
- All token counts referenced are estimates (re-tokenizing text, or A/C's `char/4`
  heuristic), never exact serving counts, except where a trace ships native token columns
  (Mooncake, BurstGPT, Azure).
