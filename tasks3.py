import os, re, sys, json, subprocess, tempfile, threading, textwrap
B = os.path.dirname(os.path.abspath(__file__)); H = os.path.join(B, "hard"); sys.path.insert(0, H)
import tasks as T, ref, gen, mut, opt_inst
NT = "Do not use any tools, do not run commands, and do not create files. Put your final answer in your reply.\n\n"
SPEC = open(os.path.join(H, "SPEC.md")).read()
LK = threading.Lock()
PROFILE = '(version 1)(allow default)(deny network*)(deny file-write*)(allow file-write* (subpath "/dev"))'
def py(code_path, stdin, timeout):
    return subprocess.run(["/usr/bin/sandbox-exec", "-p", PROFILE, sys.executable, "-I", "-B", code_path], input=stdin, capture_output=True, text=True, timeout=timeout, cwd="/")
def block(r):
    m = re.findall(r"```(?:python)?\s*\n(.*?)```", r or "", re.S); return max(m, key=len) if m else (r or "")
def js(r):
    s = r or ""; return json.loads(s[s.index("{"):s.rindex("}") + 1])
# ---- h_impl: implement the spec
SEEDS = list(range(5000, 5200))
DRV = "\nif __name__=='__main__':\n import json,sys\n out=[]\n for e in json.load(sys.stdin):\n  try: out.append(settle(e))\n  except Exception as x: out.append(repr(x))\n print('@@'+json.dumps(out))\n"
def s_impl(r, d):
    ev = [gen.scenario(s) for s in SEEDS]
    with tempfile.TemporaryDirectory() as t:
        p = os.path.join(t, "x.py"); open(p, "w").write(block(r) + DRV)
        try: o = py(p, json.dumps(ev), 120); got = json.loads(o.stdout.split("@@")[1])
        except Exception as x: return 0.0, {"err": repr(x)[:200]}
    want = [json.loads(json.dumps(ref.settle(e))) for e in ev]; bad = [k for k, (a, b) in enumerate(zip(got, want)) if a != b]
    f = lambda k: [q for q in want[k] if not isinstance(got[k], dict) or got[k].get(q) != want[k][q]]
    return 1 - len(bad) / len(ev), {"passed": len(ev) - len(bad), "of": len(ev), "first_bad": [(SEEDS[k], f(k)) for k in bad[:4]]}
IMPL = NT + "Return only the complete ledger.py in one ```python block.\n\n" + SPEC
# ---- h_review: 12 deviations from the spec
PICK = ["hold_exp", "tier_edge", "dorm_fee_cat", "split_tie", "fee_min", "amend_current", "reverse_current", "avg_open", "capture_role", "dup_taken", "cap_avail", "rev_flag"]
def build_review():
    src, marks = mut.SRC, {}
    for n in PICK:
        a, b = mut.MUT[n]; assert src.count(a) == 1, n; src = src.replace(a, b)
    L = src.split("\n")
    for n in PICK:
        a, b = mut.MUT[n]
        if n == "rev_flag":
            i = next(k for k, l in enumerate(L) if '"contra", i)' in l) + 1; marks[n] = [i - 1, i, i + 1]; continue
        first = next(l for l in b.split("\n") if l.strip()); hit = [k + 1 for k, l in enumerate(L) if first.strip() in l]
        assert len(hit) == 1, (n, hit); marks[n] = list(range(hit[0] - 1, hit[0] + 2 + b.count("\n")))
    return src, marks
RSRC, RKEY = build_review()
def s_review(r, d):
    try: bugs = js(r)["bugs"]
    except Exception as x: return 0.0, {"err": repr(x)[:200]}
    lines = [int(b["line"]) for b in bugs]; found = {n for n, k in RKEY.items() if any(l in k for l in lines)}
    fp = [l for l in lines if not any(l in k for k in RKEY.values())]; p = (len(lines) - len(fp)) / len(lines) if lines else 0; c = len(found) / len(RKEY)
    return (2 * p * c / (p + c) if p + c else 0.0), {"found": sorted(found), "missed": sorted(set(RKEY) - found), "false": fp}
REVIEW = NT + 'The Python module below should implement the specification, but it departs from it in several places. List every place where its behaviour differs from the specification. Return only a JSON object: {"bugs": [{"line": <integer>, "why": "<one sentence>"}]}. A false report costs as much as a missed one.\n\n' + SPEC + "\n# Module\n\n" + "\n".join(f"{i+1:3}| {l}" for i, l in enumerate(RSRC.split("\n")))
# ---- h_trace: work the spec by hand
TR = gen.scenario(7301, 90)
def flat(o): 
    x = {f"balances.{a}": v for a, v in o["balances"].items()}
    x.update({f"closed.{p}.{a}": v for p, c in o["closed"].items() for a, v in c.items()})
    x.update({k: o[k] for k in ("late", "fees", "live", "held")}); x["rejects"] = o["rejects"]; return x
def s_trace(r, d):
    w = flat(json.loads(json.dumps(ref.settle(TR))))
    try: g = flat(js(r))
    except Exception as x: return 0.0, {"err": repr(x)[:200]}
    ok = [k for k in w if g.get(k) == w[k]]; return len(ok) / len(w), {"right": len(ok), "of": len(w), "wrong": [k for k in w if k not in ok][:12]}
TRACE = NT + "Work out by hand the report that `settle` returns for the events below, following the specification exactly. Return only the report as a JSON object, with every account in `balances` and every closed period in `closed`.\n\n" + SPEC + "\n# Events\n\n" + "\n".join(json.dumps(e) for e in TR)
# ---- h_opt: open-ended optimisation, tools allowed
OKEY = {int(k): v for k, v in json.load(open(os.path.join(H, "opt_key.json"))).items()}
def s_opt(r, d):
    p = os.path.join(d, "solve.py"); det = {}
    if not os.path.exists(p): return 0.0, {"err": "no solve.py"}
    sc = []
    with LK:
        for s, best in OKEY.items():
            I = opt_inst.make(s)
            try: o = py(p, json.dumps(I), 12); c = opt_inst.cost(I, json.loads(o.stdout)); det[s] = c; sc.append(best / c)
            except Exception as x: det[s] = repr(x)[:120]; sc.append(0.0)
    return sum(sc) / len(sc), det
OPT = textwrap.dedent("""\
    Write solve.py in this folder. It reads one problem instance as JSON from standard input and prints a JSON list of machines, each a list of job ids in the order that machine runs them. Every job must appear exactly once. Work only inside this folder, and don't use the network.

    Each machine runs one job at a time. Machine k starts set up for family init[k]. Before a job, it needs setup[previous family][job family] time units, which may happen before the job's release time rel. The job then starts at the later of its release time and the end of the setup, and takes proc[k]. The cost is the sum over jobs of w * max(0, completion - due), plus 3 times the total setup time, plus 2 times the latest completion time. Make the cost as low as you can.

    solve.py may use only the Python 3 standard library and a single process, and must finish within 10 seconds on each instance (it is stopped at 12). It will be scored on hidden instances of the same size and kind as example1.json to example3.json, against a strong reference solution. Run `python3 check.py example1.json example2.json example3.json` to see your cost. Finish when you think you can't improve it much further.""")
T.TASKS.update(h_impl=(IMPL, s_impl), h_review=(REVIEW, s_review), h_trace=(TRACE, s_trace), h_opt=(OPT, s_opt))
SEED_DIRS = {"h_opt": os.path.join(H, "opt_seed")}
