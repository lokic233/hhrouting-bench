# AGENT G (Gemini) — Production Inference-Trace Hunter (supplementary, parallel to A)

ROLE: A focused deep-search for PUBLIC, REAL LLM/serving INFERENCE TRACES — the single highest-value and
hardest-to-find category for HHRouting-Bench. These are gold because they carry real arrival times + token
counts (i.e. potential DIRECT traces, not just payloads).

Search hard (use the internet) for, at minimum:
- Azure LLM inference traces (Azure Public Dataset / AzurePublicDataset GitHub)
- BurstGPT (request arrival + token traces)
- Mooncake trace (Kimi/Moonshot serving trace)
- Any vLLM / SGLang / production serving trace releases
- LMSYS / chatbot-arena request logs with timestamps
- Alibaba / cloud GPU cluster traces relevant to inference
- Any arrival-process or token-length trace dataset cited in serving papers (Splitwise, DistServe,
  Sarathi-Serve, AlpaServe, etc. — check their artifact/GitHub for released traces)

For each trace source found, record: name, github_url (verify public), dataset_url, what fields it actually
contains (timestamps? input_tokens? output_tokens? session id? model id?), license, last_update, and whether
it is a DIRECT request-level trace or just aggregate stats. Mark gated/unavailable ones explicitly.

DELIVERABLE: `01b_production_traces.md`
- One section per trace source, with the fields above and EVERY claim backed by a source URL.
- A short ranked list at the top: which trace sources are most directly usable as request-level arrivals.
- If a "trace" turns out to be aggregate-only or unavailable, say so clearly (that is a valuable finding).
Keep it tight and source-cited. Do not narrate your search process in the file — only the findings.
