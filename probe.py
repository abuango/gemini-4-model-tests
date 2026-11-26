import sys; sys.dont_write_bytecode=True
import tasks as T, run as R, json, concurrent.futures as cf
base=T.REASON_Q[len(T.NOTOOLS):]
V=dict(direct=T.NOTOOLS+base, notools="Do not use any tools, do not run commands, and do not create files. Put your final answer in your reply.\n\n"+base, plain=base.replace("Solve three problems","Work out three problems yourself without using tools"))
for k,q in V.items(): T.TASKS["probe_"+k]=(q,T.s_reason)
jobs=[(m,"probe_"+k,1) for k in V for m in ("gemini-4-argon-low","gemini-4-argon-medium","gemini-4-argon-high")]
R.OUT=R.OUT.replace("results.jsonl","probe.jsonl")
with cf.ThreadPoolExecutor(5) as ex:
    for r in ex.map(R.one,jobs): print(r["model"],r["task"],r.get("status"),r.get("score"),r.get("dur"),(r.get("usage") or {}).get("thinking_tokens"),(r.get("usage") or {}).get("output_tokens"),r.get("err",""),flush=True)
