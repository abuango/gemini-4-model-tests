import sys,os,json,time,shutil,subprocess,concurrent.futures as cf,threading,tempfile
sys.dont_write_bytecode=True
import tasks as T, tasks2, tasks3
B=os.path.dirname(os.path.abspath(__file__)); TMO=int(os.environ.get("BENCH_TMO","20")); OUT=os.path.join(B,os.environ.get("BENCH_OUT","results/results.jsonl")); HRUNS=os.path.join(B,"runs_hard"); lk=threading.Lock()
def quota():
    try: o=subprocess.run(["agy","-p","/usage"],capture_output=True,text=True,timeout=60,cwd=B).stdout
    except Exception as e: return None
    for l in o.splitlines():
        if l.startswith("Gemini Models") and "Five Hour" in l: f=int(l.split("\t")[2].rstrip("%"))
        if l.startswith("Gemini Models") and "Weekly" in l: w=int(l.split("\t")[2].rstrip("%"))
    try: return f,w
    except Exception: return None
def one(job):
    model,task,rep=job; q,score=T.TASKS[task]
    d=os.path.join(B,"runs",f"{task}__{model}__{rep}")
    if os.path.exists(d): shutil.rmtree(d)
    seed=T.REPO if task=="repo" else tasks3.SEED_DIRS.get(task)
    if task in tasks3.SEED_DIRS: d=os.path.join(HRUNS,f"{task}__{model}__{rep}"); (os.path.exists(d) and shutil.rmtree(d))
    shutil.copytree(seed,d) if seed else os.makedirs(d)
    cmd=["agy","-p",q,"--model",model,"--output-format","json","--print-timeout",f"{TMO}m"]
    if seed: cmd+=["--mode","auto","--sandbox"]
    t=time.time(); r=dict(model=model,task=task,rep=rep,at=time.strftime("%FT%TZ",time.gmtime()))
    try:
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=TMO*60+60,cwd=d,stdin=subprocess.DEVNULL); r["wall"]=round(time.time()-t,1)
        o=json.loads(p.stdout[p.stdout.index("{"):]); r.update(status=o.get("status"),dur=o.get("duration_seconds"),turns=o.get("num_turns"),usage=o.get("usage"),response=o.get("response"))
        s,det=score(o.get("response"),d); r.update(score=s,detail=det)
    except Exception as e:
        r.update(status="HARNESS_ERROR",err=str(e)[:200],wall=round(time.time()-t,1),stderr=(locals().get("p") and p.stderr[-300:]) or "")
    with lk: open(OUT,"a").write(json.dumps(r)+"\n")
    return r
if __name__=="__main__":
    plan=json.load(open(sys.argv[1])); floor=int(sys.argv[2]); W=int(sys.argv[3]); wf=int(sys.argv[4]) if len(sys.argv)>4 else 85
    done=set()
    if os.path.exists(OUT): done={(x["model"],x["task"],x["rep"]) for x in map(json.loads,open(OUT)) if x.get("status")=="SUCCESS"}
    jobs=[tuple(j) for j in plan if tuple(j) not in done]; print(len(jobs),"jobs",quota(),flush=True)
    for i in range(0,len(jobs),W*2):
        with cf.ThreadPoolExecutor(W) as ex:
            for r in ex.map(one,jobs[i:i+W*2]): print(r["model"],r["task"],r["rep"],r.get("status"),r.get("score"),r.get("dur"),(r.get("usage") or {}).get("thinking_tokens"),r.get("err",""),flush=True)
        qn=quota(); print("quota",qn,flush=True)
        print("after batch",time.strftime("%FT%TZ",time.gmtime()),flush=True)
        if qn and (qn[0]<floor or qn[1]<wf): print("STOP: quota floor"); break
