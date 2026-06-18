import json, statistics as st, tiktoken
from datasets import load_dataset
enc=tiktoken.get_encoding("cl100k_base")
def toks(s): return len(enc.encode(s or "", disallowed_special=()))
def pct(xs,p):
    xs=sorted(xs); k=(len(xs)-1)*p/100; f=int(k)
    return xs[f] if f+1>=len(xs) else xs[f]+(xs[f+1]-xs[f])*(k-f)
def stats(xs): return dict(n=len(xs),min=min(xs),p50=round(pct(xs,50)),p90=round(pct(xs,90)),p99=round(pct(xs,99)),max=max(xs),mean=round(st.mean(xs))) if xs else None
def J(*ks):
    def f(r): return "\n".join(str(r.get(k,"") or "") for k in ks)
    return f
out=[]
def emit(key,infn,outfn,recs,**m):
    rec=dict(key=key,tokenizer="cl100k_base",status="ok",**m)
    rec["input_tokens"]=stats([toks(infn(r)) for r in recs])
    rec["output_tokens"]=stats([toks(outfn(r)) for r in recs]) if outfn else None
    out.append(rec); it=rec["input_tokens"]; print(f"OK  {key:22} in P50={it['p50']:>6} P99={it['p99']:>7} max={it['max']:>7}",flush=True)

# RepoBench via direct parquet data_files (the listing showed these exact files)
try:
    ds=load_dataset("tianyang/repobench_python_v1.1",
        data_files=["data/cross_file_first-00000-of-00002-baebda7f3a6e980a.parquet",
                    "data/cross_file_first-00001-of-00002-5780ed62c5162a3e.parquet"],split="train")
    emit("RepoBench-py", J("all_code"), J("next_line"), list(ds.select(range(min(200,len(ds))))), hf_id="tianyang/repobench_python_v1.1",config="cross_file_first")
except Exception as e: print("ERR RepoBench", str(e)[:140])

# MultiNews: find its parquet path
try:
    from huggingface_hub import list_repo_files
    fs=[f for f in list_repo_files("multi_news",repo_type="dataset") if f.endswith(".parquet") and "test" in f]
    if fs:
        ds=load_dataset("parquet",data_files=f"hf://datasets/multi_news/{fs[0]}",split="train")
        emit("MultiNews", J("document"), J("summary"), list(ds.select(range(min(150,len(ds))))), hf_id="multi_news")
    else: print("ERR MultiNews no parquet; files sample:", list_repo_files("multi_news",repo_type="dataset")[:5])
except Exception as e: print("ERR MultiNews", str(e)[:140])
json.dump(out,open("measured4.json","w"),indent=2); print(f"WROTE measured4.json: {len(out)}")
