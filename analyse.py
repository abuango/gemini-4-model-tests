import json,collections,statistics as st
R=[json.loads(l) for l in open('results/results.jsonl')]
P=[tuple(x) for x in json.load(open('plan.json'))]
done=collections.Counter((r['model'],r['task']) for r in R)
need=collections.Counter((m,t) for m,t,_ in P)
print("dups",[k for k,v in collections.Counter((r['model'],r['task'],r['rep']) for r in R).items() if v>1])
print("cell coverage",collections.Counter(done[k] for k in need), "zero:",[k for k in need if done[k]==0])
def agg(rs):
    d=[r['dur'] for r in rs]; u=[r['usage'] or {} for r in rs]
    return dict(n=len(rs),score=round(st.mean(r['score'] for r in rs),3),perfect=sum(r['score']>=.9999 for r in rs),
      med=round(st.median(d),1),lo=round(min(d)),hi=round(max(d)),
      think=round(st.median(x.get('thinking_tokens',0) or 0 for x in u)),out=round(st.median(x.get('output_tokens',0) or 0 for x in u)))
M=sorted({m for m,_ in need}); T=sorted({t for _,t in need})
core6=['code2','review','reason2','longctx2','instruct','repo']
main=['gemini-4-hydrogen-high','gemini-4-neon-high','gemini-4-carbon-medium','gemini-4-argon-medium','gemini-4-argon-high','gemini-3.8-flash-high']
print("\n== mean of task means, shared 6 tasks, all models (missing cells flagged)")
for m in M:
    c=[[r for r in R if r['model']==m and r['task']==t] for t in core6]
    miss=[t for t,x in zip(core6,c) if not x]; c=[x for x in c if x]
    if c: print(f"{m:28}",f"n={sum(map(len,c)):2}",f"score={st.mean(st.mean(r['score'] for r in x) for x in c):.3f}",f"med-of-task-med={st.mean(st.median(r['dur'] for r in x) for x in c):.0f}s(mean)",f"think={st.mean(st.median((r['usage'] or {}).get('thinking_tokens',0) or 0 for r in x) for x in c):.0f}","MISSING",miss)
print("\n== per task x model")
for t in T:
    print("--",t)
    for m in M:
        x=[r for r in R if r['model']==m and r['task']==t]
        if x: print(f"  {m:28}",agg(x),[round(r['score'],2) for r in x])
print("\n== imperfect"); 
for r in R:
    if r['score']<.9999: print(r['model'],r['task'],r['rep'],round(r['score'],2),json.dumps(r['detail'])[:230])
print("\nusage sample",R[0]['usage'])
