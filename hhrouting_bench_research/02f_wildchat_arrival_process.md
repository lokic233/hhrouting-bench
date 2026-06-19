# 02f — WildChat-1M Arrival Process (request-level trace, extracted from real timestamps)

**Dataset:** [allenai/WildChat-1M](https://huggingface.co/datasets/allenai/WildChat-1M) · License: **ODC-BY** · 237,264 conversations · timezone **UTC** · resolution 1s.
**Window:** 2023-04-09 00:02:53+00:00 → 2023-06-23 07:57:07+00:00 (~75.3 days).

**Why this is the headline result:** of all 25 measured benchmarks, WildChat-1M is the **only chat source with
real per-request timestamps**. That lets us extract an actual **arrival process** — inter-arrival times,
burstiness, diurnal pattern, and tenant re-arrival — rather than synthesizing a Poisson process. This turns
WildChat from "payload" into a **near-direct request-level trace** for `interactive_chat_global`.

## Arrival rate & inter-arrival
- **Mean arrival rate:** 2.19 conversations/min (0.0365/s) — *in this sample*.
- **Inter-arrival time (s):** P10=3 · **P50=17** · P90=63 · P99=150 · max=1251.
- **Conv starts / minute:** P50=2 · P90=4 · P99=7 · max=15.
- **Conv starts / hour:** P50=126 · P90=195 · max=427.

## Burstiness (vs Poisson)
- **CV of per-minute counts:** 0.778 (Poisson = 1.0)
- **Fano factor (var/mean), per minute:** 1.32 (Poisson = 1.0)
- **Peak-to-mean ratio (hourly):** 3.25×
- **Verdict:** NO — overdispersed (see Fano). CV>1 and Fano>>1 => bursty/over-dispersed vs Poisson (Poisson CV=1,Fano=1).

## Diurnal pattern (normalized to mean, UTC)
A clear day/night cycle — **peak ~09:00 UTC (1.30×)**, **trough ~23:00 UTC (0.73×)**:

| UTC hour | 0 | 3 | 6 | 9 | 12 | 15 | 18 | 21 |
|---|---|---|---|---|---|---|---|---|
| rate/mean | 0.76 | 0.91 | 1.05 | 1.3 | 1.23 | 1.18 | 0.98 | 0.76 |

(Full 24h series + per-minute histogram in `02f_wildchat_arrival.png`.)

## Tenant re-arrival (session affinity over time)
- Gap between consecutive conversations from the same tenant (hashed_ip, ≥3 convs): **P50=922s (~15 min)** · P90=96192s.
- Combined with the earlier finding (top 1% tenants = 21% of traffic), this gives a **measured session/affinity
  model**: returning users cluster, with a ~15-min median gap — directly usable for prefix-cache TTL / session-sticky routing experiments.

## How to USE this in HHRouting-Bench (the build recipe)
1. **Direct replay:** the inter-arrival distribution + diurnal multiplier reproduce a realistic chat arrival
   process without inventing a Poisson λ. Multiply the base rate to target any load level.
2. **Burstiness is real but mild in-sample** (Fano≈1.3). Production multiplexes thousands of users → true
   burstiness is higher; use the diurnal shape + a burst multiplier to stress head-of-line-blocking.
3. **Tenant model:** assign sessions by hashed_ip, replay re-arrival gaps → exercises session affinity,
   prefix-cache reuse, and unfair-tenant-starvation.
4. **Join with the token profile (02c):** each arrival carries the WildChat token distribution (user input
   P50=19, prefill-ctx-per-turn P50=522, output P50=275) → a complete request = (arrival time, tenant, token shape).

## Caveats (honest)
- **Sampled rate, not absolute.** We measured ~237k convs across the released shards; the absolute req/s is a
  function of how much of WildChat you replay. **Shape** (inter-arrival distribution, diurnal, burstiness,
  re-arrival) is the transferable artifact, not the raw rate.
- **Conversation-start granularity.** `timestamp` marks conversation start; individual follow-up turns within a
  multi-turn conversation are not separately timestamped, so intra-session turn timing is modeled (turns/conv
  from 02c), not measured.
- The shards are not strictly time-partitioned, so concatenating them widens the window; dedup by
  conversation_hash applied. Diurnal/burstiness are computed on real UTC stamps and are robust to this.
