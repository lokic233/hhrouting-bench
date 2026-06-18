import json, statistics as st, tiktoken, pandas as pd
from huggingface_hub import hf_hub_download
enc=tiktoken.get_encoding("cl100k_base")
def toks(s): return len(enc.encode(s or "", disallowed_special=()))
def pct(xs,p):
    xs=sorted(xs); k=(len(xs)-1)*p/100; f=int(k)
    return xs[f] if f+1>=len(xs) else xs[f]+(xs[f+1]-xs[f])*(k-f)
def stats(xs): return dict(n=len(xs),min=min(xs),p50=round(pct(xs,50)),p90=round(pct(xs,90)),p99=round(pct(xs,99)),max=max(xs),mean=round(st.mean(xs))) if xs else None
out=[]
def push(key,ins,outs,**m):
    rec=dict(key=key,tokenizer="cl100k_base",status="ok",**m); rec["input_tokens"]=stats(ins); rec["output_tokens"]=stats(outs) if outs else None
    out.append(rec); it=rec["input_tokens"]; print(f"OK  {key:22} in P50={it['p50']:>6} P99={it['p99']:>7} max={it['max']:>7}",flush=True)

# MultiNews: raw .src.cleaned (docs joined by '|||||') + .tgt summaries
try:
    src=hf_hub_download("multi_news","data/test.src.cleaned",repo_type="dataset")
    tgt=hf_hub_download("multi_news","data/test.tgt",repo_type="dataset")
    S=open(src,encoding="utf-8",errors="ignore").read().splitlines()
    T=open(tgt,encoding="utf-8",errors="ignore").read().splitlines()
    N=min(150,len(S),len(T))
    push("MultiNews",[toks(S[i].replace("|||||","\n")) for i in range(N)],[toks(T[i]) for i in range(N)],hf_id="multi_news",split="test")
except Exception as e: print("ERR MultiNews",str(e)[:140])

# RepoBench: download the 2 parquet shards, read with pandas directly
try:
    fs=["data/cross_file_first-00000-of-00002-baebda7f3a6e980a.parquet","data/cross_file_first-00001-of-00002-5780ed62c5162a3e.parquet"]
    dfs=[pd.read_parquet(hf_hub_download("tianyang/repobench_python_v1.1",f,repo_type="dataset")) for f in fs]
    df=pd.concat(dfs).head(200)
    incol = "all_code" if "all_code" in df.columns else df.columns[0]
    print("RepoBench cols:",list(df.columns)[:8])
    ins=[toks(str(df.iloc[i].get(incol,""))) for i in range(len(df))]
    outs=[toks(str(df.iloc[i].get("next_line",""))) for i in range(len(df))] if "next_line" in df.columns else None
    push("RepoBench-py",ins,outs,hf_id="tianyang/repobench_python_v1.1",config="cross_file_first",split="test")
except Exception as e: print("ERR RepoBench",str(e)[:140])
json.dump(out,open("measured5.json","w"),indent=2); print(f"WROTE measured5.json: {len(out)}")
