# Agent C Payload Schema Inventory

Scope note: this inventory is about request-level serving payload extraction, not task accuracy. Token counts in `03_sample_payloads.jsonl` are estimates using `ceil(character_count / 4)` and are labeled in sample notes.

## Azure LLM inference traces

Sources: https://github.com/Azure/AzurePublicDataset and https://github.com/Azure/AzurePublicDataset/blob/master/AzureLLMInferenceDataset2024.md

- Format: insufficient evidence from accessible content in this run; the primary source is a GitHub-hosted dataset note, but direct GitHub page/raw access was blocked by the environment proxy for this agent.
- Input fields: insufficient evidence.
- Output fields: insufficient evidence.
- Session/timestamp/tool fields: insufficient evidence.
- Tenant/session inferability: insufficient evidence.
- Output length: likely the relevant object for routing, but unverified until the GitHub-hosted schema can be read from the source URL above.
- Sampling: not sampled. See `03_sampling_blockers.md`.

## LMSYS-Chat-1M

Sources: https://huggingface.co/datasets/lmsys/lmsys-chat-1m and https://huggingface.co/papers/2309.11998

- Format: Hugging Face dataset page advertises parquet files for `lmsys/lmsys-chat-1m`: https://huggingface.co/datasets/lmsys/lmsys-chat-1m
- Field map: the public page description says each sample includes a conversation ID, model name, conversation text in OpenAI API JSON format, detected language tag, and OpenAI moderation API tag: https://huggingface.co/datasets/lmsys/lmsys-chat-1m
- Input/output fields: conversation text is the input/output source; role-separated turns need to be parsed from the OpenAI API JSON conversation field: https://huggingface.co/datasets/lmsys/lmsys-chat-1m
- Session IDs: conversation ID exists according to the dataset page description: https://huggingface.co/datasets/lmsys/lmsys-chat-1m
- Timestamps: insufficient evidence from accessible source content.
- Tool calls/actions: insufficient evidence; the dataset page description is chat conversations, not tool traces: https://huggingface.co/datasets/lmsys/lmsys-chat-1m
- Tenant/user inferability: the page states collection from 210K unique IP addresses, but it does not expose raw IPs in the accessible description: https://huggingface.co/datasets/lmsys/lmsys-chat-1m
- Output length: missing; estimate from assistant message text if access is granted.
- Sampling: not sampled because the dataset is gated for unauthenticated access in this run.

## WildChat-1M

Sources: https://huggingface.co/datasets/allenai/WildChat-1M and https://arxiv.org/abs/2405.01470

- Format: Hugging Face dataset card lists parquet data files under `data/train-*`: https://huggingface.co/datasets/allenai/WildChat-1M
- License: ODC-BY is stated in the dataset card: https://huggingface.co/datasets/allenai/WildChat-1M
- Input fields: `conversation` is a list of utterances with `role`, `content`, language, toxicity, redaction, and per-turn metadata; user turns also include `hashed_ip`, state/country, and request `header`: https://huggingface.co/datasets/allenai/WildChat-1M
- Output fields: assistant turns are in the same `conversation` list; assistant turns include a `timestamp` when the backend receives the full response: https://huggingface.co/datasets/allenai/WildChat-1M
- Session IDs: `conversation_hash` is present but the card says it is not unique; `turn_identifier` is the unique identifier within each turn: https://huggingface.co/datasets/allenai/WildChat-1M
- Timestamps: top-level `timestamp` is the timestamp of the last turn in UTC; assistant turns have response-receipt timestamps: https://huggingface.co/datasets/allenai/WildChat-1M
- Tool calls/actions: no tool-call fields are listed in the dataset card: https://huggingface.co/datasets/allenai/WildChat-1M
- Tenant/user inferability: `hashed_ip` plus request headers may link conversations according to the card: https://huggingface.co/datasets/allenai/WildChat-1M
- Output length: not a stored field; estimate from assistant `content` text.
- Sampling: two short summaries sampled from HF streaming output; remote streaming was unstable before a third verified sample could be collected.

## SWE-bench / SWE-bench Verified

Sources: https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified and https://www.swebench.com/

- Format: Hugging Face card lists one parquet test file, 500 test examples, and fields for repository issue repair: https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified
- Input fields: `problem_statement` is the issue title/body, with `repo`, `base_commit`, `hints_text`, and environment fields providing context: https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified
- Output fields: `patch` is the gold patch and `test_patch` is the test-file patch from the solution PR: https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified
- Session IDs: `instance_id` is the request identifier: https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified
- Timestamps: `created_at` is the creation date of the pull request: https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified
- Tool calls/actions: no tool-call loop is stored in the dataset fields: https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified
- Tenant/user inferability: repository name can act as a coarse tenant; no user/session field is documented on the card: https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified
- Output length: stored patch text can be measured; model completion length must be synthesized when running an agent.
- Sampling: one verified row sampled by HF streaming; further rows were blocked by repeated remote disconnects during this run.

## ToolBench

Sources: https://github.com/OpenBMB/ToolBench and https://huggingface.co/datasets/Adorg/ToolBench

- Format: the HF mirror has JSON instruction files, JSON answer trees, tool environment files, and an Apache-2.0 card license: https://huggingface.co/datasets/Adorg/ToolBench
- Input fields: `instruction/inference_query_demo.json` contains `query`, `query_id`, and `api_list`: https://huggingface.co/datasets/Adorg/ToolBench/resolve/main/instruction/inference_query_demo.json
- Output fields: answer JSON files contain a `tree` with node types such as `Action`, `Action Input`, `Thought`, observations, and terminal status: https://huggingface.co/datasets/Adorg/ToolBench/resolve/main/answer/G1_answer/10015_ChatGPT_DFS_woFilter_w2.json
- Session IDs: `query_id` can be used as request/session identifier in instruction files: https://huggingface.co/datasets/Adorg/ToolBench/resolve/main/instruction/inference_query_demo.json
- Timestamps: no timestamp field was observed in the sampled instruction or answer-tree files: https://huggingface.co/datasets/Adorg/ToolBench/resolve/main/instruction/inference_query_demo.json
- Tool calls/actions: `api_list` and answer-tree action nodes expose tool-call structure: https://huggingface.co/datasets/Adorg/ToolBench/resolve/main/instruction/inference_query_demo.json
- Tenant/user inferability: insufficient evidence; no tenant/user field observed in sampled files.
- Output length: final completion length is not directly available in the demo query; trajectory node text can be measured.
- Sampling: one demo query and one answer-tree summary sampled from the HF mirror; official GitHub content was not directly fetchable in this environment.

## tau-bench

Sources: https://github.com/sierra-research/tau-bench and https://github.com/sierra-research/tau2-bench

- Format: insufficient evidence from accessible content in this run; the public source found by search is GitHub-hosted: https://github.com/sierra-research/tau-bench
- Field map: insufficient evidence from accessible source content.
- Input/output/session/timestamp/tool fields: insufficient evidence.
- Tenant/user inferability: insufficient evidence.
- Output length: insufficient evidence.
- Sampling: not sampled. See `03_sampling_blockers.md`.

## WebArena / WebArena Verified

Sources: https://github.com/web-arena-x/webarena, https://github.com/ServiceNow/webarena-verified, and https://pypi.org/project/webarena-verified/

- Format: WebArena Verified package assets include JSON task files such as `test.raw.json` and `webarena-verified.json`: https://pypi.org/project/webarena-verified/
- Input fields: sampled tasks include `sites`, `task_id`, `intent`, `intent_template`, `instantiation_dict`, and `start_urls` or `start_url`: https://pypi.org/project/webarena-verified/
- Output fields: evaluation blocks include expected retrieved data or reference answers: https://pypi.org/project/webarena-verified/
- Session IDs: `task_id` can be used as request/session identifier: https://pypi.org/project/webarena-verified/
- Timestamps: no timestamp field observed in sampled task JSON.
- Tool calls/actions: browser actions are not stored in task JSON; evaluators can validate retrieved data or network events in the package schema: https://pypi.org/project/webarena-verified/
- Tenant/user inferability: `sites` is an environment/site dimension; no end-user identity field observed in task JSON.
- Output length: expected answer strings can be measured; generated browser-agent trace length must be collected during evaluation.
- Sampling: three short task summaries sampled from installed `webarena-verified` package assets.

## OSWorld

Sources: https://github.com/xlang-ai/OSWorld, https://os-world.github.io/, and https://huggingface.co/datasets/xlangai/osworld_v2_tasks

- Format: OSWorld V2 task classes are distributed as root-level `task_*.py` files in a gated HF dataset according to its README: https://huggingface.co/datasets/xlangai/osworld_v2_tasks
- Input fields: insufficient evidence for concrete per-task fields because the task implementations are gated: https://huggingface.co/datasets/xlangai/osworld_v2_tasks
- Output fields: insufficient evidence from accessible content.
- Session/timestamp/tool fields: insufficient evidence from accessible content.
- Multimodal input: OSWorld is described by its official site as benchmarking agents in real computer environments, but concrete task payload fields were not accessible in this run: https://os-world.github.io/
- Tenant/user inferability: insufficient evidence.
- Output length: insufficient evidence.
- Sampling: not sampled because the task dataset is gated.

## RAGBench

Sources: https://huggingface.co/datasets/rungalileo/ragbench

- Format: Hugging Face card lists parquet files across configs such as `covidqa`, `cuad`, `hotpotqa`, and others: https://huggingface.co/datasets/rungalileo/ragbench
- License: CC-BY-4.0 is stated in the dataset card: https://huggingface.co/datasets/rungalileo/ragbench
- Input fields: `question` and `documents` are the request payload fields for RAG serving: https://huggingface.co/datasets/rungalileo/ragbench
- Output fields: `response` is stored, with sentence-level support annotations and model/metric metadata: https://huggingface.co/datasets/rungalileo/ragbench
- Session IDs: `id` is available per row: https://huggingface.co/datasets/rungalileo/ragbench
- Timestamps: no timestamp field is listed in the card features: https://huggingface.co/datasets/rungalileo/ragbench
- Tool calls/actions: no tool-call fields are listed in the card features: https://huggingface.co/datasets/rungalileo/ragbench
- Tenant/user inferability: `dataset_name` or config can act as workload family, not a user/tenant identity: https://huggingface.co/datasets/rungalileo/ragbench
- Output length: stored `response` can be measured.
- Sampling: two short covidqa summaries sampled; remote reads were not stable enough to collect three verified rows.

## LongBench / LongBench v2

Sources: https://huggingface.co/datasets/THUDM/LongBench, https://huggingface.co/datasets/zai-org/LongBench-v2, https://longbench2.github.io, and https://arxiv.org/abs/2412.15204

- Format: LongBench v1 HF card says data are loaded by task configs through `THUDM/LongBench`; this currently uses a dataset script that the installed `datasets` version rejects: https://huggingface.co/datasets/THUDM/LongBench
- Format for v2: LongBench v2 HF repo provides `data.json`: https://huggingface.co/datasets/zai-org/LongBench-v2
- Input fields for v2: sampled rows include `_id`, `domain`, `sub_domain`, `difficulty`, `length`, `question`, choices A-D, `answer`, and `context`: https://huggingface.co/datasets/zai-org/LongBench-v2
- Output fields: `answer` is a multiple-choice key; generated rationale/completion is not stored: https://huggingface.co/datasets/zai-org/LongBench-v2
- Session IDs: `_id` can be used as request identifier: https://huggingface.co/datasets/zai-org/LongBench-v2
- Timestamps/tool calls/tenant fields: no timestamp, tool-call, or tenant fields observed in v2 samples.
- Output length: answer key is short; serving completion length must be synthesized by the evaluation prompt.
- Sampling: two v2 rows sampled; v1 was not sampled due deprecated dataset-script loading.

## RepoBench

Sources: https://huggingface.co/datasets/tianyang/repobench-p, https://github.com/Leolty/repobench, and https://arxiv.org/abs/2306.03091

- Format: HF RepoBench-P card says it is a retrieval-plus-code-completion task and provides configs for Python/Java through a dataset script: https://huggingface.co/datasets/tianyang/repobench-p
- Input fields: the card schema lists `repo_name`, `file_path`, `context` entries with `path`, `identifier`, `snippet`, `tokenized_snippet`, plus `import_statement` and `code`: https://huggingface.co/datasets/tianyang/repobench-p
- Output fields: next-line/code-completion target fields are described by the card schema continuation, but exact field names beyond the visible card excerpt require loading the script/data: https://huggingface.co/datasets/tianyang/repobench-p
- Session IDs: no explicit session ID is documented; combine `repo_name` and `file_path` if sampled later: https://huggingface.co/datasets/tianyang/repobench-p
- Timestamps/tool calls: no timestamp or tool-call fields documented on the card: https://huggingface.co/datasets/tianyang/repobench-p
- Tenant/user inferability: repository name can act as tenant/workload family; no user field is documented: https://huggingface.co/datasets/tianyang/repobench-p
- Output length: target code text can be measured after data loading.
- Sampling: not sampled because the HF dataset requires a deprecated dataset script in the installed loader.

## AppWorld

Sources: https://github.com/StonyBrookNLP/appworld, https://appworld.dev/, https://pypi.org/project/appworld/, and https://huggingface.co/datasets/LukaszTP/AppWorld-Tasks

- Format: PyPI package summary describes AppWorld as a controllable world of apps and people for benchmarking interactive coding agents: https://pypi.org/project/appworld/
- Input fields: HF mirror samples include `task_id`, `instruction`, `supervisor`, `datetime`, `db_version`, mode, difficulty, `num_apps`, `num_apis`, and `num_api_calls`: https://huggingface.co/datasets/LukaszTP/AppWorld-Tasks
- Output fields: benchmark output is produced through app/API state changes; the HF mirror exposes metadata such as API-call counts, not final assistant text: https://huggingface.co/datasets/LukaszTP/AppWorld-Tasks
- Session IDs: `task_id` can be used as request/session identifier: https://huggingface.co/datasets/LukaszTP/AppWorld-Tasks
- Timestamps: `datetime` is present in sample rows: https://huggingface.co/datasets/LukaszTP/AppWorld-Tasks
- Tool calls/actions: `num_apis` and `num_api_calls` are present in sample rows; package code exposes API-call logs for environments: https://pypi.org/project/appworld/
- Tenant/user inferability: `supervisor` contains person fields in the HF mirror, so sampled payloads should avoid copying PII-like details: https://huggingface.co/datasets/LukaszTP/AppWorld-Tasks
- Output length: not stored as final text; route workload can use instruction length and expected API-call loop counts.
- Sampling: three short task summaries sampled from the HF mirror.
