# Token measurement harness (produces 02b_measured_token_distributions)

Measures REAL input/output token distributions from public benchmark payloads using tiktoken cl100k_base.

## Run
```bash
source /tmp/agentenv.sh
# IMPORTANT: the devvm no_proxy contains a bracketed IPv6 ([::1]) that breaks urllib3's
# proxy parser ("Invalid port: ':1]'"). Strip it for the python process:
export no_proxy=".facebook.com,.fbinfra.net,.internalfb.com,localhost,127.0.0.1"
export NO_PROXY="$no_proxy" HF_HUB_DISABLE_PROGRESS_BARS=1
python3 measure.py           # standard datasets (parquet-backed)
python3 measure2.py          # LongBench (data.zip), summarization
python3 measure5.py          # MultiNews (raw .src/.tgt), RepoBench (parquet shards)
```
Outputs merge into ../../hhrouting_bench_research/02b_measured_token_distributions.{csv,json}.

## Coverage: 22 public datasets measured. GAIA gated (needs HF token). LMSYS-Chat-1M / WildChat gated too.
