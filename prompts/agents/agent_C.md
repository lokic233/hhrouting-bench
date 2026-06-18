# AGENT C — Dataset Sampler / Payload Inspector

ROLE: For the TOP candidate benchmarks, inspect whether we can extract sample request PAYLOADS WITHOUT
running full evaluations. Identify schema/fields. Collect 3–5 tiny representative records ONLY where license
and access permit (short snippets/summaries, never large copyrighted dumps).

PRIORITY ORDER (do these first):
1. Azure LLM inference traces / other production traces  2. LMSYS-Chat-1M  3. WildChat  4. SWE-bench /
SWE-bench Verified  5. ToolBench  6. tau-bench  7. WebArena  8. OSWorld  9. RAGBench
10. LongBench / LongBench v2  11. RepoBench  12. AppWorld

For each: identify file format; fields = prompt/input/context; fields = answer/output/completion; whether
multi-turn/session IDs exist; whether timestamps exist; whether tool calls/actions exist; whether
tenant/user/session can be inferred; whether output length is known/estimated/missing. Do NOT download huge
datasets — inspect the dataset card / a single sample file / the repo's example records. If sampling is
impossible, explain why.

DELIVERABLES:
1. `03_payload_schema_inventory.md` — per benchmark: format, field map (input/output/session/timestamp/tool),
   and inferability of tenant/session/output-length, with source URLs.
2. `03_sample_payloads.jsonl` — 3–5 records per benchmark WHERE legally/practically possible, each normalized to:
   {"source_benchmark","source_url","sample_id","task_family","session_id","turn_id","timestamp_ms",
    "input_text_or_summary","output_text_or_summary","input_tokens_estimate","output_tokens_estimate",
    "tool_call_count","has_multimodal_input","license_ok_for_research","notes"}
   Use SHORT snippets/summaries for input/output_text — NEVER large copyrighted text. nulls where unknown.
3. `03_sampling_blockers.md` — for every benchmark you could NOT sample, why (gated, login-walled, license,
   too large, no public examples), with URLs.
