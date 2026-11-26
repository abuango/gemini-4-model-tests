import json,statistics as st
R=[json.loads(l) for l in open('results/results.jsonl')]
now={'hydrogen':(1.5,7.5),'neon':(3,15),'carbon':(2,10),'argon':(2,10)}; dec={**now,'carbon':(4,20),'argon':(4,20)}
core=['code2','review','reason2','longctx2','instruct','repo']
def fam(m): return next((k for k in now if k in m),None)
def c(r,p,inp=True):
    u=r['usage'];i,o=p[fam(r['model'])];cr=u.get('cache_read_tokens',0) or 0
    return ((u['input_tokens']*i+cr*i*0.05) if inp else 0)/1e6+u['output_tokens']*o/1e6
tot=[(r['usage']['input_tokens'],r['usage']['output_tokens'],r['usage']['thinking_tokens'],r['usage']['cache_read_tokens'],r['usage']['total_tokens'],r['task']) for r in R]
print("total==in+out",sum(a+b==e for a,b,_,_,e,_ in tot),"total==in+out+cache",sum(a+b+d==e for a,b,_,d,e,_ in tot),"thinking>out",sum(x>b for _,b,x,_,_,_ in tot),len(tot))
print("cache runs",sum(d>0 for *_,d,_,_ in tot)); print([t for t in tot if t[3]>0][:3])
print("sum of 6 shared tasks, output only (now|dec), incl. input (now|dec), sum of median secs")
for m in sorted({r['model'] for r in R}):
    if not fam(m): continue
    S=[0]*5
    for t in core:
        x=[r for r in R if r['model']==m and r['task']==t]
        for k,f in enumerate((lambda r:c(r,now,0),lambda r:c(r,dec,0),lambda r:c(r,now),lambda r:c(r,dec),lambda r:r['dur'])): S[k]+=st.median(map(f,x))
    print(f"{m:26} out ${S[0]:.2f}|${S[1]:.2f}  all ${S[2]:.2f}|${S[3]:.2f}  {S[4]/60:.1f} min")
