# AGENT A — Benchmark Validator

ROLE: Validate the credibility and PUBLIC availability of candidate benchmarks for LLM serving-routing
workload decomposition. You are the evidence gatekeeper — downstream agents trust your table.

For EACH candidate benchmark, fetch its real GitHub repo + dataset card + paper, and record:
- benchmark_name, family
- github_url (verify it resolves and is public; a 404/private repo is a finding)
- paper_url, dataset_url, license (read the actual LICENSE file / HF card; if none, "unclear")
- repo_maturity: high / medium / low  (judge by stars, recency, issues, CI — cite the signal)
- last_update (last meaningful commit/release date you can see)
- dataset_public (yes/no/gated)
- eval_scripts (yes/no)
- raw_prompts_available (can you see actual prompt/conversation/task inputs? yes/no/partial)
- sample_outputs_available (completions/answers present? yes/no)
- request_trace_extractable (can request-level traces be DIRECTLY extracted? yes/maybe/no)
- blockers (gating, license risk, deprecation, huge size, etc.)
- source_urls (the URLs you actually read, ; separated)

CANDIDATE FAMILIES (inspect ALL; mark any that don't exist/aren't public):
- Chat/assistant: LMSYS-Chat-1M, WildChat, ShareGPT-style, UltraChat, OpenAssistant
- Coding/SWE: SWE-bench, SWE-bench Verified, SWE-bench Pro (if public), SWE-Lancer, HumanEval, MBPP,
  LiveCodeBench, RepoBench, DevEval, BigCodeBench, Terminal-Bench
- Agent/tool-use: ToolBench, AgentBench, tau-bench, AppWorld, WebArena, VisualWebArena, BrowserArena,
  OSWorld, MiniWoB++, GAIA, WorkArena
- RAG/long-context: LongBench, LongBench v2, L-Eval, RAGBench, HotpotQA, Natural Questions, TriviaQA,
  MuSiQue, 2WikiMultihopQA, NarrativeQA, Qasper
- Summarization/long-doc: arXiv summarization, PubMed summarization, GovReport, MultiNews, BookSum
- Batch eval: HELM, EleutherAI lm-evaluation-harness, MMLU, MMLU-Pro, GSM8K, MATH, GPQA, BBH/Big-Bench
- Production/serving traces: Azure LLM inference traces, any public LLM inference trace dataset, any public
  request arrival/token trace dataset from cloud or serving papers (search hard for these — they are the
  highest-value targets).

DELIVERABLE: `01_benchmark_validation_table.csv`
HEADER (exact): benchmark_name,family,github_url,paper_url,dataset_url,license,repo_maturity,dataset_public,eval_scripts,raw_prompts_available,sample_outputs_available,request_trace_extractable,last_update,blockers,source_urls

Aim for 35+ rows. Quote any field containing commas. Cite a URL in source_urls for every row.
