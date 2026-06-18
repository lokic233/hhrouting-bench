import statistics as st, tiktoken
from datasets import load_dataset
enc = tiktoken.get_encoding("cl100k_base")
def toks(s): return len(enc.encode(s or "", disallowed_special=()))
def pct(xs,p):
    xs=sorted(xs); k=(len(xs)-1)*p/100; f=int(k)
    return xs[f] if f+1>=len(xs) else xs[f]+(xs[f+1]-xs[f])*(k-f)
def summ(name, xs):
    if not xs: print(f"{name}: NO DATA"); return
    print(f"{name}: n={len(xs)} min={min(xs)} P50={pct(xs,50):.0f} P90={pct(xs,90):.0f} P99={pct(xs,99):.0f} max={max(xs)} mean={st.mean(xs):.0f}")

print("=== GSM8K ===")
ds=load_dataset("openai/gsm8k","main",split="test")
summ("GSM8K INPUT", [toks(r["question"]) for r in ds.select(range(min(300,len(ds))))])
summ("GSM8K OUTPUT",[toks(r["answer"])   for r in ds.select(range(min(300,len(ds))))])

print("=== HumanEval ===")
ds=load_dataset("openai_humaneval",split="test")
summ("HumanEval INPUT", [toks(r["prompt"]) for r in ds])
summ("HumanEval OUTPUT",[toks(r["canonical_solution"]) for r in ds])

print("=== LongBench narrativeqa (parquet) ===")
try:
    ds=load_dataset("THUDM/LongBench","narrativeqa",split="test")
    summ("LongBench/narrativeqa INPUT", [toks(r.get("context","")+"\n"+r.get("input","")) for r in ds.select(range(min(120,len(ds))))])
except Exception as e:
    print("LongBench ERR:", str(e)[:120])
