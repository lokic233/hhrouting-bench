# Agent C Sampling Blockers

This file records benchmarks that could not be sampled, or could only be partially sampled, without running full evaluations or downloading large corpora.

## Azure LLM inference traces

Source URLs: https://github.com/Azure/AzurePublicDataset and https://github.com/Azure/AzurePublicDataset/blob/master/AzureLLMInferenceDataset2024.md

Blocker: the primary source discovered for the LLM inference dataset is GitHub-hosted, and direct GitHub page/raw access was blocked by this agent's environment proxy. I did not infer schema or fabricate rows without reading the source. Sampling status: no sample rows.

## LMSYS-Chat-1M

Source URLs: https://huggingface.co/datasets/lmsys/lmsys-chat-1m and https://huggingface.co/papers/2309.11998

Blocker: the dataset page is visible, but raw/card access through the Hugging Face dataset endpoint returned an access-restricted message for unauthenticated access. Sampling status: no sample rows.

## WildChat-1M

Source URL: https://huggingface.co/datasets/allenai/WildChat-1M

Blocker: public card and two streamed rows were accessible, but repeated remote host disconnects prevented collecting the requested 3-5 samples without spending the run on retries. Sampling status: two normalized summaries.

## SWE-bench Verified

Source URL: https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified

Blocker: card and one streamed row were accessible, but follow-up streaming and direct parquet download attempts hit repeated disconnect/redirect failures. Sampling status: one normalized summary.

## ToolBench

Source URLs: https://github.com/OpenBMB/ToolBench and https://huggingface.co/datasets/Adorg/ToolBench

Blocker: the official GitHub source could not be fetched directly in this environment. The HF mirror exposed a small demo query and one answer tree, but larger instruction files stalled through the HF hub helper. Sampling status: two partial rows, one instruction and one trajectory summary.

## tau-bench

Source URLs: https://github.com/sierra-research/tau-bench and https://github.com/sierra-research/tau2-bench

Blocker: discovered source is GitHub-hosted; direct GitHub access was blocked. PyPI package names `tau-bench`, `tau2-bench`, and `taubench` were not available in this environment. Sampling status: no sample rows.

## OSWorld

Source URLs: https://github.com/xlang-ai/OSWorld, https://os-world.github.io/, and https://huggingface.co/datasets/xlangai/osworld_v2_tasks

Blocker: OSWorld V2 task classes are in a gated Hugging Face dataset, and unauthenticated loading returned a gated-dataset error. Sampling status: no sample rows.

## RAGBench

Source URL: https://huggingface.co/datasets/rungalileo/ragbench

Blocker: card and two streamed covidqa rows were accessible, but repeated HF remote disconnects made additional verified samples unreliable during this run. Sampling status: two normalized summaries.

## LongBench / LongBench v2

Source URLs: https://huggingface.co/datasets/THUDM/LongBench and https://huggingface.co/datasets/zai-org/LongBench-v2

Blocker: LongBench v1 uses a dataset script rejected by the installed `datasets` version. LongBench v2 streamed two rows after retries, but additional rows were not collected to avoid repeated remote disconnects. Sampling status: two LongBench v2 normalized summaries; no LongBench v1 rows.

## RepoBench

Source URLs: https://huggingface.co/datasets/tianyang/repobench-p, https://github.com/Leolty/repobench, and https://arxiv.org/abs/2306.03091

Blocker: HF RepoBench-P requires a dataset script, and the installed `datasets` version rejects dataset scripts. Direct official GitHub access was blocked. Sampling status: no sample rows.

## AppWorld

Source URLs: https://github.com/StonyBrookNLP/appworld, https://appworld.dev/, https://pypi.org/project/appworld/, and https://huggingface.co/datasets/LukaszTP/AppWorld-Tasks

Blocker: none for small instruction-level samples from the HF mirror. Full local task state would require AppWorld data installation/evaluation and may expose supervisor PII-like fields; this run sampled only short task summaries. Sampling status: three normalized summaries.

## WebArena / WebArena Verified

Source URLs: https://github.com/web-arena-x/webarena, https://github.com/ServiceNow/webarena-verified, and https://pypi.org/project/webarena-verified/

Blocker: none for small task-level samples from the installed `webarena-verified` PyPI package. Full browser traces require running evaluations and are out of scope tonight. Sampling status: three normalized summaries.
