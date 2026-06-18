# AGENT E — Canonical Workload Taxonomy Builder

ROLE: Synthesize Agents A–D into the FIRST HHRouting-Bench workload taxonomy: 6–10 canonical workload classes.

DEPENDENCY: read 01_, 02_, 03_, 04_ deliverables if present. Ground every class in real benchmarks.

Suggested classes (refine/merge/justify — do not blindly accept): interactive_chat_global,
rag_qa_stateless, swe_agent_batch, repo_debugging_agent, workflow_tool_agent, browser_computer_use_text,
browser_computer_use_multimodal, strict_slo_autocomplete, deep_research_long_horizon,
production_mixed_enterprise.

For EACH class define: inspired_by_benchmarks (cite which, with URLs); request shape distribution;
input token distribution; output token distribution; arrival pattern; concurrency pattern; SLO class;
prefill pressure; decode residency; KV lifetime; prefix reuse potential; session affinity requirement;
expected routing difficulty; likely router failure mode; whether real traces exist; whether synthetic
augmentation is required; minimal first-version implementation (one concrete sentence).

CRITICAL: Do NOT invent exact distributions unless supported by a cited source. If unsupported, use
QUALITATIVE ranges and mark them ESTIMATED.

DELIVERABLES:
1. `05_canonical_workload_taxonomy.md` — full per-class definitions with citations.
2. `05_canonical_workload_taxonomy.csv`
   HEADER (exact): class,inspired_by_benchmarks,input_token_dist,output_token_dist,arrival_pattern,concurrency_pattern,slo_class,prefill_pressure,decode_residency,kv_lifetime,prefix_reuse,session_affinity,routing_difficulty,likely_failure_mode,real_traces_exist,synthetic_required,min_first_impl
