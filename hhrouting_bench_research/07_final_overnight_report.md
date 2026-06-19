# HHRouting-Bench — Final Overnight Report

**Agent R (Synthesizer)** · 2026-06-18 · serving-routing scope only (NOT model accuracy)

This report synthesizes the committee deliverables 01_/01b_/02_/03_/04_/05_ and their source
sidecars. It does not introduce new research; every claim traces to a peer deliverable and a
source URL. Where peers disagree or a deliverable is missing, it is flagged explicitly.

**Inputs synthesized**
- `01_benchmark_validation_table.csv` (Agent A) — 57 validated benchmarks, 15 cols, every row cited.
- `01b_production_traces.md` (Agent A/G) — 7 production serving traces.
- `02_workload_decomposition.csv` + `_notes.md` (Agent B) — 57 rows × 16 routing dimensions, MEASURED-vs-ESTIMATE labeled.
- `03_payload_schema_inventory.md` + `03_sample_payloads.jsonl` + `03_sampling_blockers.md` (Agent C) — field maps + access blockers.
- `04_trace_feasibility_matrix.csv` + `_summary.md` (Agent D) — 60 rows classified direct/payload/schema/not-suitable.
- `05_canonical_workload_taxonomy.csv` + `.md` (Agent E) — 10 canonical workload classes.
- Source sidecars `_sources_{A,B,C,D,E,G}.jsonl` → merged into `sources.json` (153 unique URLs) + `sources.bib`.

> **MISSING DELIVERABLE — Agent F (red-team / `06_`).** There is no `06_*` file, no
> `_sources_F.jsonl`, and no `_progress_F.md` in the shared folder. The committee's adversarial
> critique was **never produced**. Section 10 below is a synthesis-time red-team written by Agent R
> from the existing evidence; it is **not** an independent F deliverable and should be treated as
> lower-confidence than the rest of the package. Re-running Agent F is the top open action (Section 11).

---

## 1. Executive summary

**What we can now confidently say (every point cited to a peer row):**

1. **Public, GitHub-validated benchmarks usable for request-level serving decomposition exist in
   quantity.** Agent A validated **57** benchmarks across 8 families by live-fetching repos, HF cards,
   and papers; Agent D classified **60** rows (57 + 3 extra production traces). Of those, **46 are
   suitable=yes, 10 maybe, 1 no** (Agent B tally). Only **one** must be dropped outright — BrowserArena
   (GitHub 404, arXiv-only) — confirmed by A, B, and D.

2. **Real request-level *arrival* traces are the scarce resource.** Only **7 of 60** sources carry
   any timestamps, and only **4** are unambiguous request-arrival traces: **Mooncake, BurstGPT, Azure
   LLM Inference 2023, Azure LLM Inference 2024** (Agent D §"single most important missing data type").
   The other **53** have payloads/tasks but **no arrival process** — burstiness, concurrency, queueing,
   and SLO attainment are unobservable in them and must be synthesized.

3. **Two routing signals are each available from exactly one public trace.**
   - **Prefix/KV-cache reuse identity:** only **Mooncake** ships `hash_ids` (remapped prefix-cache
     block hashes, ~50% hit ratio) — https://github.com/kvcache-ai/Mooncake (Agent B obs #1).
   - **Bursty arrivals + session identity together:** only **BurstGPT** ships `Session ID` +
     `Timestamp` + token columns over ~110 days / ~5.34M rows — https://github.com/HPMLL/BurstGPT
     (Agent B obs #2).
   Every other "prefix_reuse=high" / "session affinity" assignment is *structurally inferred*, not measured.

4. **Production traces carry timing but no structure; agent benchmarks carry structure but no timing.**
   None of Azure/BurstGPT/Mooncake encode tool-call loops (Agent B obs #3). Tool-call realism must come
   from ToolBench / AppWorld / tau-bench / AgentBench / WebArena / OSWorld. The correct build strategy
   is therefore **graft rich payloads onto the 4 real arrival backbones** (Agent D, Agent E build order).

5. **A canonical 10-class workload taxonomy now exists** (Agent E), each class grounded in named,
   cited benchmarks and mapped to the routing axis it stresses (Section 7).

6. **Token ranges are mostly estimates.** Exact serving token counts exist only for the native-column
   traces (Mooncake/BurstGPT/Azure) and a handful of card-stated values (LongBench, L-Eval, NarrativeQA,
   arXiv/PubMed, RAGBench/HotpotQA answers, HumanEval/MBPP/GSM8K inputs, AppWorld `num_api_calls`).
   All agentic per-step ranges are reasoned from task shape (Agent B/E).

**Bottom line:** we have enough to build HHRouting-Bench v1 covering all 10 classes from public data.
The backbone is 4 real traces + Azure Functions 2019 as a burstiness donor; the payload banks are
~13 P0 datasets. The synthetic layer is needed primarily for **arrivals** (53/60 sources) and for
dimensions no public dataset measures (tenant SLO tiers, cancellation, spec-decode, multi-region).

---

## 2. Top 20 candidate benchmarks

Ranked by a composite of: real arrival data, unique routing signal, license clarity, community
recognition, extraction effort, and non-redundancy. "Class" = canonical class (Section 7). "Mode" =
trace extraction mode. Effort/feasibility from Agent D; license from Agent A.

| # | Benchmark | Family | Mode | Class | License | Why it ranks here (cited) |
|---|-----------|--------|------|-------|---------|----------------------------|
| 1 | **Mooncake Trace** | Prod trace | direct_trace | production_mixed | Apache-2.0 | Only trace with `hash_ids` prefix-cache signal; ts+in+out lengths; ~50% hit. A/B/D/G. |
| 2 | **BurstGPT** | Prod trace | direct_trace | production_mixed / interactive_chat | CC-BY-4.0 | Only trace combining bursty arrivals + `Session ID`; 110d/5.34M rows. A/B/D/G. |
| 3 | **Azure LLM Inference 2024** | Prod trace | direct_trace | production_mixed | CC-BY-4.0 | Clean ts+ContextTokens+GeneratedTokens; backs DynamoLLM HPCA25. A/D/G. |
| 4 | **Azure LLM Inference 2023** | Prod trace | direct_trace | production_mixed | CC-BY-4.0 | Same schema, separate code/conv CSVs; backs Splitwise ISCA24. A/D/G. |
| 5 | **ShareGPT (vLLM source)** | Prod/chat | payload_only | interactive_chat | Apache-2.0 (provenance risk) | Canonical vLLM `benchmark_serving.py` payload; tooling already synthesizes Poisson arrivals. A/D/G. |
| 6 | **RAGBench** | RAG | payload_only | rag_qa_stateless | CC-BY-4.0 | Strongest prefix-cache donor (Q + 4 shared docs); clean license, ~100K rows. A/B/C/D. |
| 7 | **WildChat** | Chat | direct_trace (partial) | interactive_chat | ODC-BY | Best *public* chat trace: per-turn ts + `conversation_hash` + `hashed_ip`. A/C/D. |
| 8 | **ToolBench** | Agent/tool | payload_only | workflow_tool_agent | Apache-2.0 | 469,585 real API calls; 120k+ static DFSDT trajectories (replayable tool loops). A/B/C/D. |
| 9 | **LongBench v2** | Long-context | payload_only | long_context_extreme_prefill | Apache-2.0 | Up to 2M-word context; most extreme prefill in catalog. A/B/C/D. |
| 10 | **SWE-bench Verified** | Coding/SWE | synthetic_required | swe_repo_agent | MIT (harness) | 500 deterministic agentic tasks; reproducible long-horizon KV-growth trace. A/B/C/D. |
| 11 | **L-Eval** | Long-context | payload_only | long_context_extreme_prefill | GPL-3.0 | 3k–200k-tok wide input distribution; gold answers visible. A/B/D. |
| 12 | **arXiv summarization** | Summarization | payload_only | long_doc_summarization | unstated on card | MEASURED long input (~6038) + medium decode (~299) → TPOT/chunked-prefill stress. A/B/D. |
| 13 | **RepoBench** | Coding/SWE | payload_only | strict_slo_autocomplete | CC-BY-4.0 | ~50:1 prefill:decode; same-repo prefix reuse for cache-aware routing. A/B/C/D. |
| 14 | **MMLU** | Batch eval | payload_only | batch_eval_throughput | MIT | Tiny in/out MCQ → max-concurrency QPS sweep backbone. A/B/D. |
| 15 | **HumanEval** | Coding/SWE | payload_only | batch_eval_throughput | MIT | 164 single-shot prompts in-repo; clean high-concurrency decode-bound test. A/B/D. |
| 16 | **AppWorld** | Agent/tool | payload_only | workflow_tool_agent | Apache-2.0 | MEASURED `num_api_calls` 30–101; downloadable ReAct trajectories; active. A/B/C/D. |
| 17 | **tau-bench** | Agent/tool | synthetic_required | workflow_tool_agent | MIT | Interlocked LLM-LLM user-sim loops; `historical_trajectories/`. (Deprecation→tau2.) A/B/C/D. |
| 18 | **PubMed summarization** | Summarization | payload_only | long_doc_summarization | unstated on card | MEASURED long-in/long-out; second TPOT donor. A/B/D. |
| 19 | **GSM8K** | Batch eval | payload_only | batch_eval_throughput | MIT (widely cited) | CoT decode for batch fairness. (Archived Apr 2026 → data frozen but stable.) A/B/D. |
| 20 | **WebArena** | Agent/browser | synthetic_required | browser_computer_use | Apache-2.0 | Huge DOM prefill vs tiny action (~10:1); needs self-hosted Docker sites. A/B/C/D. |

**Honorable mentions just outside 20** (cited): NarrativeQA (~41k-tok stories, extreme prefill, Apache-2.0);
Natural Questions (full-Wikipedia prefill, but 144.87 GB); Qasper (same-paper prefix reuse); HotpotQA
(shared distractor passages); LongBench v1; BBH (shared CoT-exemplar prefix); BigCodeBench; LiveCodeBench.
**Azure Functions Trace 2019** is excluded from the benchmark ranking on purpose — it has no tokens/payload,
but it is the **arrival-process donor** (used by AlpaServe) and belongs in the timing backbone (Agent D §4).

---

## 3. Top 10 highest-priority benchmarks for HHRouting-Bench

Selected so that the set (a) supplies all 4 real arrival backbones and (b) covers every one of the 10
canonical classes with the best public, clean-license donor. Ordered by build value.

1. **Mooncake Trace** — *the* prefix-cache-aware backbone. `hash_ids` is the only public per-request
   prefix-block signal; without it, prefix-cache-aware routing cannot be evaluated against real data.
   Low effort (direct replay). Apache-2.0. (A/B/D/G)
2. **BurstGPT** — *the* bursty+session backbone. Unique combination of real burstiness and `Session ID`
   over 110 days; drives interactive-chat, session-affinity, and head-of-line-blocking tests. CC-BY-4.0. (A/B/D/G)
3. **Azure LLM Inference 2024 (+2023)** — cleanest pure arrival+token traces; the neutral burstiness
   reference with no payload-license entanglement (GDPR-stripped). CC-BY-4.0. (A/D/G)
4. **ShareGPT (vLLM source)** — the de-facto serving-benchmark payload bank; vLLM's
   `benchmark_serving.py` already synthesizes Poisson arrivals over it, so it is the fastest path to a
   runnable baseline. Treat provenance/legal risk as a caveat (Agent A). (A/D/G)
5. **RAGBench** — the strongest prefix-cache *payload* donor (question + 4 shared documents), clean
   CC-BY-4.0, no gating; lets us test prefix-aware vs prefix-blind routing on real text. (A/B/C/D)
6. **WildChat** — the best *public* chat trace (LMSYS-Chat-1M is gated). Per-turn timestamps +
   `conversation_hash` + `hashed_ip` give arrival/session/coarse-tenant signal in one ODC-BY dataset. (A/C/D)
7. **ToolBench** — the richest static tool-call corpus: 469,585 real API calls and 120k+ DFSDT
   trajectories with Action/Thought/Observation nodes — replayable tool loops without re-running a server. (A/B/C/D)
8. **LongBench v2 (+ L-Eval)** — the extreme-prefill / TTFT-OOM stressor (8k–2M words). Tests
   length-aware admission control and OOM-avoidance placement. Apache-2.0 / GPL-3.0. (A/B/C/D)
9. **SWE-bench Verified** — the long-horizon agentic class with a deterministic 500-task set for
   reproducibility; produces monotonic-KV-growth per-task traces via SWE-agent. (A/B/C/D)
10. **MMLU + HumanEval + GSM8K (batch-eval bundle)** — the throughput/concurrency backbone that runs
    as a **native batch today with zero synthesis** (MCQ + coding + CoT mix). All MIT. (A/B/D)

> Classes not directly in the top-10 headline but covered by their best donor at P0/P1:
> `long_doc_summarization_streaming` → arXiv/PubMed (#12/#18); `strict_slo_autocomplete` → RepoBench (#13);
> `browser_computer_use` → WebArena (#20). These are P1 only because they need a harness/VM or have
> license caveats, not because they are low value.

---

## 4. Benchmarks to drop or deprioritize

**DROP (cannot reproduce from public sources):**
- **BrowserArena** — `github.com/web-arena-x/BrowserArena` returns HTTP 404; exists only as arXiv
  2510.02418 as a live platform, no repo/dataset. Unanimous across A/B/D. Not in any class.

**REPURPOSE, do not decompose as a benchmark:**
- **Azure Functions Trace 2019** — no tokens, no LLM payload; `not_suitable` as a standalone request
  trace. **Keep it as the arrival/burstiness donor** to graft onto payload_only datasets (Agent D §4).

**DEPRIORITIZE — gated / live-env / VM-bound (high extraction effort, use later):**
- **LMSYS-Chat-1M** (gated custom license, PII-redacted to `NAME_1`) — **WildChat covers the same class
  publicly**; only revisit if the gated raw timestamps are needed. (A/B)
- **GAIA, GPQA** — gated HF (contact-sharing; GPQA forbids plaintext example posting). (A)
- **OSWorld, WorkArena, MiniWoB++, AgentBench** — require VM/Docker fleet or live ServiceNow to
  generate any trace; defer to the agentic phase. (A/C/D)
- **WorkArena** also gated (`ServiceNow/WorkArena-Instances`). (A)

**DEPRIORITIZE — reproducibility / freshness / legal risk:**
- **Archived / maintenance repos** (data fetchable but frozen): GSM8K (archived Apr 2026), Big-Bench
  (archived Apr 2026), HELM (maintenance Jun 2026), SWE-Lancer (original archived Jul 2025). Use the
  data, but pin versions. (A/B obs #7)
- **SWE-Lancer** — hosting/gating unconfirmed (Git LFS); redundant with SWE-bench Pro for the enterprise
  long-context case. (A/B/D)
- **MultiNews** (LILY-LAB non-commercial), **TriviaQA** (license "unknown", copyright caveat),
  **2WikiMultihopQA** (Dropbox-only, no HF) — license/hosting friction; redundant within their classes. (A/B/D)
- **UltraChat** — synthetic ChatGPT-generated; distributions are model-shaped, not real serving traffic.
  Useful as a stress corpus, not for arrival realism. (A/B)
- **Natural Questions / TriviaQA** — strong prefill payloads but 145 GB / 35 GB downloads; deprioritize
  vs L-Eval/LongBench for the same axis. (A/B/D)
- **DevEval** — no GitHub license, 2.59 GB tarball reassembly, broken viewer; RepoBench covers the class. (A/B/D)
- **Alibaba GenAI GenTD26** — real trace with unique LoRA-adapter IDs, **but** it is image generation
  (Stable Diffusion), not LLM text; license unknown. Keep only as a heterogeneity/LoRA-routing analogy. (A/D)

---

## 5. Workload decomposition summary

Agent B decomposed all 57 benchmarks into 16 serving-routing dimensions
(`02_workload_decomposition.csv`). Distilled findings:

- **Suitability:** 46 yes / 10 maybe / 1 no. The single "no" is BrowserArena.
- **Prefill/decode coverage is broad and balanced:**
  - *Extreme prefill* (>32k tok, OOM-risk): LongBench v2 (≤2M words), Natural Questions (full Wikipedia),
    NarrativeQA (~41k tok), BookSum, L-Eval (≤200k), SWE-bench Pro, GovReport. (Agent B obs #4)
  - *Decode-bound, tiny-request, high-concurrency:* MMLU, HumanEval, MBPP, GSM8K, MATH, GPQA, BBH. (obs #5)
  - *Joint heavy prefill + sustained decode (TPOT):* arXiv/PubMed/GovReport/BookSum summarization.
  - *Extreme prefill:decode imbalance (cache-decisive):* RepoBench ~50:1, Natural Questions ~1000:1,
    NarrativeQA ~1000:1, WebArena/OSWorld ~10–15:1.
- **Session/KV-lifetime:** `session-persistent` only where an ID exists — WildChat `conversation_hash`,
  BurstGPT `Session ID`. Agentic benchmarks are `long` (KV held for the whole multi-step task).
- **Tool-call frequency = high** only for the 8 agent benchmarks (ToolBench, AppWorld, tau-bench,
  AgentBench, WebArena, VisualWebArena, OSWorld, + SWE-agent harness). Production traces are tool-blind.
- **Arrival pattern:** `bursty` (real) only for Azure 2023/2024 + BurstGPT; `steady/bursty` for Mooncake;
  everything else is `batch` or `batch (synthesized)`.
- **Likely router failure modes** are hypotheses each benchmark can *test*, not measured outcomes:
  head-of-line-blocking, prefill-starvation-of-decode, decode-backlog-overload, kv-cache-pressure,
  prefix-cache-miss-penalty, session-affinity-failure, OOM, tail-latency-explosion,
  unfair-tenant-starvation, cancellation-waste.

**Method caveat (carried forward):** token ranges are MEASURED only where a card/paper/sample states
them; all others are ESTIMATE via `ceil(chars/4)` on sampled text or reasoning from task shape (Agent B
notes). Production-trace ranges are `varies-MEASURED` (per-request integer columns ship in the data;
not numerically summarized this run because the CSVs were not bundled in the repo).

---

## 6. Trace feasibility matrix summary

Agent D classified 60 rows (`04_trace_feasibility_matrix.csv`):

| Mode | Count | Meaning | Examples |
|------|------:|---------|----------|
| **direct_trace** | 7 | real timestamps + token counts (or request logs) | Mooncake, BurstGPT, Azure 2023/2024, LMSYS Arena*, WildChat*, GenTD26* (*partial) |
| **payload_only** | 43 | real payload, **no** arrivals (synthesize Poisson/trace) | ShareGPT, RAGBench, LongBench, ToolBench, SWE-bench, MMLU, summarization family… |
| **schema_only** | 8 | structure exists, payload gated/live-env/VM | AgentBench, OSWorld, WorkArena, MiniWoB++, GAIA, GPQA, SWE-Lancer, 2WikiMultihopQA |
| **not_suitable** | 2 | cannot support routing decomposition | BrowserArena (drop), Azure Functions 2019 (repurpose as arrival donor) |

**The single most important missing data type: realistic per-request arrival timestamps.** Only 4 of 60
sources are unambiguous request-arrival traces; 53 have no timing at all. Every time-dependent routing
concern (concurrency, queueing, burstiness, SLO attainment, P/D pressure) is therefore unobservable in
the bulk of the corpus and must be synthesized. **Runner-up missing type:** native prefix/cache-reuse
identity (Mooncake `hash_ids` only) and LoRA-adapter identity (GenTD26 only, non-LLM).

> **Cross-deliverable discrepancy (resolved):** Agent D ran **before** Agent B's
> `02_workload_decomposition.csv` landed (D's log and summary both say it was "ABSENT at run time"), so D
> built its matrix from A+C only. The token estimates in D were therefore not reconciled against B.
> Agent E ran *after* both and did reconcile them. **For token ranges, trust Agent B/E over Agent D.**
> The feasibility *classes* themselves are unaffected (they depend on schema/timestamps, not token counts).
> A one-line re-run of D against B is a cheap consistency win (Section 8).

---

## 7. Canonical workload taxonomy (the 10 classes)

From Agent E (`05_canonical_workload_taxonomy.{md,csv}`). Each class is grounded in named, cited
benchmarks and mapped to the routing axis it stresses and its primary failure mode.

| # | Class | Stresses | Primary donors (cited) | Real arrivals? | Synthetic needed |
|---|-------|----------|------------------------|:---:|---|
| 1 | `interactive_chat_global` | burst absorption vs session stickiness; TTFT | BurstGPT, WildChat, Azure, LMSYS Arena, ShareGPT | YES (BurstGPT/Azure) | tenant SLO tier, prompt text (Azure GDPR-stripped) |
| 2 | `rag_qa_stateless` | prefix-cache reuse; TTFT | RAGBench, HotpotQA, MuSiQue, Qasper, TriviaQA | NO | arrivals |
| 3 | `long_context_extreme_prefill` | extreme prefill, OOM, admission control | LongBench v2, LongBench, L-Eval, NarrativeQA, NQ | NO | arrivals |
| 4 | `long_doc_summarization_streaming` | joint prefill + sustained decode; TPOT | arXiv, PubMed, GovReport, MultiNews, BookSum | NO | arrivals |
| 5 | `strict_slo_autocomplete` | ~50:1 prefill:decode under tight latency; cache locality | RepoBench, DevEval | NO | arrivals + IDE-session model |
| 6 | `swe_repo_agent` | long-lived growing KV; co-location | SWE-bench (+Verified/Pro), SWE-Lancer | NO (harness-gen) | harness trace + arrivals |
| 7 | `workflow_tool_agent` | tool-loop sessions; cancellation | ToolBench, AppWorld, tau-bench, AgentBench | PARTIAL (static trajectories) | arrivals |
| 8 | `browser_computer_use` | huge per-step prefill vs micro action; episode stickiness; image tokens | WebArena, VisualWebArena, OSWorld, WorkArena | NO (harness/VM) | arrivals + harness/VM |
| 9 | `batch_eval_throughput` | max-concurrency throughput; decode-backlog fairness | MMLU(-Pro), GSM8K, MATH, HumanEval, MBPP, BBH, Big-Bench, HELM, lm-eval-harness, Live/BigCodeBench | NO (native batch = legit) | none for throughput; optional Poisson |
| 10 | `production_mixed_enterprise` | everything at once + tenant fairness (capstone) | Mooncake, BurstGPT, Azure 2023/2024, Azure Functions 2019, GenTD26 | YES (4 backbones) | tenant tiers, SLO classes, tool structure |

**Cross-cutting (Agent E):** arrivals are the scarce resource (8/10 classes need synthesized arrivals);
only one real prefix signal (Mooncake) and one real bursty+session trace (BurstGPT); production traces
lack tool structure; most token ranges are ESTIMATE; gated/archived sources raise synthesis cost.

---

## 8. Data extraction plan — next 48 hours (concrete, ordered)

Cheapest→richest, mirroring Agent E's build order. Each step names the exact files/fields.

**Day 1 — backbones + zero-synthesis class (get a runnable harness end-to-end):**
1. **Fetch the 4 real arrival traces.** Mooncake `mooncake_trace.jsonl` (FAST25-release) →
   `timestamp,input_length,output_length,hash_ids`; BurstGPT `BurstGPT_3` CSV →
   `Timestamp,Session ID,Request tokens,Response tokens,Model,Log Type`; Azure 2023 + 2024 code/conv
   CSVs → `TIMESTAMP,ContextTokens,GeneratedTokens`. Normalize all to a common schema
   `(t, in_tok, out_tok, session_id?, prefix_ids?)`. Validate row counts; record them (A/G left them "not stated").
2. **Fetch Azure Functions 2019** invocation counts as the standalone **arrival-process donor**.
3. **Stand up `batch_eval_throughput` now** (no synthesis): MMLU (`cais/mmlu`) + GSM8K + HumanEval as
   one max-concurrency batch. This validates the measurement harness (throughput, TTFT/TPOT, fairness).

**Day 1→2 — payload banks for the high-value classes:**
4. **RAGBench** (`rungalileo/ragbench`): pull `question,documents(4),response,id`; hash the document set
   per row → prefix-cache group key. (rag_qa_stateless + prefix-cache test.)
5. **WildChat** (`allenai/WildChat-1M`, public split): extract per-turn `conversation` (role/content),
   per-assistant-turn `timestamp`, `conversation_hash`, `hashed_ip`. Re-tokenize text → token lengths
   (label ESTIMATE). (interactive_chat session/affinity.)
6. **ShareGPT V3** payload: load via vLLM `benchmark_serving.py` to get the existing Poisson-arrival
   tooling for free.
7. **Long-context bank:** LongBench v2 `data.json` (`_id,length,context,question,answer`) bucketed
   <32k / 32k–128k / >128k; add L-Eval (`L4NLP/LEval`). (long_context_extreme_prefill.)
8. **Summarization bank:** arXiv + PubMed (`ccdv/*-summarization`) `article,abstract`. (TPOT class.)
9. **RepoBench:** group rows by `repo_name`; note the HF loader needs a legacy dataset script (Agent C
   blocker) — plan a manual parquet pull. (strict_slo_autocomplete.)

**Day 2 — tool/agentic structure (static where possible):**
10. **ToolBench:** download the off-GitHub data (Google Drive/Tsinghua Cloud); parse DFSDT answer trees
    into per-step `(input_len, output_len, step_type)` sequences keyed by `query_id`. (workflow_tool_agent.)
11. **AppWorld:** pull HF mirror metadata (`task_id,num_api_calls,datetime`) + downloadable ReAct
    trajectories. (Second tool donor.)
12. **SWE-bench Verified:** stage the 500 tasks; defer running SWE-agent (harness) to the agentic phase
    but capture `problem_statement,patch,instance_id,created_at`.

**Day 2 — consistency + plumbing:**
13. **Re-run Agent D's feasibility matrix against Agent B's `02_*.csv`** to reconcile token estimates
    (D ran before B landed). Cheap, removes the one known cross-deliverable gap.
14. **Re-run / commission Agent F** (red-team) — see Section 10/11.
15. **Resolve "insufficient evidence" license/last-update fields** for the P0 set only (Azure already
    resolved; confirm SWE-bench Verified dataset-card license, RAGBench update date, arXiv/PubMed card licenses).

**Explicitly NOT in 48h:** generating final synthetic traces (out of scope tonight per mission);
running VM/Docker agent harnesses (OSWorld/WebArena/WorkArena); clearing gated datasets (LMSYS-Chat-1M,
GAIA, GPQA) unless a specific signal is needed.

---

## 9. Synthetic augmentation plan (ONLY after benchmark decomposition)

Sequenced to run **after** the Day-1/2 extraction above. The principle (Agent D/E): the 4 real traces
are the **timing backbone**; real payloads are **grafted on**; synthetic fields fill the gaps no public
dataset measures.

**Tier A — arrivals (the #1 missing type; needed by 8/10 classes):**
- Graft arrivals onto payload_only banks using (a) Poisson/Gamma at target QPS (vLLM-style), and
  (b) **trace-driven** replay of Azure Functions 2019 / Azure LLM 2024 inter-arrival distributions to
  get realistic burstiness instead of synthetic smoothness.
- Add diurnal phase-shifts (BurstGPT spans 110 days and contains them; Agent B noted they were not
  measured this run — measure them, or model them).

**Tier B — identity overlays (no public trace carries these except as noted):**
- **Per-tenant SLO tiers** (e.g. free 5s-TTFT vs paid 500ms-TTFT) — none of the production traces carry
  tenant tier (Agent B "open dimensions"). Synthesize tenant assignment per session.
- **Prefix-cache IDs** for non-Mooncake classes — derive from structure (RAGBench doc-set hash,
  RepoBench `repo_name`, conversation prefix) to approximate Mooncake's `hash_ids`.
- **LoRA-adapter IDs** — only GenTD26 has real ones (and it's image); synthesize adapter mixes for
  multi-LoRA routing tests.

**Tier C — stressors / events (deferred dimensions):**
- **Client-side cancellation events** (long-horizon agentic; SWE-agent emits them but they're not in the
  static dataset).
- **Speculative-decoding draft/target affinity** (no public trace records draft-vs-target tokens).
- **Multi-region / cross-DC routing** (WildChat `hashed_ip`+country is the closest real signal; coarse).
- **Tool-call structure grafted onto production timing** — combine BurstGPT/Mooncake arrivals with
  ToolBench/AppWorld per-step structure to make the capstone `production_mixed_enterprise` class.

**Validation requirement:** every synthetic distribution must be labeled (generator + parameters) and,
where it imitates a real one, validated against the source trace's marginal (e.g. token-length CDF vs
Mooncake/BurstGPT). Do not let synthetic and measured fields be indistinguishable in the output schema.

---

## 10. Risks and red-team critique

> **Caveat:** Agent F's deliverable is missing (no `06_`). This section is Agent R's synthesis-time
> red-team from the existing evidence, **not** an independent adversarial pass. Treat as provisional;
> a real Agent F run is the #1 open action.

**R1 — Arrival realism is mostly fiction.** 53/60 sources have no arrivals; 8/10 classes run on
synthesized timing. If the synthetic arrival model is wrong, *every* time-dependent routing conclusion
(burstiness, queueing, SLO) is suspect. **Mitigation:** anchor synthetic arrivals to Azure Functions
2019 / Azure LLM 2024 marginals and report results both with real and synthetic arrivals.

**R2 — Single points of failure for two whole signals.** Prefix-cache realism rests entirely on Mooncake
`hash_ids`; bursty+session realism rests entirely on BurstGPT. If either trace is withdrawn, mis-mapped,
or its remapping (Mooncake's hashes are *remapped*, not raw) doesn't behave like a real cache, the
corresponding routing claims lose their only ground truth. **Mitigation:** treat structurally-inferred
prefix groups (RAGBench/RepoBench) as a cross-check; don't over-fit to one trace.

**R3 — Token counts are mostly estimates.** Outside the native-column traces and ~10 card-stated values,
all token ranges are `ceil(chars/4)` or task-shape reasoning. `chars/4` ≠ BPE for code, math, non-English,
or multimodal. Routing decisions keyed on token *thresholds* (admission, P/D split) could be systematically
off. **Mitigation:** re-tokenize with the actual target tokenizer before fixing thresholds; never ship a
threshold derived from `chars/4`.

**R4 — "Agentic = has a trace" is false.** SWE-bench, WebArena, OSWorld, AgentBench, tau-bench have *tasks*,
not request traces; the multi-turn/tool trace only exists if you run a (possibly non-deterministic, model-
dependent) harness. Traces generated by one model won't generalize to another's routing profile.
**Mitigation:** mark these `synthetic_required`; pin the harness+model; prefer the static-trajectory donors
(ToolBench, AppWorld baseline trajectories) for reproducibility.

**R5 — License/legal landmines in the most-used assets.** ShareGPT (anonymous scrape, ToS risk),
TriviaQA (license "unknown"), MultiNews (non-commercial), arXiv/PubMed/GovReport (no license on the ccdv
cards), several SWE-bench dataset cards (license not shown), GenTD26 (license unknown). The single most
*convenient* payload (ShareGPT) has the weakest provenance. **Mitigation:** for any published benchmark,
prefer CC-BY/Apache/MIT donors (RAGBench, WildChat ODC-BY, MMLU/HumanEval MIT, Mooncake/BurstGPT/Azure);
keep ShareGPT for internal dev only until legal review.

**R6 — Freshness/availability decay.** GSM8K, Big-Bench (archived Apr 2026), HELM (maintenance Jun 2026),
SWE-Lancer (archived Jul 2025) are frozen; ToolBench data lives on Google Drive/Tsinghua Cloud (off-GitHub,
can vanish); 2WikiMultihopQA is Dropbox-only. **Mitigation:** mirror P0/P1 data to a pinned internal store
immediately; record content hashes.

**R7 — Process risk: the committee has gaps.** Agent F never ran; Agent D ran before Agent B (token
estimates unreconciled in D); Agent C could not sample many datasets (HF disconnects, gating) so several
schema entries are "insufficient evidence". The package is solid on *validation* but thin on *adversarial
verification* and *live sampling*. **Mitigation:** Sections 8.13–8.15 (re-run D vs B, run F, resolve P0
"insufficient evidence" fields).

**R8 — Redundancy / overfitting to chat+QA.** The catalog skews to chat and QA/long-context; tool-agent
and browser classes are thinner and harder to extract. A router tuned on the easy classes may underperform
on the agentic ones we under-sampled. **Mitigation:** weight evaluation by class, not by row count.

---

## 11. Open questions for Loki and Liangqi

1. **Agent F (red-team) is missing.** Re-run it, or accept Section 10 as the red-team of record? (Recommend re-run.)
2. **Scope of v1:** ship all 10 classes, or start with the 3 zero/low-synthesis classes
   (`batch_eval_throughput`, `interactive_chat_global` via BurstGPT, `rag_qa_stateless` via RAGBench)?
3. **Real vs synthetic arrivals as the default:** should benchmark headline numbers use trace-driven
   (Azure/BurstGPT) arrivals, synthetic Poisson, or both side-by-side?
4. **ShareGPT legal call:** is the convenient-but-scraped ShareGPT acceptable for a *published* benchmark,
   or restrict to internal dev and use CC-BY/Apache/MIT donors externally?
5. **Tokenizer of record:** which tokenizer fixes the token thresholds (so we can replace all `chars/4`
   estimates)? This blocks any token-threshold routing logic.
6. **Harness + model pin for agentic classes:** which agent harness (SWE-agent, ToolLLaMA/DFSDT, ReAct)
   and which model do we standardize on to make `synthetic_required` traces reproducible?
7. **Multimodal in-scope?** VisualWebArena/OSWorld add an image-token routing axis (Agent E). v1 or later?
8. **Gated datasets:** do we have/obtain credentials for LMSYS-Chat-1M, GAIA, GPQA, WorkArena, OSWorld-v2,
   or skip them for v1 (WildChat already covers the chat class publicly)?
9. **Tenant/SLO tier model:** what tenant tiers + SLO targets should the synthetic overlay encode (this
   is the biggest dimension no public trace provides)?
10. **GenTD26 (image, LoRA IDs):** include as a heterogeneity/LoRA-routing analogy, or out of scope as non-LLM?

---

## Final-decision table (all 60 entries)

Priority: **P0** must use · **P1** likely useful · **P2** maybe · **Drop**.
Mode: direct_trace / payload_only / schema_only / synthetic_required / not_suitable.
(Mode follows Agent D's feasibility class, refined to `synthetic_required` where the request-level trace
only exists by running a harness. Class = Section 7.)

| Benchmark | Priority | Workload class | Trace extraction mode |
|-----------|:--------:|----------------|------------------------|
| Mooncake Trace | P0 | production_mixed_enterprise | direct_trace |
| BurstGPT | P0 | production_mixed_enterprise / interactive_chat_global | direct_trace |
| Azure LLM Inference 2024 | P0 | production_mixed_enterprise | direct_trace |
| Azure LLM Inference 2023 | P0 | production_mixed_enterprise | direct_trace |
| ShareGPT (vLLM source) | P0 | interactive_chat_global | payload_only |
| RAGBench | P0 | rag_qa_stateless | payload_only |
| WildChat | P0 | interactive_chat_global | direct_trace (partial) |
| ToolBench | P0 | workflow_tool_agent | payload_only |
| LongBench v2 | P0 | long_context_extreme_prefill | payload_only |
| SWE-bench Verified | P0 | swe_repo_agent | synthetic_required |
| MMLU | P0 | batch_eval_throughput | payload_only |
| HumanEval | P0 | batch_eval_throughput | payload_only |
| Azure Functions Trace 2019 | P0 (arrival donor) | production_mixed_enterprise (timing only) | not_suitable (repurpose) |
| L-Eval | P1 | long_context_extreme_prefill | payload_only |
| arXiv summarization | P1 | long_doc_summarization_streaming | payload_only |
| PubMed summarization | P1 | long_doc_summarization_streaming | payload_only |
| RepoBench | P1 | strict_slo_autocomplete | payload_only |
| AppWorld | P1 | workflow_tool_agent | payload_only |
| tau-bench | P1 | workflow_tool_agent | synthetic_required |
| GSM8K | P1 | batch_eval_throughput | payload_only |
| MBPP | P1 | batch_eval_throughput | payload_only |
| MATH | P1 | batch_eval_throughput | payload_only |
| MMLU-Pro | P1 | batch_eval_throughput | payload_only |
| LongBench (v1) | P1 | long_context_extreme_prefill | payload_only |
| NarrativeQA | P1 | long_context_extreme_prefill | payload_only |
| Qasper | P1 | rag_qa_stateless | payload_only |
| HotpotQA | P1 | rag_qa_stateless | payload_only |
| SWE-bench | P1 | swe_repo_agent | synthetic_required |
| SWE-bench Pro | P1 | swe_repo_agent | synthetic_required |
| WebArena | P1 | browser_computer_use | synthetic_required |
| BBH (BIG-Bench-Hard) | P1 | batch_eval_throughput | payload_only |
| EleutherAI lm-evaluation-harness | P1 | batch_eval_throughput | payload_only |
| LMSYS-Chat-1M | P2 | interactive_chat_global | payload_only (gated) |
| LMSYS Chatbot Arena Conversations | P2 | interactive_chat_global | direct_trace (partial) |
| MuSiQue | P2 | rag_qa_stateless | payload_only |
| GovReport summarization | P2 | long_doc_summarization_streaming | payload_only |
| BookSum | P2 | long_doc_summarization_streaming | payload_only |
| Natural Questions | P2 | long_context_extreme_prefill | payload_only (145 GB) |
| TriviaQA | P2 | rag_qa_stateless | payload_only (license unknown) |
| LiveCodeBench | P2 | batch_eval_throughput | payload_only |
| BigCodeBench | P2 | batch_eval_throughput | payload_only |
| Big-Bench | P2 | batch_eval_throughput | payload_only (archived) |
| HELM | P2 | batch_eval_throughput | payload_only (maintenance) |
| Terminal-Bench | P2 | swe_repo_agent | synthetic_required |
| VisualWebArena | P2 | browser_computer_use | synthetic_required |
| AgentBench | P2 | workflow_tool_agent | schema_only |
| ShareGPT | P2 | interactive_chat_global | payload_only |
| OpenAssistant | P2 | interactive_chat_global | payload_only |
| UltraChat | P2 | interactive_chat_global | payload_only (synthetic) |
| DevEval | P2 | strict_slo_autocomplete | payload_only |
| Alibaba GenAI GenTD26 | P2 | production_mixed_enterprise (heterogeneity) | direct_trace (non-LLM image) |
| MiniWoB++ | P2 | browser_computer_use | schema_only |
| 2WikiMultihopQA | P2 | rag_qa_stateless | schema_only |
| GAIA | P2 | workflow_tool_agent | schema_only (gated) |
| GPQA | P2 | batch_eval_throughput | schema_only (gated) |
| OSWorld | P2 | browser_computer_use | schema_only (VM) |
| WorkArena | P2 | browser_computer_use | schema_only (gated + live) |
| SWE-Lancer | P2 | swe_repo_agent | schema_only (archived) |
| MultiNews | P2 | long_doc_summarization_streaming | payload_only (non-commercial) |
| BrowserArena | **Drop** | n/a (no class) | not_suitable (404) |

---

## Companion artifacts produced by Agent R
- `sources.json` — 153 unique source URLs merged from all peer sidecars (`{id,label,url,benchmark,cited_by}`).
- `sources.bib` — 53 best-effort BibTeX entries keyed by benchmark (verify before publication).
- `_build_sources_R.py` — the generator (re-run to refresh after peers add sources).

*Every benchmark claim in this report traces to a peer deliverable row and its cited URL (see
`sources.json`). Uncertainty is labeled "insufficient evidence"; estimates are labeled ESTIMATE.
The one unverified structural gap — the missing Agent F red-team — is flagged in Sections 10–11.*


---

## 12. MEASURED DATA ADDENDUM (post-committee, real payloads + traces)

*Added after the committee run: the team's token ranges were mostly estimates. This addendum replaces
estimates with MEASURED distributions from actual payloads (tiktoken cl100k) and real production traces.*

### 12.1 Coverage
- **25 benchmarks** tokenized from real payloads → `02b_measured_token_distributions.csv`
- **3 chat/agent datasets** profiled (gated, via HF token): WildChat-1M `02c`, LMSYS-Chat-1M `02d`, GAIA `02e`
- **WildChat-1M arrival process** extracted from real timestamps → `02f` (the only chat dataset with arrivals)
- **6 production traces** downloaded + measured → `02g` (the direct-trace gold standard)

### 12.2 The 7 real arrival traces (the scarce resource, now measured)
| trace | n requests | input P50 | output P50 | special signal |
|---|--:|--:|--:|---|
| WildChat-1M | 237k | 19 (msg) | 275 | timestamps + tenant IP + 25d window |
| Azure-LLM-conv-2023 | 19,366 | 1020 | 129 | real arrivals, balanced |
| Azure-LLM-code-2023 | 8,819 | 1469 | 13 | autocomplete: prefill-heavy, Fano/s=13.2 |
| Azure-LMM-multimodal-2024 | 1,000,000 | 1124 | 98 | 50% carry images |
| BurstGPT | 1,404,294 | 262 | 36 | ChatGPT+GPT-4 mix, Fano/s=2.0 |
| Mooncake-conversation | 12,031 | 6909 | 350 | prefix hit-ratio 0.366 |
| Mooncake-toolagent | 23,608 | 6346 | 30 | prefix hit-ratio 0.553 (tool loop) |

### 12.3 What changed vs the committee's estimates
- **Estimates were directionally right but imprecise.** E.g. GSM8K input est 50-200 → measured P50=54/P99=123;
  LongBench-narrativeqa est 5-30k → measured P50=31k/max=65k (the long tail was under-counted).
- **Prefix reuse is now MEASURED, not assumed.** Mooncake conv 36.6% / tool 55.3% block-reuse — the committee
  marked many benchmarks 'prefix_reuse=high' by inference; only Mooncake actually proves it from hash_ids.
- **Arrivals are no longer hypothetical.** WildChat + Azure + BurstGPT give measured inter-arrival + burstiness
  (Fano 1.3-13.2) + diurnal — the benchmark's arrival process is now evidence-grounded.

### 12.4 Updated build recipe (measured-data-first)
1. **Arrivals:** replay WildChat (chat), Azure-code (autocomplete), Azure-MM (multimodal), Mooncake (prefix/tool), BurstGPT (scale). No synthetic arrival process needed for these classes.
2. **Tokens:** draw per-request input/output from the measured 02b/02g distributions for the matching class.
3. **Prefix/KV:** use Mooncake hash_ids directly for prefix-reuse routing; for others, the 02b shapes + WildChat session model.
4. **Still synthetic (justified):** tool-call LOOP timing (GAIA/agent), cross-tenant multiplexing at scale, P/D-disaggregation labels, LoRA/adapter ids, cancellation. See §9.

*Artifacts: `02b`–`02g` (+ `02f_wildchat_arrival.png`, `02g_workload_landscape.png`). Harnesses in `tools/token_measure/`.*