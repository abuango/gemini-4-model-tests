import subprocess, json, opt_inst, concurrent.futures as cf
def txt(I):
    o=[f"{len(I['jobs'])} {I['machines']} {len(I['setup'])}"," ".join(map(str,I['init']))]+[" ".join(map(str,r)) for r in I['setup']]
    return "\n".join(o+[" ".join(map(str,[j['fam'],j['rel'],j['due'],j['w']]+j['proc'])) for j in I['jobs']])
def run(a): s,lim,k=a; return s,int(subprocess.run(["./ref_sa",str(lim),str(k)],input=txt(opt_inst.make(s)),capture_output=True,text=True).stdout.split()[0])
def greedy(I):
    seqs=[[] for _ in range(I['machines'])]
    st=[(0,f) for f in I['init']]
    for j in sorted(I['jobs'],key=lambda j:j['due']):
        c=[]
        for k,(t,f) in enumerate(st): c.append((max(t+I['setup'][f][j['fam']],j['rel'])+j['proc'][k],k))
        e,k=min(c); seqs[k].append(j['id']); st[k]=(e,j['fam'])
    return opt_inst.cost(I,seqs)
seeds=[901,902,903,904,905,906]
with cf.ThreadPoolExecutor(6) as ex: res=list(ex.map(run,[(s,l,k) for s in seeds for l,k in((20,1),(20,2),(60,3))]))
best={s:min(v for q,v in res if q==s) for s in seeds}
for s in seeds: print(s,"ref",sorted(v for q,v in res if q==s),"greedy",greedy(opt_inst.make(s)))
json.dump(best,open("opt_key.json","w"))
