# 02g — Production Inference Traces: MEASURED (the direct-trace gold standard)

Agent G *documented* these; here they are **downloaded and measured**. These 6 are the only sources
with **real arrivals + native token counts** (and Mooncake adds **prefix-cache hash_ids**). They are the
backbones HHRouting-Bench should replay directly — no synthesis needed for arrivals/tokens.

| trace | n requests | input P50 | output P50 | IAT P50 (s) | burst Fano/s | special |
|---|--:|--:|--:|--:|--:|---|
| Azure-LLM-conv-2023 | 19,366 | 1020.0 | 129.0 | 0.1 | 1.33 | real chat arrivals |
| Azure-LLM-code-2023 | 8,819 | 1469.0 | 13.0 | 0.1 | 13.2 | autocomplete: in»out, strict TTFT |
| Azure-LMM-multimodal-2024 | 1,000,000 | 1124.0 | 98.0 | 0.3 | 1.76 | 50% w/ images (NumImages) |
| BurstGPT | 1,404,294 | 262.0 | 36.0 | 1.0 | 2.01 | 1.4M reqs, ChatGPT+GPT-4 |
| Mooncake-conversation | 12,031 | 6909.0 | 350.0 | 0.0 | 1.1 | prefix hash_ids |
| Mooncake-toolagent | 23,608 | 6346.0 | 30.0 | 0.0 | 1.57 | prefix hash_ids (tool loop) |

## The standout routing signals (all MEASURED, not estimated)

### 1. Prefix-cache reuse (Mooncake `hash_ids`) — the rarest signal
- **Conversation trace:** prefix-cache hit-ratio proxy **0.366** (24.2% of 182,790 unique blocks reused), prefix blocks/req P50=14.0.
- **Tool-agent trace:** hit-ratio proxy **0.553** — tool loops reuse context MORE (agentic context carries forward). This is the measured basis for prefix-aware / KV-reuse routing.

### 2. Prefill/decode asymmetry (Azure code vs conv)
- **Code/autocomplete:** input P50=1469.0 but output P50=13.0 (ratio 113.0:1) + Fano/s=13.2 → extreme prefill-heavy, decode-light, very bursty = the `strict_slo_autocomplete` class, measured.
- **Conversation:** input P50=1020.0, output P50=129.0 (ratio 7.91:1) — balanced.

### 3. Real burstiness + model mix (BurstGPT, 1,404,294 reqs)
- Models: {'ChatGPT': 1189167, 'GPT-4': 215127}. Fano/s=2.01 (over-dispersed vs Poisson=1). input P50=262.0, output P50=36.0.

### 4. Multimodal (Azure LMM 2024, 1,000,000 reqs)
- **50.0% of requests carry images** (NumImages P90=9.0), input P50=1124.0 → the measured anchor for `browser_computer_use_multimodal` (image prefill not captured by text tokens).

## How these slot into HHRouting-Bench
- **Direct replay (no synthesis):** Azure conv/code/MM + BurstGPT give arrival time + token counts per request. Mooncake adds prefix structure. Replay verbatim, scale rate to target load.
- **Coverage map:** Azure-conv→`interactive_chat_global` (alt to WildChat), Azure-code→`strict_slo_autocomplete`, Azure-MM→`browser_computer_use_multimodal`, BurstGPT→bursty chat at scale, Mooncake-conv→prefix-reuse chat, Mooncake-tool→`workflow_tool_agent` w/ measured KV reuse.
- **Together with WildChat (02f):** 7 real arrival traces now measured — the scarce resource Agent A/D flagged. HHRouting-Bench arrivals are now evidence-grounded, not synthetic.

## Caveats
- Azure timestamps anonymized to a window (real inter-arrival preserved; absolute date shifted). Token counts are the provider's own tokenizer (not cl100k) — these are NATIVE counts, more accurate than our estimates.
- Mooncake `hash_ids` are remapped block hashes (privacy); the hit-ratio proxy is first-seen-vs-repeat over block references — a lower bound on real cache benefit (ignores eviction/window).
- BurstGPT timestamps are integer seconds → sub-second ordering within a second is arbitrary.