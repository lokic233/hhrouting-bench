# Second pass: datasets that need non-standard loading (zip, parquet data_files, alt configs).
import json, statistics as st, time, io, zipfile, os
import tiktoken
from datasets import load_dataset
from huggingface_hub import hf_hub_download
enc = tiktoken.get_encoding("cl100k_base")
def toks(s): return len(enc.encode(s or "", disallowed_special=()))
def pct(xs,p):
    xs=sorted(xs); k=(len(xs)-1)*p/100; f=int(k)
    return xs[f] if f+1>=len(xs) else xs[f]+(xs[f+1]-xs[f])*(k-f)
def stats(xs):
    if not xs: return None
    return dict(n=len(xs),min=min(xs),p50=round(pct(xs,50)),p90=round(pct(xs,90)),p99=round(pct(xs,99)),max=max(xs),mean=round(st.mean(xs)))
def J(*ks):
    def f(r): return "\n".join(str(r.get(k,"") or "") for k in ks)
    return f

out=[]
def emit(key,infn,outfn,records,**meta):
    ins=[toks(infn(r)) for r in records]
    rec=dict(key=key,tokenizer="cl100k_base",status="ok",**meta)
    rec["input_tokens"]=stats(ins)
    if outfn:
        outs=[]
        for r in records:
            v=outfn(r)
            if isinstance(v,list): v=" ".join(map(str,v))
            outs.append(toks(v))
        rec["output_tokens"]=stats(outs)
    else: rec["output_tokens"]=None
    out.append(rec)
    it=rec["input_tokens"]
    print(f"OK  {key:24} in P50={it['p50']:>6} P99={it['p99']:>7} max={it['max']:>7}", flush=True)

# --- LongBench: download data.zip, read per-task .jsonl ---
LB_TASKS={"narrativeqa":150,"hotpotqa":150,"gov_report":120,"multifieldqa_en":150,"qasper":150,"2wikimqa":150}
try:
    zpath=hf_hub_download("THUDM/LongBench","data.zip",repo_type="dataset")
    zf=zipfile.ZipFile(zpath)
    names=zf.namelist()
    for task,n in LB_TASKS.items():
        cand=[x for x in names if x.endswith(f"{task}.jsonl")]
        if not cand: print(f"ERR LongBench-{task} (no file)"); continue
        rows=[json.loads(l) for l in zf.read(cand[0]).decode().splitlines() if l.strip()][:n]
        # LongBench schema: context,input,answers
        emit(f"LongBench-{task}", J("context","input"), J("answers"), rows, hf_id="THUDM/LongBench", config=task, split="test")
except Exception as e:
    print("ERR LongBench-zip", str(e)[:120])

# --- RepoBench python (parquet data_files) ---
try:
    ds=load_dataset("tianyang/repobench_python_v1.1", data_files={"test":"data/cross_file_first-*.parquet"}, split="test")
    sub=ds.select(range(min(200,len(ds))))
    emit("RepoBench-py-cff", J("all_code"), J("next_line"), list(sub), hf_id="tianyang/repobench_python_v1.1", config="cross_file_first", split="test")
except Exception as e:
    print("ERR RepoBench", str(e)[:120])

# --- MultiNews via parquet mirror ---
for key,repo,cfg,ink,outk,n in [
    ("MultiNews","alexfabbri/multi_news",None,"document","summary",150),
]:
    try:
        ds=load_dataset(repo,split="test")
        sub=ds.select(range(min(n,len(ds))))
        emit(key, J(ink), J(outk), list(sub), hf_id=repo, config=cfg, split="test")
    except Exception as e:
        print(f"ERR {key}", str(e)[:120])

json.dump(out, open("measured2.json","w"), indent=2)
print(f"\nWROTE measured2.json: {len(out)} entries")
