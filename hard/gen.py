import random, collections
import ref
def scenario(seed, n=70):
    r = random.Random(seed); ev = []; t = 0; names = ["ash", "birch", "cedar", "dune"]; k = 0; ents = []; holds = []; nextp = 0
    for a in names[:r.choice([3, 4])]:
        ev.append(dict(op="open", t=0, acct=a, kind=r.choice(["prepaid", "credit"]), limit=r.choice([8000, 20000, 60000, 90000])))
    accts = [e["acct"] for e in ev]
    kinds = {e["acct"]: e for e in ev}
    def A(): return r.choice(accts) if r.random() > .03 else "zzz"
    def eff(): return max(0, t - r.choice([0, 0, 1, 3, 9, 25, 40, 55])) + (r.choice([0, 0, 0, 4, 20]))
    for a in accts:
        k += 1; ev.append(dict(op="post", t=0, id=f"e{k}", acct=a, amt=r.randint(500, 30000), eff=0, cat="pay")); ents.append(f"e{k}")
    while len(ev) < n:
        t += r.choice([0, 0, 1, 1, 2, 4, 7]); x = r.random(); k += 1; i = f"e{k}"
        if r.random() < .03 and k > 5: i = f"e{r.randint(1, k - 1)}"
        if x < .24:
            ev.append(dict(op="post", t=t, id=i, acct=A(), amt=r.choice([-1, -1, 1]) * r.randint(1, r.choice([300, 9000, 45000])), eff=eff(), cat=r.choice(["pay", "buy", "buy", "fee"]))); ents.append(i)
        elif x < .33:
            w = [r.randint(1, 9) for _ in range(r.randint(2, 4))]
            ev.append(dict(op="split", t=t, id=i, acct=A(), amt=r.choice([-1, 1]) * r.randint(1, 5000), eff=eff(), weights=w)); ents += [f"{i}#{j}" for j in range(len(w))]
        elif x < .47:
            ev.append(dict(op="transfer", t=t, id=i, src=A(), dst=A(), amt=r.randint(1, r.choice([200, 6000, 25000])), eff=eff())); ents += [i + s for s in (".s", ".d", ".f")]
        elif x < .62 and ents:
            ev.append(dict(op="amend", t=t, id=r.choice(ents + ents[-6:]), amt=r.choice([-1, 1, 1]) * r.randint(1, 9000)))
        elif x < .72 and ents:
            ev.append(dict(op="reverse", t=t, id=r.choice(ents + ents[-6:])))
        elif x < .80:
            ev.append(dict(op="hold", t=t, id=i, acct=A(), amt=r.randint(1, 9000), exp=t + r.choice([1, 5, 15, 40]))); holds.append(i)
        elif x < .88 and holds:
            ev.append(dict(op="capture", t=t, id=i, hold=r.choice(holds[-4:]), amt=r.randint(1, 4000))); ents.append(i)
        else:
            if r.random() < .75 and t < 30 * (nextp + 1): t = 30 * (nextp + 1) + r.randint(0, 6)
            p = nextp if r.random() < .9 else nextp + r.choice([-1, 1]); ev.append(dict(op="close", t=t, period=p))
            if p == nextp and t >= 30 * (p + 1): nextp += 1
    return ev
if __name__ == "__main__":
    c = collections.Counter(); st = collections.Counter()
    for s in range(300):
        ev = scenario(s); o = ref.settle(ev); c.update(x[1] for x in o["rejects"]); st["closed"] += len(o["closed"]); st["late"] += o["late"]; st["held"] += o["held"] > 0; st["live"] += o["live"]
    print(c, st)
