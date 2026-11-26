import re, gen, ref
import os
SRC = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ref.py")).read()
M = [("amount >= avg", "if avg >= 5000", "if avg > 5000 - 1 and avg > 5000"),]
MUT = {  # name: (old, new) exact, unique in ref.py
 "hold_exp": ("self.t <= h[\"exp\"] and a in", "self.t < h[\"exp\"] and a in"),
 "tier_edge": ("F(15, 1000)", "F(1, 100)"),
 "int_round": ("due = rhe(due + max(v - 50000, 0) * F(2, 100))", "due = rhe(due) + rhe(max(v - 50000, 0) * F(2, 100))"),
 "dorm_fee_cat": ('not in ("fee", "int")', 'not in ("fee",)'),
 "dorm_min": ("-min(50, end)", "-min(50, abs(avg))"),
 "split_tie": ("(-(exact[k] - parts[k]), k)", "(-(exact[k] - parts[k]), -k)"),
 "fee_min": ("-max(1, rhe(F(7 * amt, 1000)))", "-rhe(F(7 * amt, 1000))"),
 "cap_balance": ("self.bal(d) + amt > self.acct[d][1]", "self.bal(d) + amt >= self.acct[d][1] + 0"),
 "current_adj": ('if y["role"] == "adj" and y["of"] == i)\n            self.add(f"{i}~{k}"', 'if y["of"] == i)\n            self.add(f"{i}~{k}"'),
 "amend_current": ('diff = e["amt"] - self.current(i)', 'diff = e["amt"] - x["amt"]'),
 "reverse_current": ("diff = -self.current(i)", 'diff = -x["amt"]'),
 "avg_open": ("avg = F(sum(x[\"amt\"] for d in range(30 * p, nxt) for x in mine if x[\"day\"] <= d), 30)", "avg = F(sum(x[\"amt\"] for d in range(30 * p, nxt) for x in mine if x[\"day\"] < d or x[\"day\"] == 30 * p), 30)"),
 "rhe_up": ("return round(F(x))", "return int(F(x) + F(1, 2))"),
 "late_removed": ("self.late += 1", "self.late += role == 'base'"),
 "cap_avail": ('return x >= 0 or self.bal(a) - self.held(a)', 'return self.bal(a) - self.held(a)'),
 "capture_role": ('self.t, "cap", "capture")', 'self.t, "cap")'),
 "capture_release": ('or self.t > h["exp"] or', 'or self.t >= h["exp"] or'),
 "dup_taken": ('        elif takes:\n            L.ids.add(e["id"])', '        if takes:\n            L.ids.add(e["id"])'),
 "close_sort": ("sorted(self.acct)", "list(self.acct)"),
 "bonus_round": ("b.numerator // b.denominator, \"int\"", "rhe(b), \"int\""),
 "rev_flag": ('            x["rev"] = True\n', ""),
 "split_sign": ("exact = [F(n * w, total)", "exact = [F(e['amt'] * w, total)"),
}
def load(src):
    ns = {}; exec(compile(src, "m", "exec"), ns); return ns["settle"]
if __name__ == "__main__":
    ev = [gen.scenario(s) for s in range(400)]; want = [ref.settle(e) for e in ev]
    for n, (a, b) in MUT.items():
        assert SRC.count(a) == 1, (n, SRC.count(a))
        try: f = load(SRC.replace(a, b)); d = sum(1 for e, w in zip(ev, want) if f(e) != w)
        except Exception as x: d = "ERR %r" % x
        print(f"{n:18} differs on {d}/400")
