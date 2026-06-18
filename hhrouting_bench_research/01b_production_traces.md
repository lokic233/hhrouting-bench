# Production LLM Inference Traces for HHRouting-Bench

This document catalogs public, GitHub-validated datasets containing real-world LLM serving inference traces. These traces are critical for simulating request-level workloads, including arrival processes, token lengths, and session tracking.

## Ranked List of Most Usable Request-Level Traces
1. **Azure LLM Inference Dataset (2024 & 2023)**: The gold standard for direct request-level traces, containing real timestamps, context tokens, and generated tokens from production Azure clusters.
2. **BurstGPT**: Highly valuable for its inclusion of multi-turn conversation tracking (`Session ID`) alongside timestamps and token lengths from real ChatGPT/GPT-4 API usage.
3. **Mooncake Trace**: Extremely rare and valuable for prefix-caching evaluation, as it explicitly includes `hash_ids` representing prefix blocks along with token lengths and timestamps from Moonshot AI's Kimi service.
4. **Splitwise Artifact Traces**: Provides Azure production traces (similar to the Azure Public Dataset but packaged for the Splitwise ISCA'24 paper).
5. **LMSYS Chatbot Arena Conversations**: Contains real timestamps and text (which can be tokenized), but is limited by gated access.
6. **ShareGPT (Standard vLLM benchmark)**: Commonly used but lacks arrival timestamps, requiring synthesized (e.g., Poisson) arrival processes.

---

## 1. Azure LLM Inference Dataset (2024 & 2023)
- **GitHub URL**: [https://github.com/Azure/AzurePublicDataset](https://github.com/Azure/AzurePublicDataset)
- **Dataset URL**: [https://github.com/Azure/AzurePublicDataset/blob/master/AzureLLMInferenceDataset2024.md](https://github.com/Azure/AzurePublicDataset/blob/master/AzureLLMInferenceDataset2024.md)
- **Contained Fields**: `TIMESTAMP` (invocation time), `ContextTokens` (input tokens), `GeneratedTokens` (output tokens). Prompt text is omitted for GDPR reasons.
- **License**: [CC-BY 4.0 Attribution License](https://github.com/Azure/AzurePublicDataset/blob/master/LICENSE)
- **Last Update**: May 2024 (for the 2024 dataset), 2023 (for the 2023 dataset).
- **Direct Request-Level Trace**: **Yes**. These are true production arrivals and token counts without aggregation.

## 2. BurstGPT
- **GitHub URL**: [https://github.com/HPMLL/BurstGPT](https://github.com/HPMLL/BurstGPT)
- **Dataset URL**: [https://huggingface.co/datasets/lzzmm/BurstGPT](https://huggingface.co/datasets/lzzmm/BurstGPT)
- **Contained Fields**: `Timestamp` (seconds from 0:00:00), `Session ID` (for conversation continuity tracking), `Elapsed time`, `Model` (ChatGPT/GPT-4), `Request tokens`, `Response tokens`, `Total tokens`, `Log Type` (Conversation vs API).
- **License**: [CC-BY 4.0](https://github.com/HPMLL/BurstGPT/blob/main/LICENSE)
- **Last Update**: Jan 2024 (ArXiv paper) / Active releases in 2024.
- **Direct Request-Level Trace**: **Yes**. Real-world trace of ChatGPT/GPT-4 workloads capturing both bursty arrivals and actual token lengths.

## 3. Mooncake Trace (Kimi/Moonshot AI)
- **GitHub URL**: [https://github.com/kvcache-ai/Mooncake](https://github.com/kvcache-ai/Mooncake)
- **Dataset URL**: [https://github.com/kvcache-ai/Mooncake/tree/main/FAST25-release/traces](https://github.com/kvcache-ai/Mooncake/tree/main/FAST25-release/traces)
- **Contained Fields**: `timestamp`, `input_length`, `output_length`, `hash_ids` (an array representing blocked prefix caches for exact cache-hit simulations).
- **License**: [Apache 2.0](https://github.com/kvcache-ai/Mooncake/blob/main/LICENSE-APACHE)
- **Last Update**: Feb 2025 (FAST 2025 artifact release).
- **Direct Request-Level Trace**: **Yes**. Extracted from Kimi's production serving platform, featuring unique prefix block metadata for routing optimization.

## 4. Splitwise Artifact Traces
- **GitHub URL**: [https://github.com/Mutinifni/splitwise-sim](https://github.com/Mutinifni/splitwise-sim)
- **Dataset URL**: [https://zenodo.org/records/11003049](https://zenodo.org/records/11003049)
- **Contained Fields**: Contains raw `.csv` traces (`AzureLLMInferenceTrace_conv.csv` and `AzureLLMInferenceTrace_code.csv`) mirroring the Azure public dataset schema.
- **License**: [CC-BY 4.0](https://zenodo.org/records/11003049)
- **Last Update**: April 2024.
- **Direct Request-Level Trace**: **Yes**. Backs the ISCA'24 Splitwise paper.

## 5. LMSYS Chatbot Arena Conversations
- **GitHub URL**: [https://github.com/lm-sys/FastChat](https://github.com/lm-sys/FastChat)
- **Dataset URL**: [https://huggingface.co/datasets/lmsys/chatbot_arena_conversations](https://huggingface.co/datasets/lmsys/chatbot_arena_conversations)
- **Contained Fields**: Question ID, full conversation text (can be tokenized for lengths), anonymized user ID, timestamp.
- **License**: CC-BY 4.0 (for user inputs).
- **Last Update**: Mid-2023 (for the 33K split) to 2024.
- **Direct Request-Level Trace**: **Yes, but GATED**. The dataset is set to `gated="auto"` on Hugging Face, requiring manual authentication. It provides real timestamps but requires an extra tokenization step to get `input_tokens` and `output_tokens`.

## 6. ShareGPT (vLLM / Sarathi-Serve standard)
- **GitHub URL**: [https://github.com/vllm-project/vllm](https://github.com/vllm-project/vllm)
- **Dataset URL**: [https://huggingface.co/datasets/anon8231489123/ShareGPT_Vicuna_unfiltered](https://huggingface.co/datasets/anon8231489123/ShareGPT_Vicuna_unfiltered)
- **Contained Fields**: Text prompts and responses only.
- **License**: Unclear / Scraped data.
- **Last Update**: 2023.
- **Direct Request-Level Trace**: **No**. This dataset contains only payloads. Standard benchmarks (like vLLM's benchmark suite) must synthesize request arrival times (e.g., via a Poisson process) because true timestamps are absent. 

## 7. Alibaba GPU Cluster Data (2020-2022)
- **GitHub URL**: [https://github.com/alibaba/clusterdata](https://github.com/alibaba/clusterdata)
- **Dataset URL**: [https://github.com/alibaba/clusterdata/tree/master/cluster-trace-gpu-v2020](https://github.com/alibaba/clusterdata/tree/master/cluster-trace-gpu-v2020)
- **Contained Fields**: GPU utilization, task names, instances, sensor metrics. 
- **License**: Custom Alibaba EULA / Open for research.
- **Last Update**: 2022 (NSDI '22).
- **Direct Request-Level Trace**: **No**. The trace provides aggregate metrics of MLaaS jobs (training and inference) across 6,500 GPUs. It lacks the request-level token resolution (input/output tokens) necessary for LLM serving routing.
