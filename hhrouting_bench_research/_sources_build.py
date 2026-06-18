#!/usr/bin/env python3
import json

SRC = r"""
https://huggingface.co/datasets/lmsys/lmsys-chat-1m | LMSYS-Chat-1M HF card (gated, custom license, 1M convs, 69.5/214.5 avg prompt/response tokens, 2.0 avg turns, 154 langs)
https://huggingface.co/datasets/allenai/WildChat-1M | WildChat-1M HF card (odc-by, ~838k rows, turn field, multilingual)
https://huggingface.co/datasets/allenai/WildChat-1M/blob/main/README.md | WildChat-1M README (ODC-BY, not gated; full version gated; 837989 examples; updated 2024-10-17)
https://huggingface.co/datasets/anon8231489123/ShareGPT_Vicuna_unfiltered | ShareGPT Vicuna unfiltered HF card (apache-2.0, ~53k convs, 2048-token chunks, English-only)
https://huggingface.co/datasets/RyokoAI/ShareGPT52K | ShareGPT52K HF card (cc0-1.0, ~52k/90k convs, viewer error)
https://huggingface.co/datasets/stingning/ultrachat | UltraChat (stingning) HF card (mit, ~949k dialogues, ChatGPT-generated)
https://huggingface.co/datasets/HuggingFaceH4/ultrachat_200k | UltraChat 200k HF card (mit, 515311 rows, user/assistant roles)
https://huggingface.co/datasets/HuggingFaceH4/ultrachat_200k/commits/main | UltraChat 200k commit history (top commit Oct 16 2024)
https://huggingface.co/datasets/OpenAssistant/oasst1 | oasst1 HF card (apache-2.0, 88.8k rows, message-tree structure)
https://huggingface.co/datasets/OpenAssistant/oasst2 | oasst2 HF card (apache-2.0, 135k rows, message-tree structure)
https://github.com/lm-sys/FastChat | FastChat repo (ShareGPT/Vicuna tooling, LMSYS)
https://github.com/thunlp/UltraChat | UltraChat GitHub repo
https://github.com/LAION-AI/Open-Assistant | OpenAssistant GitHub repo
https://github.com/princeton-nlp/SWE-bench | SWE-bench repo (5.2k stars, MIT, harness)
https://arxiv.org/abs/2310.06770 | SWE-bench paper
https://huggingface.co/datasets/SWE-bench/SWE-bench | SWE-bench HF dataset
https://huggingface.co/datasets/SWE-bench/SWE-bench_Verified | SWE-bench Verified HF dataset (500 rows, problem_statement + gold patch)
https://github.com/scaleapi/SWE-bench_Pro-os | SWE-bench Pro open-source repo (447 stars, MIT, eval scripts)
https://huggingface.co/datasets/ScaleAI/SWE-bench_Pro | SWE-bench Pro HF dataset (731 rows, public, problem_statement + gold patch)
https://github.com/openai/SWELancer-Benchmark | SWE-Lancer original repo (archived Jul 18 2025, redirects to preparedness)
https://github.com/openai/preparedness | OpenAI preparedness repo (active SWE-Lancer eval, MIT, 1.2k stars)
https://github.com/openai/human-eval | HumanEval repo (3.3k stars, MIT, eval harness, data/ folder)
https://arxiv.org/abs/2107.03374 | HumanEval paper
https://huggingface.co/datasets/google-research-datasets/mbpp | MBPP HF dataset (CC-BY-4.0, 974/427 rows, prompts+code)
https://arxiv.org/abs/2108.07732 | MBPP paper
https://github.com/LiveCodeBench/LiveCodeBench | LiveCodeBench repo (887 stars, MIT, 143 commits)
https://huggingface.co/datasets/livecodebench/code_generation_lite | LiveCodeBench HF dataset (public, cc, viewer disabled)
https://github.com/Leolty/RepoBench | RepoBench repo (208 stars, CC-BY-4.0, eval.py)
https://huggingface.co/datasets/tianyang/repobench_python_v1.1 | RepoBench Python v1.1 HF dataset
https://github.com/seketeam/DevEval | DevEval repo (40 stars, NO license listed, 3 commits)
https://huggingface.co/datasets/LJ0815/DevEval | DevEval HF dataset (cc-by-4.0, 2.59GB, broken viewer)
https://github.com/bigcode-project/bigcodebench | BigCodeBench repo (509 stars, Apache-2.0, v0.2.4 Mar 2 2025)
https://huggingface.co/datasets/bigcode/bigcodebench-hard | BigCodeBench-hard HF dataset
https://github.com/laude-institute/terminal-bench | terminal-bench repo (2.4k stars, Apache-2.0, in-repo tasks, harbor successor)
https://github.com/OpenBMB/ToolBench | ToolBench repo (5.7k stars, Apache-2.0, ToolEval, data on GDrive/Tsinghua, 120k+ solution paths)
https://arxiv.org/abs/2307.16789 | ToolBench/ToolLLM paper
https://github.com/THUDM/AgentBench | AgentBench repo (3.5k stars, Apache-2.0, Docker envs, configs/prompts)
https://arxiv.org/abs/2308.03688 | AgentBench paper
https://github.com/sierra-research/tau-bench | tau-bench repo (1.3k stars, MIT, run.py, historical_trajectories, deprecated->tau2)
https://arxiv.org/abs/2406.12045 | tau-bench paper
https://github.com/StonyBrookNLP/appworld | AppWorld repo (444 stars, Apache-2.0, v0.1.3.post1 Feb 17 2026, ReAct trajectories)
https://arxiv.org/abs/2407.18901 | AppWorld paper
https://github.com/web-arena-x/webarena | WebArena repo (1.5k stars, Apache-2.0, 812 tasks, self-host Docker, 170 human recordings)
https://arxiv.org/abs/2307.13854 | WebArena paper
https://github.com/web-arena-x/visualwebarena | VisualWebArena repo (480 stars, MIT, 910 tasks, GDrive trajectories)
https://arxiv.org/abs/2401.13649 | VisualWebArena paper
https://github.com/xlang-ai/OSWorld | OSWorld repo (2.9k stars, Apache-2.0, VM required, v0.1.16 Jun 26 2024)
https://arxiv.org/abs/2404.07972 | OSWorld paper
https://github.com/Farama-Foundation/miniwob-plusplus | MiniWoB++ repo (388 stars, MIT, Selenium/Gymnasium, 100+ envs, Aug 14 2023)
https://huggingface.co/datasets/gaia-benchmark/GAIA | GAIA HF dataset (GATED contact-sharing + no-reshare, ~450+ Qs, no license shown)
https://arxiv.org/abs/2311.12983 | GAIA paper
https://github.com/web-arena-x/BrowserArena | BrowserArena at web-arena-x: HTTP 404, repo does not exist
https://github.com/search?q=BrowserArena+benchmark+LLM&type=repositories | GitHub repo search for BrowserArena: 0 results
https://arxiv.org/abs/2510.02418 | BrowserArena paper (arXiv, UPenn, Oct 2025, live Arena platform, no repo/dataset linked)
https://github.com/ServiceNow/WorkArena | WorkArena repo (256 stars, v0.5.3 Feb 3 2026, browsergym-workarena, gated HF instances)
https://github.com/ServiceNow/WorkArena/blob/main/LICENSE | WorkArena LICENSE (Apache-2.0, ServiceNow 2024)
https://arxiv.org/abs/2403.07718 | WorkArena paper
https://huggingface.co/datasets/THUDM/LongBench | LongBench HF card (no license shown, viewer disabled, 4750 ex, 5k-15k words)
https://github.com/THUDM/LongBench | LongBench/LongBench v2 GitHub (MIT, 1.2k stars, pred.py/result.py)
https://huggingface.co/datasets/THUDM/LongBench-v2 | LongBench v2 HF card (apache-2.0, 503 MCQ, 8k-2M words, viewer TooBigContentError)
https://huggingface.co/datasets/OpenLMLab/LEval | L-Eval HF mirror (HTTP 401 inaccessible)
https://huggingface.co/datasets/L4NLP/LEval | L-Eval canonical HF dataset (gpl-3.0, public, input 71.6k-116k chars, gold answers)
https://github.com/OpenLMLab/LEval | L-Eval GitHub (GPL-3.0, 405 stars, auto_eval.py/llm_eval.py)
https://huggingface.co/datasets/galileo-ai/ragbench | RAGBench HF (cc-by-4.0, 12 subsets, rows viewable)
https://huggingface.co/datasets/rungalileo/ragbench | RAGBench second public mirror (cc-by-4.0)
https://arxiv.org/abs/2407.11005 | RAGBench paper
https://huggingface.co/datasets/hotpotqa/hotpot_qa | HotpotQA HF (cc-by-sa-4.0, 203k rows, context/supporting_facts visible)
https://arxiv.org/abs/1809.09600 | HotpotQA paper
https://huggingface.co/datasets/google-research-datasets/natural_questions | Natural Questions HF (cc-by-sa-3.0, 144GB, full-wiki-page contexts)
https://research.google/pubs/pub47761/ | Natural Questions paper
https://huggingface.co/datasets/mandarjoshi/trivia_qa | TriviaQA HF (license unknown, 847k rows, 34.8GB, evidence docs)
https://arxiv.org/abs/1705.03551 | TriviaQA paper
https://huggingface.co/datasets/dgslibisey/MuSiQue | MuSiQue HF mirror (NO dataset card, 22355 rows viewable)
https://github.com/StonyBrookNLP/musique | MuSiQue GitHub (CC-BY-4.0, 227 stars, evaluate_v1.0.py)
https://github.com/Alab-NII/2wikimultihop | 2WikiMultihopQA GitHub (CC-BY-4.0 data, Apache repo, 156 stars, Dropbox-only data, no HF)
https://aclanthology.org/2020.coling-main.580/ | 2WikiMultihopQA paper
https://huggingface.co/datasets/deepmind/narrativeqa | NarrativeQA HF (apache-2.0, 28668 rows, full-story contexts ~41k tokens)
https://arxiv.org/abs/1712.07040 | NarrativeQA paper
https://huggingface.co/datasets/allenai/qasper | Qasper HF (cc-by-4.0, 1585 papers/5049 Qs, full_text contexts, gold answers)
https://github.com/allenai/qasper-led-baseline | Qasper official LED baseline eval scripts
https://huggingface.co/datasets/ccdv/arxiv-summarization | arXiv summarization HF card (no license shown; avg tokens 6038/299; 431826 rows)
https://huggingface.co/datasets/ccdv/pubmed-summarization | PubMed summarization HF card (no license shown; avg 3043/215; 266430 rows)
https://huggingface.co/datasets/ccdv/govreport-summarization | GovReport HF card (no license shown; 19463 rows)
https://huggingface.co/datasets/launch/gov_report | GovReport alt mirror (cc-by-4.0; 19.5k rows)
https://huggingface.co/datasets/alexfabbri/multi_news | MultiNews HF card (license other/LILY LAB non-commercial; viewer disabled)
https://huggingface.co/datasets/kmfoda/booksum | BookSum HF card (BSD-3-Clause; 12515 rows; chapter/book summaries)
https://arxiv.org/abs/2104.02112 | arXiv/PubMed/GovReport summarization paper (efficient attention long-doc)
https://arxiv.org/abs/1906.01749 | MultiNews paper
https://arxiv.org/abs/2105.08209 | BookSum paper
https://github.com/stanford-crfm/helm | HELM GitHub (Apache-2.0; 2.8k stars; v0.5.16 Apr 30 2026; maintenance mode June 1 2026)
https://arxiv.org/abs/2211.09110 | HELM paper
https://github.com/EleutherAI/lm-evaluation-harness | lm-eval-harness GitHub (MIT; 13k stars; v0.4.12 May 11 2026; public prompts)
https://arxiv.org/abs/2405.14782 | lm-evaluation-harness paper
https://huggingface.co/datasets/cais/mmlu | MMLU HF card (MIT; public; 231400 rows / 14042 test)
https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro | MMLU-Pro HF card (MIT; public; 12102 rows; cot_content; updated 2026.03.11)
https://github.com/openai/grade-school-math | GSM8K GitHub (archived Apr 8 2026; 1.4k stars; 8.5K problems w/ CoT)
https://github.com/hendrycks/math | MATH GitHub (MIT; 1.4k stars; dataset linked off-repo)
https://huggingface.co/datasets/HuggingFaceH4/MATH-500 | MATH-500 verified mirror (public; 500 test rows; problem/solution/answer)
https://huggingface.co/datasets/Idavidrein/gpqa | GPQA HF card (GATED contact-info agreement; CC-BY-4.0; 448 MCQs)
https://github.com/google/BIG-bench | BIG-bench GitHub (archived Apr 17 2026; Apache-2.0; 3.2k stars; 200+ JSON tasks)
https://github.com/suzgun/BIG-Bench-Hard | BBH source repo: 404 on all fetch attempts (unverifiable directly)
https://huggingface.co/datasets/maveriq/bigbenchhard | BBH HF mirror (MIT; public; 6511 rows; 23 tasks; input/target)
https://github.com/Azure/AzurePublicDataset | Azure Public Dataset repo (CC-BY-4.0/MIT, 1.1k stars, latest release Jun 2 2026)
https://github.com/Azure/AzurePublicDataset/blob/master/AzureLLMInferenceDataset2023.md | Azure LLM Inference 2023 columns (TIMESTAMP, ContextTokens, GeneratedTokens; no prompt text per GDPR)
https://github.com/Azure/AzurePublicDataset/blob/master/AzureLLMInferenceDataset2024.md | Azure LLM Inference 2024 one-week (May 10-19 2024), same 3 columns
https://github.com/Azure/AzurePublicDataset/blob/master/README.md | Azure repo README (maps datasets to Splitwise ISCA24 / DynamoLLM HPCA25)
https://www.microsoft.com/en-us/research/publication/splitwise-efficient-generative-llm-inference-using-phase-splitting/ | Splitwise paper (Azure 2023 trace)
https://arxiv.org/abs/2408.00741 | DynamoLLM paper (Azure 2024 trace)
https://github.com/HPMLL/BurstGPT | BurstGPT trace schema (CC-BY-4.0, 272 stars, v2.0 Jan 15 2026, ~5.34M rows)
https://arxiv.org/abs/2401.17644 | BurstGPT paper (KDD25)
https://github.com/kvcache-ai/Mooncake | Mooncake repo + mooncake_trace.jsonl (timestamp,input_length,output_length,hash_ids; Apache-2.0; 5.6k stars)
https://www.usenix.org/system/files/fast25-qin.pdf | Mooncake FAST25 paper
https://github.com/vllm-project/vllm/blob/main/benchmarks/README.md | vLLM benchmarks README (ShareGPT dataset; arrivals synthesized via Poisson)
"""

seen = set()
out = []
for line in SRC.strip().splitlines():
    line = line.strip()
    if not line or "|" not in line:
        continue
    url, label = line.split("|", 1)
    url = url.strip()
    label = label.strip()
    if url in seen:
        continue
    seen.add(url)
    out.append({"url": url, "label": label, "agent": "A"})

with open("_sources_A.jsonl", "w") as f:
    for o in out:
        f.write(json.dumps(o, ensure_ascii=False) + "\n")

print(f"OK: wrote {len(out)} unique sources to _sources_A.jsonl")
