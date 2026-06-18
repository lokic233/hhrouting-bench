# 02c — WildChat-1M Session/Routing Profile (gated dataset, measured with HF token)

**Dataset:** [allenai/WildChat-1M](https://huggingface.co/datasets/allenai/WildChat-1M) · License: **ODC-BY** · measured shard 0, **20,000 conversations** · tokenizer cl100k_base.

**Why this matters:** WildChat-1M is the single best public proxy for `interactive_chat_global`. Unlike the
other 22 benchmarks (payload-only), it carries the fields routing actually needs: **real timestamps**,
**tenant identity (`hashed_ip`)**, **model id**, **per-turn role structure**, and **geo** — measured below.

## Measured token distributions (cl100k_base)

| signal | distribution | routing meaning |
|---|---|---|
| **User message input** | P50=19 · P90=207 · P99=2019 · max=8111 | per-request prefill (single msg) |
| **Assistant message output** | P50=275 · P90=723 · P99=1454 · max=4050 | decode residency / TPOT load |
| **Prefill context per assistant turn** (cumulative) | P50=522 · P90=2825 · P99=5605 · max=8152 | **the real prefill the server re-computes each turn** — far above single-msg P50 |
| **Full-session token total** (KV high-water) | P50=844 · P90=3888 · P99=7446 · max=8192 | KV-cache footprint per session |
| **Turns per conversation** | P50=4 · P90=14 · P99=30 · max=110 | multi-turn context growth / session length |

## Session / tenant structure (the routing-critical part)
- **Unique tenants (hashed_ip):** 5,426 across 20,000 conversations.
- **Tenant skew:** the **top 1% of tenants account for 21.3% of all conversations** — a strong, MEASURED signal for session-affinity routing and unfair-tenant-starvation stress (not estimated).
- **Models in trace:** {'gpt-3.5-turbo-0301': 12074, 'gpt-4-0314': 7926} — enables heterogeneity / model-routing labels.
- **Languages:** {'English': 9464, 'Chinese': 5732, 'Russian': 1729, 'French': 502, 'Spanish': 353, 'Italian': 318}.

## Routing interpretation
1. **Prefill ≠ single message.** Single user messages are tiny (P50=19), but the *cumulative prefill context*
   per assistant turn is P50=522 / P99=5605 — the router must size prefill on the **growing session context**,
   not the last message. This is the head-of-line-blocking + KV-pressure regime.
2. **Decode-dominant per turn.** Assistant output (P50=275) >> user input (P50=19): ~14:1 — interactive chat is
   decode-residency-bound at the turn level, prefill-bound at the session level. A router juggling both is the
   core `interactive_chat_global` challenge.
3. **Session affinity is real and skewed.** With 21%+ of traffic from 1% of tenants, prefix/KV reuse and
   session-sticky routing have large, measurable upside — and starvation risk if mishandled.
4. **Arrival process available.** `timestamp` is present per turn → real inter-arrival/burstiness can be
   derived (next 48h work), making WildChat a *near-direct* trace for chat (rare among the 23).

## Caveats
- One shard (~60k convs) sampled at 20k; distributions are stable but not the full 1M.
- cl100k_base counts; SentencePiece tokenizers shift ±10-20% (shape stable).
- `timestamp` present but arrival-process extraction (inter-arrival, concurrency) is deferred to the 48h plan.
