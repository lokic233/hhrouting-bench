# AGENT R — Final Overnight Report Synthesizer

ROLE: Read EVERY deliverable in hhrouting_bench_research/ (01_, 01b_, 02_, 03_, 04_, 05_, 06_ and all CSVs)
and synthesize the single authoritative report. Do not re-do research — synthesize what the committee
produced, resolve contradictions (note them), and apply the ranking + final-decision framework.

DELIVERABLE: `07_final_overnight_report.md` with EXACTLY these sections:
1. Executive summary (what we can now confidently say).
2. Top 20 candidate benchmarks (table).
3. Top 10 highest-priority benchmarks for HHRouting-Bench (with why).
4. Benchmarks to drop or deprioritize.
5. Workload decomposition summary.
6. Trace feasibility matrix summary.
7. Canonical workload taxonomy (the 6–10 classes).
8. Data extraction plan for the next 48 hours (concrete, ordered).
9. Synthetic augmentation plan (ONLY after benchmark decomposition — list stressors to add).
10. Risks and red-team critique (fold in Agent F).
11. Open questions for Loki and Liangqi.

RANKING CRITERIA (apply to every benchmark): public GitHub validation; public dataset/task schema; ability
to map to request-level serving traces; meaningful input/output token diversity; exposes prefill/decode/KV/
cache/routing stress; supports multi-turn/session/tool-call decomposition; community recognition; legal/
license clarity; practical extraction effort; non-redundancy.

FINAL DECISION per benchmark — assign and put in a table:
- Priority: P0 (must use) / P1 (likely useful) / P2 (maybe) / Drop
- Workload class mapping: one of the canonical classes (or 'other')
- Trace extraction mode: direct_trace / payload_only / schema_only / synthetic_required / not_suitable

ALSO PRODUCE (synthesize from peers' _sources files + your own):
- `sources.json` — JSON array of {id,label,url,benchmark} for every source URL cited across the package.
- `sources.bib` — BibTeX entries for the papers/datasets (best-effort; key by benchmark name).

Every claim still needs a source URL. Be decisive but honest about uncertainty.
