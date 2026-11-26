from fractions import Fraction as F


def rhe(x):
    return round(F(x))


class Ledger:
    def __init__(self):
        self.acct, self.ent, self.holds, self.ids = {}, {}, {}, set()
        self.closed, self.rej, self.late, self.t = {}, [], 0, 0

    def first_open(self):
        p = 0
        while p in self.closed:
            p += 1
        return p

    def is_closed(self, day):
        return day // 30 in self.closed

    def bal(self, a):
        return sum(e["amt"] for e in self.ent.values() if e["acct"] == a)

    def floor(self, a):
        kind, lim = self.acct[a]
        return 0 if kind == "prepaid" else -lim

    def held(self, a=None):
        return sum(h["amt"] for h in self.holds.values()
                   if not h["cap"] and self.t <= h["exp"] and a in (None, h["acct"]))

    def funds(self, a, x):
        return x >= 0 or self.bal(a) - self.held(a) - self.floor(a) + x >= 0

    def add(self, i, a, amt, day, cat, role="base", of=None):
        if self.is_closed(day):
            day = 30 * self.first_open()
            self.late += 1
        self.ent[i] = dict(acct=a, amt=amt, day=day, cat=cat, role=role, of=of, rev=False)

    def current(self, i):
        return self.ent[i]["amt"] + sum(e["amt"] for e in self.ent.values()
                                        if e["role"] == "adj" and e["of"] == i)

    def do_open(self, e):
        if e["acct"] in self.acct:
            return "dup"
        self.acct[e["acct"]] = (e["kind"], e["limit"])

    def do_post(self, e):
        if e["acct"] not in self.acct:
            return "acct"
        if e["cat"] != "fee" and not self.funds(e["acct"], e["amt"]):
            return "funds"
        self.add(e["id"], e["acct"], e["amt"], e["eff"], e["cat"])

    def do_split(self, e):
        if e["acct"] not in self.acct:
            return "acct"
        if not self.funds(e["acct"], e["amt"]):
            return "funds"
        total, n = sum(e["weights"]), abs(e["amt"])
        exact = [F(n * w, total) for w in e["weights"]]
        parts = [x.numerator // x.denominator for x in exact]
        order = sorted(range(len(parts)), key=lambda k: (-(exact[k] - parts[k]), k))
        for k in order[:n - sum(parts)]:
            parts[k] += 1
        sign = -1 if e["amt"] < 0 else 1
        for k, v in enumerate(parts):
            self.add(f"{e['id']}#{k}", e["acct"], sign * v, e["eff"], "split")

    def do_transfer(self, e):
        s, d, amt = e["src"], e["dst"], e["amt"]
        if s not in self.acct or d not in self.acct:
            return "acct"
        if s == d:
            return "same"
        if not self.funds(s, -amt):
            return "funds"
        if self.acct[d][0] == "credit" and self.bal(d) + amt > self.acct[d][1]:
            return "cap"
        self.add(e["id"] + ".s", s, -amt, e["eff"], "xfer")
        self.add(e["id"] + ".d", d, amt, e["eff"], "xfer")
        self.add(e["id"] + ".f", s, -max(1, rhe(F(7 * amt, 1000))), e["eff"], "fee")

    def changeable(self, i):
        x = self.ent.get(i)
        return x is not None and not x["rev"] and x["role"] == "base"

    def do_amend(self, e):
        i = e["id"]
        if not self.changeable(i):
            return "state"
        x = self.ent[i]
        diff = e["amt"] - self.current(i)
        if x["cat"] != "fee" and not self.funds(x["acct"], diff):
            return "funds"
        if diff == 0:
            return None
        if not self.is_closed(x["day"]):
            x["amt"] += diff
        else:
            k = 1 + sum(1 for y in self.ent.values() if y["role"] == "adj" and y["of"] == i)
            self.add(f"{i}~{k}", x["acct"], diff, self.t, x["cat"], "adj", i)

    def do_reverse(self, e):
        i = e["id"]
        if not self.changeable(i):
            return "state"
        x = self.ent[i]
        diff = -self.current(i)
        if x["cat"] != "fee" and not self.funds(x["acct"], diff):
            return "funds"
        if self.is_closed(x["day"]):
            self.add(i + "!", x["acct"], diff, self.t, x["cat"], "contra", i)
            x["rev"] = True
        else:
            for k in [k for k, y in self.ent.items() if k == i or (y["role"] == "adj" and y["of"] == i)]:
                del self.ent[k]

    def do_hold(self, e):
        if e["acct"] not in self.acct:
            return "acct"
        if not self.funds(e["acct"], -e["amt"]):
            return "funds"
        self.holds[e["id"]] = dict(acct=e["acct"], amt=e["amt"], exp=e["exp"], cap=False)

    def do_capture(self, e):
        h = self.holds.get(e["hold"])
        if h is None or h["cap"] or self.t > h["exp"] or e["amt"] > h["amt"]:
            return "hold"
        h["cap"] = True
        self.add(e["id"], h["acct"], -e["amt"], self.t, "cap", "capture")

    def do_close(self, e):
        p = e["period"]
        if p != self.first_open() or self.t < 30 * (p + 1):
            return "period"
        last, nxt, new, closing = 30 * p + 29, 30 * (p + 1), [], {}
        for a in sorted(self.acct):
            mine = [x for x in self.ent.values() if x["acct"] == a]
            end = closing[a] = sum(x["amt"] for x in mine if x["day"] <= last)
            avg = F(sum(x["amt"] for d in range(30 * p, nxt) for x in mine if x["day"] <= d), 30)
            if self.acct[a][0] == "credit":
                if avg < 0:
                    v = -avg
                    due = min(v, 10000) * F(1, 100) + min(max(v - 10000, 0), 40000) * F(15, 1000)
                    due = rhe(due + max(v - 50000, 0) * F(2, 100))
                    if due:
                        new.append((f"int:{p}:{a}", a, -due, "int"))
            else:
                if avg >= 5000:
                    b = avg * F(25, 10000)
                    new.append((f"int:{p}:{a}", a, b.numerator // b.denominator, "int"))
                active = any(30 * p <= x["day"] <= last and x["cat"] not in ("fee", "int") for x in mine)
                if end > 0 and not active:
                    new.append((f"dor:{p}:{a}", a, -min(50, end), "fee"))
        for i, a, amt, cat in new:
            self.add(i, a, amt, nxt, cat, "close")
        self.closed[p] = closing


def settle(events):
    L = Ledger()
    for e in events:
        L.t = e["t"]
        op = e["op"]
        takes = op in ("post", "transfer", "split", "hold", "capture")
        code = "dup" if takes and e["id"] in L.ids else getattr(L, "do_" + op)(e)
        if code:
            key = e["acct"] if op == "open" else str(e["period"]) if op == "close" else e["id"]
            L.rej.append([key, code])
        elif takes:
            L.ids.add(e["id"])
    return {"balances": {a: L.bal(a) for a in L.acct},
            "closed": {str(p): c for p, c in L.closed.items()},
            "late": L.late,
            "fees": -sum(x["amt"] for x in L.ent.values() if x["cat"] == "fee"),
            "live": len(L.ent), "held": L.held(), "rejects": L.rej}
