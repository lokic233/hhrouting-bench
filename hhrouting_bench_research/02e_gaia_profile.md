# 02e — GAIA Profile (gated, measured with HF token)

**Dataset:** [gaia-benchmark/GAIA](https://huggingface.co/datasets/gaia-benchmark/GAIA) · License: gated/research · **466 tasks** (val+test, L1/L2/L3) · cl100k_base.

**Role in HHRouting-Bench:** anchors `deep_research_long_horizon` and `browser_computer_use_multimodal`.
GAIA tasks are short to STATE but require long multi-step tool/agent execution (the routing cost is in the
agent loop, not the prompt).

## Measured (cl100k_base)
| signal | distribution | note |
|---|---|---|
| Question input tokens | P50=49 · P90=110 · P99=303 · max=787 (n=466) | the *task statement* only — tiny |
| Final answer tokens | P50=2 · P90=8 · P99=22 · max=67 (n=165) | exact-match answers — near-zero (P50=2) |
| Annotator "Steps" (reasoning-trace proxy) | P50=0 · P90=206 · P99=714 · max=3798 (n=466) | proxy for the hidden agent-loop length |
| Levels | {'L1': 146, 'L2': 245, 'L3': 75} | L3 = hardest / longest-horizon |
| Multimodal | **109 tasks (23.4%) have file attachments** | → `browser_computer_use_multimodal` |

## Routing interpretation
- **Prompt tokens are NOT the workload.** Question P50=49, answer P50=2 — but each task fans out into many
  tool calls / browser steps / model invocations. The real routing load is the **agent loop**, invisible in
  the static payload (matches Agent D: GAIA is schema/payload, the trace must be synthesized from agent runs).
- **23.4% multimodal** (file attachments) → the only measured signal for the multimodal
  browser/computer-use class; those requests carry image/doc prefill not captured by text tokens.
- The "Steps" field (P99=714 tok) is the closest public proxy for how long the deep-research loop runs.
