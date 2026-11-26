import sys,random
sys.path.insert(0,sys.argv[1]); sys.dont_write_bytecode=True
from fractions import Fraction
def ref(total,w):
    if total<0: return [-x for x in ref(-total,w)]
    s=sum(w)
    if s==0: w=[1]*len(w); s=len(w)
    ex=[Fraction(total*x,s) for x in w]; p=[int(e) for e in ex]; left=total-sum(p)
    for i in sorted(range(len(w)),key=lambda i:(-(ex[i]-p[i]),i))[:left]: p[i]+=1
    return p
ok=n=0
def chk(f):
    global ok,n; n+=1
    try: ok+=bool(f())
    except Exception: pass
from shop.money import allocate
from shop.report import cost_per_team
from shop.refund import refund_lines
from shop.invoice import invoice_total
chk(lambda:list(allocate(100,[333,333,334]))==ref(100,[333,333,334]))
chk(lambda:list(allocate(-100,[333,333,334]))==ref(-100,[333,333,334]))
chk(lambda:list(allocate(5,[0,0,0]))==[2,2,1])
chk(lambda:list(allocate(10**17+1,[1,2,4]))==ref(10**17+1,[1,2,4]))
chk(lambda:list(allocate(10,[1,1,1,1]))==[3,3,2,2])
chk(lambda:cost_per_team(1000,{"a":3,"b":3,"c":1})==dict(zip("abc",ref(1000,[3,3,1]))))
chk(lambda:sum(v for _,v in refund_lines([("x",199),("y",301),("z",77)],100))==-100)
chk(lambda:invoice_total([("x",199),("y",301),("z",77)],100)==477)
r=random.Random(3); C=[(r.randint(-5000,5000),[r.randint(0,900) for _ in range(r.randint(1,7))]) for _ in range(300)]
chk(lambda:all(list(allocate(t,w))==ref(t,w) for t,w in C))
chk(lambda:list(allocate(0,[5,6]))==[0,0])
print(f"RESULT {ok}/{n}")
