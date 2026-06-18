import json, statistics as st
import tiktoken
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

# RepoBench: config is positional name, use 'cross_file_first'
try:
    ds=load_dataset("tianyang/repobench_python_v1.1","cross_file_first",split="test")
    emit("RepoBench-py", J("all_code"), J("next_line"), list(ds.select(range(min(200,len(ds))))), hf_id="tianyang/repobench_python_v1.1",config="cross_file_first",split="test")
except Exception as e: print("ERR RepoBench", str(e)[:120])

# MultiNews via explicit parquet mirror (alexfabbri/multi_news has parquet under refs/convert)
try:
    ds=load_dataset("multi_news",split="test",revision="refs/convert/parquet")
    emit("MultiNews", J("document"), J("summary"), list(ds.select(range(min(150,len(ds))))), hf_id="multi_news",split="test")
except Exception as e:
    try:
        ds=load_dataset("parquet",data_files="hf://datasets/multi_news@refs/convert/parquet/default/test/0000.parquet",split="train")
        emit("MultiNews", J("document"), J("summary"), list(ds.select(range(min(150,len(ds))))), hf_id="multi_news",split="test")
    except Exception as e2: print("ERR MultiNews", str(e2)[:120])

json.dump(out,open("measured3.json","w"),indent=2); print(f"WROTE measured3.json: {len(out)}")
