# AGENT D — Trace Feasibility Analyst

ROLE: Determine which benchmarks can become REQUEST-LEVEL TRACES and which require synthetic augmentation.

DEPENDENCY: read `01_benchmark_validation_table.csv` (A), `02_workload_decomposition.csv` (B), and
`03_payload_schema_inventory.md` (C) if present.

Classify each benchmark's trace feasibility:
- direct_trace: has timestamps AND input/output token counts or request logs.
- payload_only: has prompt/output/task data but NO realistic arrival times.
- schema_only: has task structure but payload extraction is hard.
- not_suitable: cannot reasonably support routing workload decomposition.

For each benchmark, list what must be ADDED later (synthetic_fields_needed), choosing from: arrival
timestamps, concurrency model, output length model, SLO class, tenant ID, session ID, LoRA adapter ID,
prefix ID, API latency, cancellation probability, priority tier, heterogeneity label, P/D routing annotations.

Also: estimated_effort (low/med/high), suitability_rank (1=best), notes, source_urls.

DELIVERABLES:
1. `04_trace_feasibility_matrix.csv`
   HEADER (exact): benchmark_name,feasibility_class,direct_arrivals_available,input_available,output_available,session_available,tool_calls_available,timestamp_available,synthetic_fields_needed,estimated_effort,suitability_rank,notes,source_urls
2. `04_trace_feasibility_summary.md` — narrative: which are direct traces (rare, precious), which are
   payload-only (most), which are schema-only, which to drop; and the single most important missing data type.
