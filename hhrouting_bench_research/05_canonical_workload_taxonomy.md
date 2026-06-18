# 05 — Canonical Workload Taxonomy (Agent E)

Scope: **serving-routing mechanics only** (arrivals, input/output token length, KV-cache
lifetime, prefix reuse, session/tenant identity, tool-call loops, SLO regime).
**Not** model accuracy. This is the first HHRouting-Bench workload taxonomy: **10 canonical
workload classes** synthesized from the validated peer evidence packages.

## Inputs read (dependencies)
- `01_benchmark_validation_table.csv` + `01b_production_traces.md` (Agent A) — 57 validated
  benchmarks + production serving traces, each with source URLs.
- `02_workload_decomposition.csv` + `02_workload_decomposition_notes.md` (Agent B) — per-benchmark
  routing-dimension decomposition with MEASURED vs ESTIMATE labels and estimation method.
- `03_payload_schema_inventory.md` + `03_sample_payloads.jsonl` + `03_sampling_blockers.md`
  (Agent C) — concrete field maps and access blockers.
- `04_trace_feasibility_matrix.csv` + `04_trace_feasibility_summary.md` (Agent D) — direct_trace /
  payload_only / schema_only / not_suitable classification (7 / 43 / 8 / 2 of 60 rows).

## Evidence-discipline rules carried into this taxonomy
- Every class is **grounded in named benchmarks with URLs**. No class is invented from
  intuition.
- Token distributions are **qualitative + labeled ranges**. A range is `MEASURED` only when a
  dataset card / paper / sample row states it (copied from Agent B); otherwise it is `ESTIMATE`
  (reasoned from task shape per Agent B's method table). Production-trace ranges are
  `varies-MEASURED` (the trace ships per-request integer token columns; the *distribution* is in
  the data, not numerically summarized in this run).
- `real_traces_exist` answers: *does a public source ship real per-request arrival timestamps +
  token counts for this class?* Per Agent D, only **4 of 60** sources are unambiguous arrival
  traces (Mooncake, BurstGPT, Azure 2023, Azure 2024); 2 more are partial (LMSYS Arena, WildChat).
- `synthetic_required` answers: *must we synthesize fields (arrivals, tenant tier, SLO class,
  tool structure) to make this class routable?* For 53 of 60 sources the **arrival process is
  entirely absent** and must be synthesized (Agent D, §"single most important missing data type").

## Coverage check (which routing axes each class stresses)
| Routing axis | Best-covered by class(es) |
|---|---|
| Extreme prefill / TTFT | `long_context_extreme_prefill`, `long_doc_summarization_streaming` |
| Decode residency / TPOT | `long_doc_summarization_streaming`, `batch_eval_throughput` (CoT) |
| Prefix / KV-cache reuse | `rag_qa_stateless`, `strict_slo_autocomplete`, `production_mixed_enterprise` (Mooncake `hash_ids`) |
| Session affinity | `interactive_chat_global`, `workflow_tool_agent`, `production_mixed_enterprise` (BurstGPT `Session ID`) |
| Multi-turn context growth | `swe_repo_agent`, `workflow_tool_agent`, `browser_computer_use` |
| Tool-call loops | `workflow_tool_agent`, `swe_repo_agent`, `browser_computer_use` |
| Arrival burstiness | `interactive_chat_global`, `production_mixed_enterprise` (Azure / BurstGPT) |
| Max-concurrency throughput | `batch_eval_throughput` |
| Heterogeneous tenant mix | `production_mixed_enterprise` |
| Image-token-aware routing | `browser_computer_use` (multimodal variant) |

---

## Class 1 — `interactive_chat_global`
**Inspired by (cited):** WildChat-1M (https://huggingface.co/datasets/allenai/WildChat-1M),
LMSYS-Chat-1M (https://huggingface.co/datasets/lmsys/lmsys-chat-1m),
BurstGPT (https://github.com/HPMLL/BurstGPT),
Azure LLM Inference Trace 2023/2024 (https://github.com/Azure/AzurePublicDataset),
LMSYS Chatbot Arena Conversations (https://huggingface.co/datasets/lmsys/chatbot_arena_conversations),
ShareGPT (https://huggingface.co/datasets/anon8231489123/ShareGPT_Vicuna_unfiltered).

- **Request shape:** many short-to-medium human turns; conversation grows monotonically across turns.
- **Input token dist:** 30–2500 (WildChat MEASURED-short-sample ~25–30 tok extrapolated; LMSYS 50–2000 ESTIMATE; Azure/BurstGPT `varies-MEASURED`).
- **Output token dist:** 30–2500 (ESTIMATE for chat datasets; `varies-MEASURED` for BurstGPT `Response tokens` / Azure `GeneratedTokens`).
- **Arrival pattern:** interactive / bursty — Azure & BurstGPT are real bursty production arrivals (MEASURED, KDD25 burstiness focus); chat datasets without timestamps need synthesized arrivals.
- **Concurrency:** high (small per-request footprint → many in-flight).
- **SLO class:** strict-TTFT (human waits for first token).
- **Prefill pressure:** medium. **Decode residency:** medium. **KV lifetime:** session-persistent (WildChat `conversation_hash` + per-turn timestamps; BurstGPT `Session ID`) — KV reuse spans hours–days.
- **Prefix reuse:** high (turn-over-turn conversation prefix). **Session affinity:** required (sticky routing per `Session ID` / `conversation_hash`).
- **Routing difficulty:** high — must balance burst absorption against session stickiness.
- **Likely failure mode:** head-of-line-blocking, session-affinity-failure, kv-cache-pressure.
- **Real traces exist:** YES — BurstGPT + Azure 2023/2024 (token+arrival; no text), partial for LMSYS Arena / WildChat (conversation/response timestamps, not request-arrival; tokens by re-tokenizing — ESTIMATE).
- **Synthetic required:** PARTIAL — arrivals real, but per-tenant SLO tier and prompt text (Azure is GDPR-stripped) must be synthesized.
- **Min first impl:** Replay BurstGPT (`Timestamp`+`Session ID`+`Request/Response tokens`) as the arrival+session backbone, attaching WildChat text payloads to matching token lengths for sticky-session routing tests.

## Class 2 — `rag_qa_stateless`
**Inspired by (cited):** RAGBench (https://huggingface.co/datasets/rungalileo/ragbench),
HotpotQA (https://huggingface.co/datasets/hotpotqa/hotpot_qa),
MuSiQue (https://github.com/StonyBrookNLP/musique),
Qasper (https://huggingface.co/datasets/allenai/qasper),
TriviaQA (https://huggingface.co/datasets/mandarjoshi/trivia_qa),
2WikiMultihopQA (https://github.com/Alab-NII/2wikimultihop).

- **Request shape:** question + N retrieved passages → short extractive/free-form answer; single-shot (no session).
- **Input token dist:** 500–5000 ESTIMATE (question + 4–20 passages; RAGBench=4 docs, MuSiQue=20 paragraphs, HotpotQA=10 distractors).
- **Output token dist:** 5–500 (RAGBench `response` 50–500 MEASURED; HotpotQA answer 5–50 MEASURED — short).
- **Arrival pattern:** batch (synthesized Poisson — no native timestamps).
- **Concurrency:** high. **SLO class:** strict-TTFT (user waits on answer).
- **Prefill pressure:** medium. **Decode residency:** low. **KV lifetime:** short (single-shot).
- **Prefix reuse:** high — same documents reused across questions (RAGBench shared docs, HotpotQA shared distractor passages, Qasper same paper across multiple questions). This is the **strongest catalog candidate for prefix-cache-aware routing** (Agent B/D).
- **Session affinity:** none. **Routing difficulty:** medium.
- **Likely failure mode:** prefix-cache-miss-penalty, decode-backlog-overload.
- **Real traces exist:** NO (payload_only — no arrivals).
- **Synthetic required:** YES (arrival process). Prefix structure is real (shared docs), arrivals are not.
- **Min first impl:** Load RAGBench question+4-document rows, hash the document set to assign prefix-cache groups, fire under a synthesized Poisson arrival to test prefix-aware vs prefix-blind routing.

## Class 3 — `long_context_extreme_prefill`
**Inspired by (cited):** LongBench v2 (https://huggingface.co/datasets/THUDM/LongBench-v2,
https://arxiv.org/abs/2412.15204), LongBench (https://huggingface.co/datasets/THUDM/LongBench),
L-Eval (https://github.com/OpenLMLab/LEval), NarrativeQA (https://huggingface.co/datasets/deepmind/narrativeqa),
Natural Questions (https://huggingface.co/datasets/google-research-datasets/natural_questions).

- **Request shape:** one very large context (book / full paper / full Wikipedia page / up-to-2M-word doc) + tiny query → micro answer (often a single MCQ letter). Single-shot.
- **Input token dist:** 5,000–2,000,000 MEASURED (LongBench avg 5k–15k words, LSHT 22,337; L-Eval 3k–200k tok; NarrativeQA ~41k tok; LongBench v2 up to 2M words; NQ full Wikipedia page).
- **Output token dist:** 1–1000 — micro for MCQ (LongBench v2 answer = 1 letter MEASURED), short for QA (5–50 MEASURED).
- **Arrival pattern:** batch (synthesized). **Concurrency:** low — each request is a per-request memory hog.
- **SLO class:** strict-TTFT (TTFT fully dominated by the massive prefill).
- **Prefill pressure:** extreme. **Decode residency:** low. **KV lifetime:** short. **Prefix reuse:** low. **Session affinity:** none.
- **Routing difficulty:** high — single requests can exceed a node's KV budget; the router must do admission control / length-aware placement.
- **Likely failure mode:** OOM, prefill-starvation-of-decode.
- **Real traces exist:** NO.
- **Synthetic required:** YES (arrivals). Context lengths are real/MEASURED.
- **Min first impl:** Stream LongBench-v2 + L-Eval contexts (bucketed by token length: <32k / 32k–128k / >128k) through a synthesized arrival generator to test length-aware admission and OOM-avoidance routing.

## Class 4 — `long_doc_summarization_streaming`
**Inspired by (cited):** arXiv summarization (https://huggingface.co/datasets/ccdv/arxiv-summarization),
PubMed summarization (https://huggingface.co/datasets/ccdv/pubmed-summarization),
GovReport (https://huggingface.co/datasets/ccdv/govreport-summarization),
MultiNews (https://huggingface.co/datasets/alexfabbri/multi_news),
BookSum (https://huggingface.co/datasets/kmfoda/booksum).

- **Request shape:** long input document → multi-paragraph generated summary; user reads output as it streams.
- **Input token dist:** 2,000–100,000 (arXiv ~6038 ws-tok MEASURED; PubMed ~3043 ws-tok MEASURED; GovReport 7k–30k ESTIMATE; BookSum up to ~100k ESTIMATE).
- **Output token dist:** 100–3000 (arXiv ~299 ws-tok MEASURED; PubMed ~215 MEASURED; GovReport 500–2000, BookSum 500–3000 ESTIMATE) — **the distinguishing axis: meaningfully long decode.**
- **Arrival pattern:** batch (synthesized). **Concurrency:** low–medium (large prefill limits in-flight count).
- **SLO class:** strict-TPOT (users read the summary as it generates → inter-token latency matters more than TTFT).
- **Prefill pressure:** high–extreme. **Decode residency:** medium–high. **KV lifetime:** short. **Prefix reuse:** low (BookSum: medium, chapter-level reuse). **Session affinity:** none.
- **Routing difficulty:** high — simultaneous heavy prefill AND sustained decode; classic chunked-prefill scheduler / disaggregated P-D stress.
- **Likely failure mode:** prefill-starvation-of-decode, decode-backlog-overload, OOM (GovReport/BookSum).
- **Real traces exist:** NO. **Synthetic required:** YES (arrivals).
- **Min first impl:** Replay arXiv/PubMed (input+target lengths MEASURED) under synthesized arrivals with a TPOT SLO, to test whether the router co-schedules long-decode jobs without starving them behind new prefills.

## Class 5 — `strict_slo_autocomplete`
**Inspired by (cited):** RepoBench (https://huggingface.co/datasets/tianyang/repobench-c),
DevEval (https://github.com/seketeam/DevEval).

- **Request shape:** large retrieved repo/file context → tiny next-line / completion output; latency-critical (IDE keystroke loop).
- **Input token dist:** 2,000–16,000 ESTIMATE (retrieved repo context; RepoBench ships `context` list w/ path/snippet/tokenized_snippet + `import_statement`).
- **Output token dist:** 10–150 MEASURED (RepoBench next-line target) — tiny decode.
- **Arrival pattern:** interactive/steady (synthesized — IDE keystroke cadence; no native timestamps). **Concurrency:** high.
- **SLO class:** strict-TPOT / strict-TTFT (IDE: the whole completion must return in tens of ms).
- **Prefill pressure:** high. **Decode residency:** low (tiny). **KV lifetime:** short per request, but session-like at the file/repo level. **Prefix reuse:** high — same `repo_name` across rows enables prefix-cache hits. **Session affinity:** medium (per-repo/per-IDE-session stickiness improves cache hit rate).
- **Routing difficulty:** high — extreme prefill-to-decode ratio (~50:1) under the tightest latency budget; cache locality is decisive.
- **Likely failure mode:** prefill-starvation-of-decode, prefix-cache-miss-penalty.
- **Real traces exist:** NO. **Synthetic required:** YES (arrivals + IDE-session model).
- **Min first impl:** Group RepoBench rows by `repo_name`, route same-repo completions to the same node under a synthesized high-rate arrival, and measure prefix-cache hit rate vs round-robin.

## Class 6 — `swe_repo_agent`
**Inspired by (cited):** SWE-bench / SWE-bench Verified / SWE-bench Pro
(https://huggingface.co/datasets/princeton-nlp/SWE-bench,
https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified),
SWE-Lancer (https://github.com/openai/SWELancer-Benchmark).

- **Request shape:** GitHub-issue task driven by an agent harness (SWE-agent) over a large repo prefix; many tool-call turns; KV grows monotonically across the whole task.
- **Input token dist:** 2,000–50,000 ESTIMATE (repo+issue context; SWE-bench Pro `problem_statement` 419–8.04k chars MEASURED + repo context).
- **Output token dist:** 100–3000 ESTIMATE (patch / per-step actions).
- **Arrival pattern:** batch (harness fires the task set). **Concurrency:** batch-synchronized.
- **SLO class:** relaxed (long-horizon background job).
- **Prefill pressure:** high (SWE-bench Pro: extreme). **Decode residency:** medium. **KV lifetime:** long (agentic session — KV held for the full multi-step task). **Prefix reuse:** high (repo prefix reused every turn). **Session affinity:** required at task granularity (multi_turn growth = large). **Tool calls:** high.
- **Routing difficulty:** high — the long-lived growing KV must stay co-located for the whole task; evicting mid-task is catastrophic.
- **Likely failure mode:** kv-cache-pressure, prefill-starvation-of-decode, unfair-tenant-starvation, cancellation-waste.
- **Real traces exist:** NO — the static dataset has tasks, not request traces; a harness must generate the multi-turn trace.
- **Synthetic required:** YES (harness-generated multi-turn trace + arrivals). Use SWE-bench Verified (500 deterministic tasks) for reproducibility.
- **Min first impl:** Run SWE-agent on SWE-bench Verified, log each turn's (input_len, output_len, task_id) to produce per-task monotonic-KV traces; route by `task_id` stickiness.

## Class 7 — `workflow_tool_agent`
**Inspired by (cited):** ToolBench (https://github.com/OpenBMB/ToolBench),
AppWorld (https://huggingface.co/datasets/LukaszTP/AppWorld-Tasks, https://github.com/StonyBrookNLP/appworld),
tau-bench (https://github.com/sierra-research/tau-bench),
AgentBench (https://github.com/THUDM/AgentBench).

- **Request shape:** ReAct / DFSDT tool-call loop — repeated (Thought → Action → Observation) turns against external APIs; multi-turn context growth.
- **Input token dist:** 500–5000 ESTIMATE per step (query + api_list). **Output token dist:** 100–2000 ESTIMATE per step (action/thought).
- **Arrival pattern:** batch; tau-bench is interactive (user-simulator LLM in the loop). **Concurrency:** medium.
- **SLO class:** relaxed (tau-bench: strict-TTFT inside the user-sim loop).
- **Prefill pressure:** medium. **Decode residency:** medium (AppWorld: high). **KV lifetime:** long (loop spans many steps). **Prefix reuse:** medium (shared `api_list` per tool family). **Session affinity:** required (the loop is one logical session). **Tool calls:** high (ToolBench 469,585 real API calls MEASURED; AppWorld `num_api_calls` 30–101 MEASURED in Agent C samples).
- **Routing difficulty:** high — interlocked LLM-LLM loops (tau-bench) and long tool chains create complex concurrency + cancellation dynamics.
- **Likely failure mode:** session-affinity-failure, cancellation-waste, kv-cache-pressure.
- **Real traces exist:** PARTIAL — ToolBench ships 120k+ static DFSDT solution paths with Action/Thought/Observation nodes (replayable step structure, Agent C), AppWorld ships downloadable ReAct trajectories; but **no real arrival timestamps**.
- **Synthetic required:** YES (arrivals). Per-step structure is real and replayable.
- **Min first impl:** Replay ToolBench DFSDT trajectories as fixed per-step token sequences under a synthesized arrival process, routing each solution-path's steps to the same node to test session-sticky tool-loop routing.

## Class 8 — `browser_computer_use`
**Inspired by (cited):** WebArena (https://github.com/web-arena-x/webarena) [text DOM/AX-tree],
VisualWebArena (https://github.com/web-arena-x/visualwebarena) [multimodal],
OSWorld (https://github.com/xlang-ai/OSWorld) [multimodal, VM],
WorkArena (https://github.com/ServiceNow/WorkArena) [gated, live ServiceNow].

- **Request shape:** per-step the agent observes a large page/screen state (DOM, accessibility tree, or screenshot+a11y) and emits one tiny action (click/type). Long multi-step episodes.
- **Input token dist:** 1,000–15,000 ESTIMATE per step (WebArena DOM/AX-tree 1k–8k; OSWorld screenshot+a11y 2k–15k; VisualWebArena adds image tokens). **Output token dist:** 50–500 ESTIMATE per action — tiny.
- **Arrival pattern:** batch (harness). **Concurrency:** low for OSWorld (per-VM-bound); medium for WebArena text.
- **SLO class:** strict-TTFT per browser step (WebArena) / relaxed (OSWorld background).
- **Prefill pressure:** high (OSWorld: extreme). **Decode residency:** low. **KV lifetime:** long (episode). **Prefix reuse:** medium (page DOMs / repeated screens reuse). **Session affinity:** required (episode = session). **Tool calls:** high.
- **Multimodal variant (VisualWebArena, OSWorld):** image tokens are a **distinct routing axis** — image-token-aware placement and multimodal-encoder co-location; this variant raises a separate OOM/throughput profile from the text-only DOM variant.
- **Routing difficulty:** high — huge per-step prefill vs micro action (~10:1) plus VM/episode stickiness.
- **Likely failure mode:** prefill-starvation-of-decode, kv-cache-pressure, OOM (multimodal/OSWorld), session-affinity-failure.
- **Real traces exist:** NO (schema_only — live env / VM / Docker fleet required; WorkArena gated). WebArena ships 170 human Playwright recordings and VisualWebArena 233 human recordings (structure, not arrival traces).
- **Synthetic required:** YES (arrivals + harness/VM to produce per-step traces).
- **Min first impl:** Start with WebArena text (no VM image cost): generate per-step (DOM_len, action_len, episode_id) traces from the raw prompt observations, route by `episode_id`; add the multimodal variant later with a separate image-token length channel.

## Class 9 — `batch_eval_throughput`
**Inspired by (cited):** MMLU (https://huggingface.co/datasets/cais/mmlu),
MMLU-Pro (https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro),
GSM8K (https://huggingface.co/datasets/openai/gsm8k),
MATH (https://huggingface.co/datasets/HuggingFaceH4/MATH-500),
HumanEval (https://github.com/openai/human-eval),
MBPP (https://huggingface.co/datasets/google-research-datasets/mbpp),
BBH (https://huggingface.co/datasets/lukaemon/bbh),
Big-Bench (https://github.com/google/BIG-bench),
HELM (https://github.com/stanford-crfm/helm),
EleutherAI lm-evaluation-harness (https://github.com/EleutherAI/lm-evaluation-harness),
LiveCodeBench (https://github.com/LiveCodeBench/LiveCodeBench),
BigCodeBench (https://huggingface.co/datasets/bigcode/bigcodebench).

- **Request shape:** short single-shot prompt (MCQ stem, word problem, function spec) → short answer or CoT; thousands fired together.
- **Input token dist:** 30–2000 ESTIMATE (MMLU 50–500; HumanEval 50–300 MEASURED; MBPP 30–200 MEASURED; GSM8K 50–200 MEASURED). **Output token dist:** 1–1500 (MCQ letter 1–5; CoT 100–1500 ESTIMATE — MATH/MMLU-Pro/GSM8K).
- **Arrival pattern:** batch (all requests fired at start — this is the **native** pattern, not a synthesis gap). **Concurrency:** high / batch-synchronized.
- **SLO class:** background (no interactive latency budget).
- **Prefill pressure:** low. **Decode residency:** low (medium for CoT). **KV lifetime:** short. **Prefix reuse:** low (BBH: medium — shared CoT exemplar prefix). **Session affinity:** none. **Tool calls:** none.
- **Routing difficulty:** low-to-medium — the throughput/QPS stressor; tests max-concurrency batching and fairness across heterogeneous sub-benchmarks.
- **Likely failure mode:** decode-backlog-overload, unfair-tenant-starvation (HELM heterogeneous mix).
- **Real traces exist:** NO (synchronized batch, not an arrival trace) — but batch IS a legitimate native pattern for this class.
- **Synthetic required:** NO for pure throughput (run as native batch); PARTIAL if staggered/Poisson arrivals are desired.
- **Min first impl:** Fire MMLU + GSM8K + HumanEval as one max-concurrency batch (mix short-decode MCQ with longer-decode CoT) to measure throughput and decode-backlog fairness under saturation.

## Class 10 — `production_mixed_enterprise`
**Inspired by (cited):** Mooncake Trace (https://github.com/kvcache-ai/Mooncake),
BurstGPT (https://github.com/HPMLL/BurstGPT),
Azure LLM Inference Trace 2023/2024 (https://github.com/Azure/AzurePublicDataset),
Azure Functions Trace 2019 (https://github.com/Azure/AzurePublicDataset/blob/master/AzureFunctionsDataset2019.md) [arrival donor],
Alibaba GenAI GenTD26 (https://github.com/alibaba/clusterdata/tree/master/cluster-trace-v2026-GenAI) [LoRA adapter IDs].

- **Request shape:** the integration / replay class — a realistic heterogeneous mix of the classes
  above grafted onto a **real production arrival backbone**, with multiple tenants/SLO tiers.
- **Input/Output token dist:** `varies-MEASURED` (Mooncake `input_length`/`output_length`; BurstGPT `Request/Response tokens`; Azure `ContextTokens`/`GeneratedTokens` — all native per-request integer columns).
- **Arrival pattern:** bursty (real production — Azure 2023/2024, BurstGPT KDD25 burstiness; Azure Functions 2019 as the community-standard burstiness donor). **Concurrency:** high.
- **SLO class:** mixed / heterogeneous (per-tenant tiers — must be synthesized; no public trace carries tenant tier).
- **Prefill pressure:** varies (high tail). **Decode residency:** varies. **KV lifetime:** mixed — session-persistent (BurstGPT `Session ID`), short (Azure). **Prefix reuse:** high — **Mooncake `hash_ids` is the only public trace with explicit per-request prefix-cache block hashes (~50% hit ratio).** **Session affinity:** required (BurstGPT `Session ID`). **Tool calls:** none natively (must be grafted from Classes 6–8).
- **Routing difficulty:** highest — every pressure at once: burst absorption + session stickiness + prefix-cache awareness + tenant fairness.
- **Likely failure mode:** head-of-line-blocking, tail-latency-explosion, unfair-tenant-starvation, prefix-cache-miss-penalty, session-affinity-failure.
- **Real traces exist:** YES — 4 real arrival traces form the backbone (Mooncake, BurstGPT, Azure 2023, Azure 2024).
- **Synthetic required:** YES — overlay tenant tiers, per-tier SLO classes, and tool-call structure (none present in production traces; Agent B §"Open routing dimensions").
- **Min first impl:** Replay BurstGPT (arrivals+sessions) and Mooncake (arrivals+prefix `hash_ids`) as two backbones; assign synthetic tenant tiers + SLO classes per session, then evaluate a router that must jointly honor stickiness, prefix-cache locality, and tenant fairness.

---

## Cross-cutting notes & honest limitations
1. **The arrival process is the scarce resource.** 53 of 60 catalog sources have NO arrival
   timestamps (Agent D). 8 of 10 classes here are marked `synthetic_required = YES` *because of
   arrivals*, even when their payloads/token-lengths are real. Only Classes 1 and 10 inherit real
   arrivals (from BurstGPT/Azure/Mooncake).
2. **Only one real prefix-cache signal exists.** Mooncake `hash_ids` is the sole public per-request
   prefix-hash trace (Agent B obs #1). Every other `prefix_reuse = high` is *structurally inferred*
   (shared docs / repos / conversation prefixes), not measured at the cache-block level.
3. **Only one real bursty+session trace exists.** BurstGPT (`Session ID` + bursty arrivals over
   ~110 days) is unique (Agent B obs #2).
4. **Production traces lack tool structure.** Tool-call realism (Classes 6–8) must come from the
   agent benchmarks; production traces contribute timing, not per-step structure (Agent B obs #3).
5. **Token ranges are mostly ESTIMATE.** Per Agent B/C, exact serving token counts exist only for
   the native-column traces (Mooncake/BurstGPT/Azure) and a handful of MEASURED card values
   (LongBench, L-Eval, NarrativeQA, arXiv/PubMed, RAGBench/HotpotQA answers, HumanEval/MBPP/GSM8K
   inputs, AppWorld `num_api_calls`). All per-step agentic ranges are reasoned from task shape.
6. **Reproducibility risk carried forward.** Archived/maintenance repos (GSM8K, Big-Bench, HELM,
   SWE-Lancer) remain fetchable but frozen (Agent B obs #7). BrowserArena (404) is **excluded** —
   it backs no class (Agent A/D). Gated sources (LMSYS, GAIA, GPQA, WorkArena, OSWorld) raise the
   `synthetic_required` / access cost of any class drawing on them.
7. **Dimensions no public dataset measures** (deferred to the synthetic-trace layer, Agent B):
   per-tenant SLO heterogeneity, speculative-decoding draft affinity, client-side cancellation
   events, multi-region routing. Class 10 is where these synthetic overlays land.

## Suggested first-version build order (cheapest → richest)
1. `batch_eval_throughput` — runs as native batch today, zero synthesis (MMLU+GSM8K+HumanEval).
2. `interactive_chat_global` — replay BurstGPT backbone + WildChat payloads (real arrivals+sessions).
3. `rag_qa_stateless` — RAGBench + synthesized Poisson (real prefix structure).
4. `long_context_extreme_prefill` + `long_doc_summarization_streaming` — length-bucketed payloads + synthesized arrivals.
5. `strict_slo_autocomplete` — RepoBench grouped by repo + synthesized IDE cadence.
6. `workflow_tool_agent` — replay ToolBench DFSDT static trajectories + synthesized arrivals.
7. `swe_repo_agent`, `browser_computer_use` — require running a harness/VM; build last.
8. `production_mixed_enterprise` — the capstone integration once Classes 1–9 payload banks exist.
