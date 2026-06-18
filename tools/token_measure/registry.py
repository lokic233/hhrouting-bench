# Curated dataset registry: (key, hf_id, config, split, input_fn, output_fn, max_samples, notes)
# input_fn/output_fn map a record -> the text that would be SENT to / RETURNED by the model.
# Only PUBLIC, ungated datasets here. Gated ones (LMSYS-Chat-1M, WildChat) handled separately (need HF token).
def J(*ks):
    def f(r):
        return "\n".join(str(r.get(k,"") or "") for k in ks)
    return f
def NQ_in(r):  # natural_questions style
    return str(r.get("question",{}).get("text","") if isinstance(r.get("question"),dict) else r.get("question",""))

REG = [
 # key, hf_id, config, split, input_fn, output_fn, n
 ("GSM8K","openai/gsm8k","main","test", J("question"), J("answer"), 400),
 ("MATH-500","HuggingFaceH4/MATH-500",None,"test", J("problem"), J("solution"), 400),
 ("HumanEval","openai/openai_humaneval",None,"test", J("prompt"), J("canonical_solution"), 164),
 ("MBPP","google-research-datasets/mbpp","full","test", J("text"), J("code"), 400),
 ("BBH-boolean","maveriq/bigbenchhard","boolean_expressions","train", J("input"), J("target"), 250),
 ("LongBench-narrativeqa","THUDM/LongBench","narrativeqa","test", J("context","input"), J("answers"), 150),
 ("LongBench-hotpotqa","THUDM/LongBench","hotpotqa","test", J("context","input"), J("answers"), 150),
 ("LongBench-gov_report","THUDM/LongBench","gov_report","test", J("context","input"), J("answers"), 120),
 ("HotpotQA","hotpotqa/hotpot_qa","distractor","validation", J("question"), J("answer"), 300),
 ("TriviaQA-rc","mandarjoshi/trivia_qa","rc.nocontext","validation", J("question"), J("answer"), 300),
 ("MuSiQue","dgslibisey/MuSiQue",None,"validation", J("question"), J("answer"), 300),
 ("Qasper","allenai/qasper",None,"validation", J("title","abstract"), None, 150),
 ("NarrativeQA","deepmind/narrativeqa",None,"test", J("question"), J("answers"), 200),
 ("arXiv-sum","ccdv/arxiv-summarization","section","test", J("article"), J("abstract"), 120),
 ("PubMed-sum","ccdv/pubmed-summarization","section","test", J("article"), J("abstract"), 120),
 ("GovReport-sum","ccdv/govreport-summarization","document","test", J("report"), J("summary"), 100),
 ("MultiNews","alexfabbri/multi_news",None,"test", J("document"), J("summary"), 150),
 ("RAGBench-hotpotqa","galileo-ai/ragbench","hotpotqa","test", J("question"), J("response"), 200),
 ("SWE-bench-Verified","SWE-bench/SWE-bench_Verified",None,"test", J("problem_statement"), J("patch"), 200),
 ("SWE-bench-Lite","SWE-bench/SWE-bench_Lite",None,"test", J("problem_statement"), J("patch"), 300),
 ("RepoBench-py","tianyang/repobench_python_v1.1","cross_file_first","test", J("all_code"), J("next_line"), 200),
 ("LiveCodeBench","livecodebench/code_generation_lite","release_v1","test", J("question_content"), None, 200),
 ("GAIA","gaia-benchmark/GAIA","2023_all","validation", J("Question"), J("Final answer"), 165),
]
