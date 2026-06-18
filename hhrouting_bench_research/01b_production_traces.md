# Production Inference-Trace Datasets

## Summary Ranked List (Usability for Request-Level Arrivals & Routing)
1. **Mooncake LLM Serving Traces (Kimi)**: Highest value for routing due to the inclusion of `hash_ids` for KV cache/prefix sharing analysis along with token counts and timestamps.
2. **Azure LLM Inference Traces (2023/2024)**: Directly usable large-scale request-level traces from a major cloud provider (Microsoft), explicitly containing timestamps and token counts.
3. **BurstGPT**: Directly usable ChatGPT/GPT-4 workload trace with actual arrival times, elapsed times, session IDs, and token counts.
4. **LMSYS Chatbot Arena Conversations**: Extremely rich real-world user conversations with timestamps. Token counts must be inferred by re-tokenizing the conversational text, but it accurately captures session multi-turn dynamics.
5. **Alibaba GenAI Serving Dataset (GenTD26)**: Highly detailed top-down trace of request execution, but focused on Stable Diffusion (GenAI) rather than LLM text generation. Useful for pipeline stage routing.
6. **Azure Functions Trace 2019**: Aggregate serverless function invocations. Often used in LLM serving papers (e.g., AlpaServe) as a proxy for request arrival burstiness, but does not contain LLM-specific token counts.

---

## 1. Mooncake LLM Serving Traces (Kimi/Moonshot)
* **GitHub URL**: https://github.com/kvcache-ai/Mooncake (Public)
* **Dataset URL**: https://github.com/kvcache-ai/Mooncake/tree/main/FAST25-release/traces
* **Contained Fields**: `timestamp`, `input_length`, `output_length`, `hash_ids` (indicates KV cache block/prefix sharing). Contains three sub-traces: `conversation_trace.jsonl`, `synthetic_trace.jsonl`, and `toolagent_trace.jsonl`.
* **License**: Apache-2.0 (Source: https://api.github.com/repos/kvcache-ai/Mooncake/license)
* **Last Update**: Released for FAST 2025.
* **Trace Type**: Direct request-level LLM serving trace.
* **Status**: Open, available.

## 2. Azure LLM Inference Traces (Azure Public Dataset)
* **GitHub URL**: https://github.com/Azure/AzurePublicDataset (Public)
* **Dataset URLs**: 
  * 2023 Trace (Splitwise): https://github.com/Azure/AzurePublicDataset/blob/master/AzureLLMInferenceDataset2023.md
  * 2024 Trace (DynamoLLM): https://github.com/Azure/AzurePublicDataset/blob/master/AzureLLMInferenceDataset2024.md
* **Contained Fields**: `TIMESTAMP` (invocation time), `ContextTokens` (input), `GeneratedTokens` (output).
* **License**: CC-BY-4.0 (Source: https://api.github.com/repos/Azure/AzurePublicDataset/license)
* **Last Update**: May 2024 (for the 2024 trace dataset).
* **Trace Type**: Direct request-level inference trace.
* **Status**: Open, available.

## 3. BurstGPT
* **GitHub URL**: https://github.com/HPMLL/BurstGPT (Public)
* **Dataset URL**: https://github.com/HPMLL/BurstGPT/releases/tag/v2.0
* **Contained Fields**: `Timestamp`, `Session ID`, `Elapsed time`, `Model`, `Request tokens`, `Response tokens`, `Total tokens`, `Log Type`.
* **License**: CC-BY-4.0 (Source: https://api.github.com/repos/HPMLL/BurstGPT/license)
* **Last Update**: 2024 (v2.0 release adding elapsed time and session IDs).
* **Trace Type**: Direct request-level traces based on Azure OpenAI API interactions.
* **Status**: Open, available.

## 4. LMSYS Chatbot Arena Conversations
* **GitHub URL**: N/A (Dataset hosted on HuggingFace)
* **Dataset URL**: https://huggingface.co/datasets/lmsys/chatbot_arena_conversations
* **Contained Fields**: `question_id`, `model_a`, `model_b`, `conversation_a` (content, role), `conversation_b` (content, role), `turn`, `anony`, `language`, `tstamp` (timestamp), `openai_moderation`, `toxic_chat_tag`.
* **License**: cc (HuggingFace card metadata; non-commercial terms often apply based on underlying model APIs).
* **Last Update**: Collected April to June 2023.
* **Trace Type**: Direct request-level conversation logs. Explicit token lengths are missing but can be synthetically derived from the provided raw conversation strings.
* **Status**: Open, available.

## 5. Alibaba GenAI Serving Top-Down Dataset 2026 (GenTD26)
* **GitHub URL**: https://github.com/alibaba/clusterdata (Public)
* **Dataset URL**: https://github.com/alibaba/clusterdata/tree/master/cluster-trace-v2026-GenAI
* **Contained Fields**: Detailed system tracing including `pipeline_inference_data_anon.csv`, `pod_gpu_duty_cycle_anon.csv`, and application-level `lora_request_trace.csv`.
* **License**: Unknown (Repo implies open access for research, but no explicit SPDX license file matched).
* **Last Update**: 2026 (Reflected in dataset title).
* **Trace Type**: Direct request-level pipeline trace (Note: Focused on Stable Diffusion/Generative Image, NOT LLM text generation).
* **Status**: Open, available.

## 6. Azure Functions Trace 2019 (Proxy Trace)
* **GitHub URL**: https://github.com/Azure/AzurePublicDataset (Public)
* **Dataset URL**: https://github.com/Azure/AzurePublicDataset/blob/master/AzureFunctionsDataset2019.md
* **Contained Fields**: Function invocation counts/triggers, execution time distributions, memory allocation distributions.
* **License**: CC-BY-4.0 (Source: https://api.github.com/repos/Azure/AzurePublicDataset/license)
* **Last Update**: July 2019.
* **Trace Type**: Aggregate serverless execution times and invocations. Does not contain token lengths. Included here as it is frequently cited (e.g., AlpaServe) as a source for simulating realistic cloud arrival burstiness.
* **Status**: Open, available.

## Note on Serving Paper Artifacts
Many popular LLM serving systems do not release net-new production traces, but instead re-synthesize or repackage existing datasets:
* **DistServe / vLLM**: Both systems typically rely on `ShareGPT` (https://huggingface.co/datasets/anon8231489123/ShareGPT_Vicuna_unfiltered) for token lengths and synthesize arrival times artificially using a Poisson process (Source: https://github.com/LLMServe/DistServe/blob/main/evaluation/2-benchmark-serving/0-prepare-dataset.py).
* **AlpaServe**: Uses the Azure Functions 2019 trace (above) to simulate request arrival distribution.
