# HHRouting-Bench — multi-agent research environment

A **benchmark-grounded evidence package** for studying **LLM serving routing** across multiple GPU/vLLM
nodes. This repo is a multi-agent research environment instantiated from the
[research-os](https://github.com/lokic233/research-os) template (the generic autonomous-research engine),
adapted into a focused **7-agent hostile research committee** running on 4 model backends.

> **Goal of the sprint:** answer, with source-cited evidence — *Which public, GitHub-validated benchmarks/
> datasets are actually usable for decomposing into request-level LLM serving routing workloads?*
> We care about **serving mechanics, not model accuracy.**

## The committee (roles × backends)

| Agent | Role | Backend |
|-------|------|---------|
| A | Benchmark Validator | Claude Opus 4.8 |
| B | Workload Decomposer | Claude Sonnet 4.7 |
| C | Dataset Sampler / Payload Inspector | Codex 5.5 |
| D | Trace Feasibility Analyst | Claude Opus 4.8 |
| E | Canonical Workload Taxonomy Builder | Claude Opus 4.8 |
| F | Red Team / Skeptical Reviewer | Codex 5.5 |
| G | Production Inference-Trace Hunter | Gemini 3.5 |
| R | Final Report Synthesizer | Claude Opus 4.8 |

All four requested backends are in play: **Gemini 3.5, Claude Code 4.8, Claude Code 4.7, Codex 5.5.**

## How it runs

```bash
./run_sprint.sh        # dependency-aware wave schedule, all agents headless + internet-enabled
```

Dependency waves:
```
WAVE 1 (parallel):  A (validate)  ||  C (sample payloads)  ||  G (hunt traces)
WAVE 2 (parallel):  B (decompose) ||  D (trace feasibility)      [read A/C/G]
WAVE 3:             E (taxonomy)                                 [read A–D]
WAVE 4:             F (red team)                                 [attack A–E]
WAVE 5:             R (final overnight report + sources.json/bib)
```

## Layout

```
prompts/agents/   role prompts (A–G, R) + _common.md (shared rules + hard constraints)
tasks/            per-agent task addendum (the "go now" instruction)
run_agent.sh      dispatch ONE agent to its backend (Linux internet-mode flags)
run_sprint.sh     the wave driver
hhrouting_bench_research/   ← ALL DELIVERABLES land here
logs/             per-agent run logs
```

## Deliverables (produced into `hhrouting_bench_research/`)

`01_benchmark_validation_table.csv` · `01b_production_traces.md` ·
`02_workload_decomposition.csv` + `_notes.md` · `03_payload_schema_inventory.md` +
`03_sample_payloads.jsonl` + `03_sampling_blockers.md` · `04_trace_feasibility_matrix.csv` +
`04_trace_feasibility_summary.md` · `05_canonical_workload_taxonomy.md` + `.csv` ·
`06_red_team_review.md` · `07_final_overnight_report.md` · `sources.json` · `sources.bib`

## Hard constraints (enforced in every agent prompt)

- Do **not** modify HHRouting implementation code. Do **not** generate final synthetic traces yet.
- Every claim has a **source URL**. Gated/unclear/deprecated data is marked explicitly.
- Token ranges that are estimates are **labelled as estimates** with method.
- No accuracy-leaderboard focus. No large copyrighted text dumps.

---
Built by Navi (Meta engineering assistant) for [@lokic233](https://github.com/lokic233).
