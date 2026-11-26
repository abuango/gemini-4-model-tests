import random, json
def make(seed, n=150, m=5, f=6):
    r = random.Random(seed * 7919 + 13)
    setup = [[0 if a == b else r.randint(4, 30) for b in range(f)] for a in range(f)]
    jobs = []; hor = n * 12 // m
    for i in range(n):
        base = r.randint(4, 24); rel = r.randint(0, hor * 7 // 10)
        jobs.append(dict(id=i, fam=r.randrange(f), rel=rel, due=rel + base + r.randint(10, 160), w=r.choice([1, 1, 2, 3, 5, 9]), proc=[max(1, int(base * r.uniform(.6, 1.8))) for _ in range(m)]))
    return dict(machines=m, init=[r.randrange(f) for _ in range(m)], setup=setup, jobs=jobs)
def cost(inst, seqs):
    J = inst["jobs"]
    assert len(seqs) == inst["machines"] and sorted(x for s in seqs for x in s) == list(range(len(J))), "every job must appear exactly once"
    tard = st = mk = 0
    for k, s in enumerate(seqs):
        t, fam = 0, inst["init"][k]
        for x in s:
            j = J[x]; u = inst["setup"][fam][j["fam"]]; st += u
            t = max(t + u, j["rel"]) + j["proc"][k]; fam = j["fam"]; tard += j["w"] * max(0, t - j["due"])
        mk = max(mk, t)
    return tard + 3 * st + 2 * mk
