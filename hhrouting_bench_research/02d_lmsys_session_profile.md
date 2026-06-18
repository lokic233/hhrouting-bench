# 02d — LMSYS-Chat-1M Session/Routing Profile (gated, measured with HF token)

**Dataset:** [lmsys/lmsys-chat-1m](https://huggingface.co/datasets/lmsys/lmsys-chat-1m) · License: **research / non-commercial, no de-anonymization** · shard 0, **20,000 conversations** · cl100k_base.

**Role in HHRouting-Bench:** second pillar for `interactive_chat_global`, and the best **model-heterogeneity**
source — 25 distinct models in one trace (vs WildChat's 2). Use it for model-routing /
heterogeneity labels. NOTE: unlike WildChat-1M it has **no timestamps and no IP/tenant** field, so it is
payload+structure only (no arrival process, weaker session-affinity signal).

## Measured token distributions (cl100k_base)
| signal | distribution | routing meaning |
|---|---|---|
| User message input | P50=16 · P90=157 · P99=576 · max=2503 | per-request prefill |
| Assistant message output | P50=125 · P90=407 · P99=661 · max=402367 | decode residency |
| Prefill context per assistant turn (cumulative) | P50=127 · P90=1266 · P99=5653 · max=403498 | real per-turn prefill |
| Full-session token total (KV high-water) | P50=316 · P90=1023 · P99=2830 · max=805865 | KV footprint |
| Turns per conversation | P50=2 · P90=8 · P99=26 · max=170 | multi-turn growth |

**Models (25):** vicuna-13b, koala-13b, alpaca-13b, chatglm-6b, llama-13b, vicuna-33b, llama-2-13b-chat, oasst-pythia-12b, fastchat-t5-3b, claude-1 … — heterogeneity/model-routing signal.

⚠️ **Degenerate-tail caveat:** the assistant-output `max` (~402K) and session `max` (~805K) come from **6
degenerate repetition loops** out of ~20K conversations — a real serving system caps these via `max_tokens`.
Use **P50/P90/P99** for routing; treat the raw max as a degenerate-generation artifact, not a real request.

## Routing interpretation
- Same shape as WildChat: tiny user msgs (P50=16) but cumulative prefill per turn ~8x larger (P50=127, P99=5653).
- Shorter sessions than WildChat (turns P50=2 vs 4) — more single-shot Q&A, less deep multi-turn.
- **Its unique value = model heterogeneity** (25 models) → the only public chat trace rich
  enough to drive heterogeneous-backend / model-aware routing experiments.
