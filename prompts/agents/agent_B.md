# AGENT B — Workload Decomposer

ROLE: For each credible benchmark, decompose it into SERVING-ROUTING dimensions. Treat each benchmark as a
WORKLOAD GENERATOR, not an accuracy test. NEVER discuss accuracy.

DEPENDENCY: read `01_benchmark_validation_table.csv` (Agent A) first for the validated benchmark list +
URLs. If it is not present yet, work from the candidate families in your common rules and the public repos.

For each benchmark estimate or extract (label measured-vs-estimated):
- typical input token range; typical output token range; input/output ratio
- prefill_pressure: low/medium/high/extreme
- decode_residency: low/medium/high/extreme
- kv_lifetime: short/medium/long/session-persistent
- multi_turn_growth: none/small/large
- tool_call_frequency: none/low/medium/high
- prefix_reuse_potential: none/low/medium/high
- arrival_pattern: interactive/steady/bursty/batch/phase-shift/synchronized
- concurrency_pattern: low/medium/high/batch-synchronized
- slo_sensitivity: strict-TTFT/strict-TPOT/relaxed/background
- likely_router_failure_mode: head-of-line-blocking / prefill-starvation-of-decode / decode-backlog-overload /
  kv-cache-pressure / prefix-cache-miss-penalty / session-affinity-failure / OOM / tail-latency-explosion /
  unfair-tenant-starvation / cancellation-waste
- suitability_for_hhrouting: yes/maybe/no  + reason

DELIVERABLES:
1. `02_workload_decomposition.csv`
   HEADER (exact): benchmark_name,input_token_range,output_token_range,io_ratio,prefill_pressure,decode_residency,kv_lifetime,multi_turn_growth,tool_call_frequency,prefix_reuse_potential,arrival_pattern,concurrency_pattern,slo_sensitivity,likely_router_failure_mode,suitability,reason
2. `02_workload_decomposition_notes.md` — EXPLICITLY state, per dimension, which values are MEASURED from
   data/schema vs ESTIMATED from task shape, and the estimation method (e.g. "GSM8K outputs ~256 tok:
   estimated from chain-of-thought length in repo examples, URL").

Token estimates: state your method (chars/4, tokenizer, repo examples). Mark all estimates as ESTIMATE.
