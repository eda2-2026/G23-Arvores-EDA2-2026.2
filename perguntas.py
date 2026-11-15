"""Gerador de perguntas e leitura de respostas."""
import random

from arvores import new_tree
from textos import opts_for


def make_question(lv):
    kind = lv["tree"] if lv["tree"] != "MIX" else random.choice(["AVL", "RB"])
    op = lv["op"] if lv["op"] != "MIX" else random.choice(["insert", "delete"])
    qt = lv["q"]
    if qt == "MIX":
        choices = ["case", "preorder"]
        if kind == "AVL" and op == "insert":
            choices.append("click")
        qt = random.choice(choices)
    opts = opts_for(kind, op)
    pool = [c for c in (lv["allowed"] or list(opts)) if c in opts]
    target = random.choice(pool)
    if kind == "RB" and op == "insert" and target == "ROOT":
        target = "NONE"
    for attempt in range(6000):
        n = random.randint(*lv["n"])
        keys = random.sample(range(1, 100), n)
        T = new_tree(kind)
        for k in keys:
            T.insert(k)
        before = T.snapshot()
        if op == "insert":
            k = random.choice([x for x in range(1, 100) if x not in keys])
            if qt == "click":
                naive = new_tree("AVL")
                for kk in keys:
                    naive.insert(kk)
                naive.insert(k, rebalance=False)
                before = naive.snapshot()
            T.insert(k)
        else:
            k = random.choice(keys)
            T.delete(k)
        code = T.first_code()
        if qt == "case":
            if code not in pool or (attempt < 4000 and code != target):
                continue
        elif qt == "click":
            if code == "NONE":
                continue
        elif code == "NONE" and random.random() < 0.8:
            continue
        return {
            "kind": kind, "op": op, "qt": qt, "key": k, "keys": keys,
            "before": before, "after": T.snapshot(), "code": code,
            "events": list(T.events),
            "node": T.events[0][1] if T.events else None,
            "pre": T.preorder(),
        }
    raise RuntimeError("não consegui gerar pergunta")


def parse_preorder(text, colored):
    res = []
    for t in text.replace(",", " ").split():
        col = "B"
        if colored and t[-1] in "vVrR":
            col = "R"
            t = t[:-1]
        if not t.isdigit():
            return None
        res.append((int(t), col) if colored else int(t))
    return res
