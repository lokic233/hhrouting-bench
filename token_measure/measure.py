import sys, json, statistics as st, traceback, time
import tiktoken
from datasets import load_dataset
from registry import REG
enc = tiktoken.get_encoding("cl100k_base")
def toks(s): return len(enc.encode(s or "", disallowed_special=()))
def pct(xs,p):
    xs=sorted(xs); k=(len(xs)-1)*p/100; f=int(k)
    return xs[f] if f+1>=len(xs) else xs[f]+(xs[f+1]-xs[f])*(k-f)
def stats(xs):
    if not xs: return None
    return dict(n=len(xs),min=min(xs),p50=round(pct(xs,50)),p90=round(pct(xs,90)),
                p99=round(pct(xs,99)),max=max(xs),mean=round(st.mean(xs)))

out=[]
only = sys.argv[1].split(",") if len(sys.argv)>1 else None
for key,hf,cfg,split,infn,outfn,n in REG:
    if only and key not in only: continue
    rec={"key":key,"hf_id":hf,"config":cfg,"split":split,"tokenizer":"cl100k_base"}
    t0=time.time()
    try:
        ds = load_dataset(hf,cfg,split=split) if cfg else load_dataset(hf,split=split)
        m=min(n,len(ds)); sub=ds.select(range(m))
        ins=[toks(infn(r)) for r in sub]
        rec["input_tokens"]=stats(ins)
        if outfn:
            outs=[]
            for r in sub:
                v=outfn(r)
                if isinstance(v,(list,)): v=" ".join(map(str,v))
                outs.append(toks(v))
            rec["output_tokens"]=stats(outs)
        else:
            rec["output_tokens"]=None
        rec["status"]="ok"; rec["secs"]=round(time.time()-t0,1)
        print(f"OK  {key:24} in P50={rec['input_tokens']['p50']:>6} P99={rec['input_tokens']['p99']:>7} max={rec['input_tokens']['max']:>7}"
              + (f" | out P50={rec['output_tokens']['p50']}" if rec.get('output_tokens') else ""), flush=True)
    except Exception as e:
        rec["status"]="error"; rec["error"]=str(e)[:200]
        print(f"ERR {key:24} {str(e)[:90]}", flush=True)
    out.append(rec)
json.dump(out, open("measured.json","w"), indent=2)
print(f"\nWROTE measured.json: {sum(1 for r in out if r['status']=='ok')}/{len(out)} ok")
