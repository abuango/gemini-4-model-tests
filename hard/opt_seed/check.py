import json, subprocess, sys, time

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

if __name__ == "__main__":
    for p in sys.argv[1:]:
        raw = open(p).read(); t = time.time()
        o = subprocess.run([sys.executable, "solve.py"], input=raw, capture_output=True, text=True, timeout=12)
        print(p, "cost", cost(json.loads(raw), json.loads(o.stdout)), "seconds", round(time.time() - t, 1))
