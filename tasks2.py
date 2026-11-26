import json,random,itertools,subprocess,sys,datetime as dt,re
import tasks as T
from tasks import jgrab,code_block
NT="Do not use any tools, do not run commands, and do not create files. Put your final answer in your reply.\n\n"
def strip(q): return NT+q[len(T.NOTOOLS):] if q.startswith(T.NOTOOLS) else q
# ---- longctx2: every asked setting is wrong under "last set wins"
def mklog2():
    r=random.Random(23); keys=[f"svc{n}.{w}" for n,w in itertools.product((12,34,47,58,71,86),("pool","ttl","retry","batch","quota","shard","lease"))]
    base={k:r.randint(1,999) for k in keys}; L=[f"BASE {k} = {base[k]}" for k in keys]; sets={k:[] for k in keys}; rev=set(); ids=[]
    for n in range(1,3201):
        c=f"C{n:04d}"; x=r.random()
        if x<.3 and ids:
            lk=r.choice(keys); live=[c2 for c2,_ in sets[lk] if c2 not in rev]
            t=live[-1] if (r.random()<.6 and live) else r.choice(ids[-160:])
            if t in rev: L.append(f"{c} note: {t} was already reverted")
            else: rev.add(t); L.append(f"{c} revert {t}")
        elif x<.36: L.append(f"{c} note: reviewed {r.choice(keys)}, proposed value {r.randint(1,999)} rejected")
        else: k=r.choice(keys); v=r.randint(1,999); sets[k].append((c,v)); ids.append(c); L.append(f"{c} set {k} = {v}")
    fin={k:next((v for c,v in reversed(sets[k]) if c not in rev),base[k]) for k in keys}
    hard=[k for k in keys if sets[k] and fin[k]!=sets[k][-1][1]]
    depth=lambda k:next((i for i,(c,_) in enumerate(reversed(sets[k])) if c not in rev),99)
    hard=sorted(hard,key=lambda k:(-depth(k),k))[:10]
    return "\n".join(L),{k:fin[k] for k in hard},{k:depth(k) for k in hard}
LOG2,A2,DEP=mklog2()
HEAD="Below is a configuration change log. BASE lines give starting values. 'set' changes a value. 'revert Cxxxx' cancels that one earlier change: the setting's value becomes the value from its most recent change that has not been reverted, or its BASE value if there is none. A revert can refer to a change that is no longer the latest one for its setting. 'note' lines change nothing.\n\n"
ASK="Return only a JSON object with the final value (integer) of each of these settings: "+", ".join(A2)
L_END=NT+HEAD+LOG2+"\n\nBased on the log above: "+ASK
L_START=NT+ASK+"\n\n"+HEAD+LOG2
def s_l2(t,d):
    o=jgrab(t) or {}; ok={k:o.get(k)==v for k,v in A2.items()}; return sum(ok.values())/len(ok),{"right":sum(ok.values()),"of":len(ok)}
# ---- reason2
def b2():
    p1=0
    for m in range(1<<16):
        R=[(m>>(4*i))&15 for i in range(4)]
        if any(bin(x).count("1")!=2 for x in R): continue
        if any(sum((x>>j)&1 for x in R)!=2 for j in range(4)): continue
        if any(((R[i]&R[i+1])>>j)&3==3 for i in range(3) for j in range(3)): continue
        p1+=1
    p2=sum(1 for p in itertools.permutations(range(1,9)) if p[0]<p[-1] and all(abs(a-b)!=1 for a,b in zip(p,p[1:])) and p.index(1)<p.index(8))
    D=dict(A=4,B=3,C=6,D=2,E=5,F=4,G=3); P=dict(C=["A"],D=["A"],E=["B"],F=["C","E"],G=["D","E"]); best=99
    for o in itertools.permutations(D):
        if any(o.index(x)>o.index(k) for k,v in P.items() for x in v): continue
        for a in itertools.product((0,1),repeat=6):
            f=[0,0]; e={}
            for j,mc in zip(o,(0,)+a): s=max([f[mc]]+[e[x] for x in P.get(j,[])]); e[j]=s+D[j]; f[mc]=e[j]
            best=min(best,max(f))
    I=[(7,13),(4,8),(9,17),(3,5),(6,12),(8,14),(5,9),(2,3)]; p4=0
    for m in range(256):
        S=[i for i in range(8) if m>>i&1]
        if sum(I[i][0] for i in S)<=23 and not(2 in S and 4 in S) and not(0 in S and 5 in S) and not(6 in S and 1 not in S): p4=max(p4,sum(I[i][1] for i in S))
    p5=sum(1 for n in range(1000,10000) if (d:=list(map(int,str(n)))) and len(set(d))==4 and d[0]+d[3]==d[1]+d[2] and n%9==(d[0]*d[1])%9)
    return dict(p1=p1,p2=p2,p3=best,p4=p4,p5=p5)
K2=b2()
R2=NT+"""Solve five problems and return only a JSON object with integer keys p1 to p5.
p1: How many 4 by 4 matrices of 0s and 1s have every row sum and every column sum equal to 2 and contain no 2 by 2 block of adjacent rows and adjacent columns that is all 1s?
p2: How many orderings of the numbers 1 to 8 have no two neighbours that differ by exactly 1, have the first number smaller than the last, and have 1 somewhere before 8?
p3: Seven jobs run on two identical machines, one job per machine at a time, without interruption. Durations: A 4, B 3, C 6, D 2, E 5, F 4, G 3. C and D need A finished; E needs B finished; F needs C and E finished; G needs D and E finished. What is the shortest possible total time?
p4: Eight items have (weight, value): 0 (7,13), 1 (4,8), 2 (9,17), 3 (3,5), 4 (6,12), 5 (8,14), 6 (5,9), 7 (2,3). Choose items with total weight at most 23. Items 2 and 4 cannot both be chosen. Items 0 and 5 cannot both be chosen. Item 6 can be chosen only if item 1 is chosen. What is the largest total value?
p5: How many four-digit numbers with digits a b c d (a is not 0) have four different digits, satisfy a+d = b+c, and leave the same remainder when divided by 9 as the product a times b does?"""
def s_r2(t,d):
    o=jgrab(t) or {}; ok={k:o.get(k)==v for k,v in K2.items()}; return sum(ok.values())/5,{"ok":ok,"got":{k:o.get(k) for k in K2}}
# ---- code2: cron
C2=NT+"""Write one Python function, next_run(expr, after), using only the standard library, and return only the code in a single ```python block with no explanation.

expr is a five-field cron expression: minute hour day-of-month month day-of-week. after is a naive datetime. Return the first datetime strictly later than after, with seconds and microseconds zero, that matches, or None if there is none within 8 years after it.
Each field is a comma-separated list of: *, a number, a range a-b, or any of *, a-b or a followed by /step ("a/step" means from a to the field's maximum). Months accept jan-dec and weekdays accept sun-sat, in any letter case, including inside ranges. Day-of-week is 0 to 7, where 0 and 7 are both Sunday, and a range may end in 7. A range whose start is greater than its end wraps around (for example 22-2 in hours, or fri-mon).
Day rule: if both day-of-month and day-of-week are restricted, a day matches when either matches. A field counts as restricted unless it is exactly "*" or starts with "*/". If only one is restricted, only that one counts; if a "*/n" field is not restricted it must still match together with the other field.
"L" alone in day-of-month means the last day of the month. An invalid expression raises ValueError."""
def ref_next(expr,after):
    F=[(0,59),(0,23),(1,31),(1,12),(0,7)]; MN={m:i+1 for i,m in enumerate("jan feb mar apr may jun jul aug sep oct nov dec".split())}; DN={m:i for i,m in enumerate("sun mon tue wed thu fri sat".split())}
    p=expr.split()
    if len(p)!=5: raise ValueError
    sets=[];L=False
    for i,(f,(lo,hi)) in enumerate(zip(p,F)):
        if i==2 and f.upper()=="L": sets.append(set()); L=True; continue
        S=set(); top=6 if i==4 else hi
        def num(x):
            y=x.lower()
            if i==3 and y in MN: return MN[y]
            if i==4 and y in DN: return DN[y]
            if not re.fullmatch(r"\d+",x): raise ValueError
            n=int(x)
            if not lo<=n<=hi: raise ValueError
            return n
        for part in f.split(","):
            st=1; b=part
            if "/" in part:
                b,s=part.split("/",1)
                if not re.fullmatch(r"\d+",s) or int(s)<1: raise ValueError
                st=int(s)
            if b=="*": seq=list(range(lo,top+1))
            elif "-" in b:
                x,y=map(num,b.split("-",1)); seq=list(range(x,y+1)) if x<=y else list(range(x,top+1))+list(range(lo,y+1))
            else:
                x=num(b); seq=list(range(x,hi+1)) if "/" in part and i!=4 else (list(range(x,max(top,x)+1)) if "/" in part else [x])
            S|=set(seq[::st])
        sets.append({z%7 for z in S} if i==4 else S)
    rd=not(p[2]=="*" or p[2].startswith("*/")); rw=not(p[4]=="*" or p[4].startswith("*/"))
    t=after.replace(second=0,microsecond=0)+dt.timedelta(minutes=1); end=after.replace(year=after.year+8) if not(after.month==2 and after.day==29) else after+dt.timedelta(days=2922)
    while t<=end:
        last=(t.replace(day=28)+dt.timedelta(days=4)).replace(day=1)-dt.timedelta(days=1)
        dm=(t.day==last.day) if L else t.day in sets[2]; dw=(t.isoweekday()%7) in sets[4]
        day=(dm or dw) if rd and rw else (dm and dw)
        if t.month not in sets[3] or not day: t=(t+dt.timedelta(days=1)).replace(hour=0,minute=0); continue
        if t.hour not in sets[1]: t=(t+dt.timedelta(hours=1)).replace(minute=0); continue
        if t.minute not in sets[0]: t+=dt.timedelta(minutes=1); continue
        return t
    return None
CR=["* * * * *","*/15 * * * *","0 0 1 * *","30 4 1,15 * 5","0 22-2 * * *","0 12 * * fri-mon","5/20 * * * *","0 0 29 2 *","0 0 30 2 *","0 0 L * *","0 9 L 2 *","0 0 L * mon","0 0 */10 * mon","0 0 13 * fri","0 0 * jan-mar sun","0 0 * nov-feb *","0 8 * * 5-7","0 8 * * 7","0 8 * * Sat,0","15 10-20/3 * * *","0 0 1-7 * 1","0 0 */2 * */2","59 23 31 12 *","0 6 * FEB-apr TUE","7-3/10 * * * *"]
BAD=["* * * *","60 * * * *","* 24 * * *","* * 0 * *","*/0 * * * *","a * * * *","* * * 13 *","* * * * 8","1- * * * *","* * * foo *"]
AF=["2026-02-28 23:59:30","2024-02-28 12:00:00","2026-12-31 23:59:00","2026-11-25 10:07:12","2027-01-01 00:00:00"]
def s_c2(t,d):
    cases=[(e,a) for e in CR for a in AF]
    src=code_block(t)+"\n\nimport json as _j,sys as _s,datetime as _d\nC=_j.load(_s.stdin)\nO=[]\nfor e,a in C:\n    try:\n        r=next_run(e,_d.datetime.strptime(a,'%Y-%m-%d %H:%M:%S')); O.append(None if r is None else r.strftime('%Y-%m-%d %H:%M:%S'))\n    except ValueError: O.append('VE')\n    except Exception as x: O.append('EX '+repr(x)[:60])\nprint(_j.dumps(O))\n"
    try:
        p=subprocess.run([sys.executable,"-I","-c",src],input=json.dumps(cases+[(b,AF[0]) for b in BAD]),capture_output=True,text=True,timeout=120); O=json.loads(p.stdout.strip().splitlines()[-1])
    except Exception as e: return 0.0,{"err":str(e)[:150]}
    exp=[]
    for e,a in cases:
        r=ref_next(e,dt.datetime.strptime(a,"%Y-%m-%d %H:%M:%S")); exp.append(None if r is None else r.strftime("%Y-%m-%d %H:%M:%S"))
    exp+=["VE"]*len(BAD); g=sum(x==y for x,y in zip(O,exp)); badc=sorted({(cases+[(b,0) for b in BAD])[i][0] for i,(x,y) in enumerate(zip(O,exp)) if x!=y})
    return g/len(exp),{"passed":g,"of":len(exp),"failing":badc}
T.TASKS.update(longctx2=(L_END,s_l2),longctx2_qfirst=(L_START,s_l2),reason2=(R2,s_r2),code2=(C2,s_c2))
for k in ("extract","review","review_tuned","honest","honest_tuned","instruct","code","reason"): T.TASKS[k]=(strip(T.TASKS[k][0]),T.TASKS[k][1])
