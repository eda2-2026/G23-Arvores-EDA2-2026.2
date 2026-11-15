"""Árvore Rubro-Negra estilo CLRS (com registro dos eventos de correção)."""

class RBNode:
    __slots__ = ("key", "color", "left", "right", "parent")

    def __init__(self, key, color="B"):
        self.key = key
        self.color = color
        self.left = self.right = self.parent = None


class RBTree:
    kind = "RB"

    def __init__(self):
        self.NIL = RBNode(None, "B")
        self.NIL.left = self.NIL.right = self.NIL.parent = self.NIL
        self.root = self.NIL
        self.events = []

    def _left(self, x):
        y = x.right
        x.right = y.left
        if y.left is not self.NIL:
            y.left.parent = x
        y.parent = x.parent
        if x.parent is self.NIL:
            self.root = y
        elif x is x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y

    def _right(self, x):
        y = x.left
        x.left = y.right
        if y.right is not self.NIL:
            y.right.parent = x
        y.parent = x.parent
        if x.parent is self.NIL:
            self.root = y
        elif x is x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y
        y.right = x
        x.parent = y

    def insert(self, k):
        self.events = []
        NIL = self.NIL
        y, x = NIL, self.root
        while x is not NIL:
            y = x
            if k == x.key:
                return
            x = x.left if k < x.key else x.right
        z = RBNode(k, "R")
        z.left = z.right = NIL
        z.parent = y
        if y is NIL:
            self.root = z
        elif k < y.key:
            y.left = z
        else:
            y.right = z
        self._ins_fix(z)

    def _ins_fix(self, z):
        NIL = self.NIL
        if z.parent is NIL:
            self.events.append(("ROOT", z.key))
            z.color = "B"
            return
        if z.parent.color == "B":
            self.events.append(("NONE", z.key))
            return
        while z.parent.color == "R":
            p = z.parent
            g = p.parent
            if p is g.left:
                u = g.right
                if u.color == "R":
                    self.events.append(("RECOLOR", z.key))
                    p.color = u.color = "B"
                    g.color = "R"
                    z = g
                else:
                    if z is p.right:
                        self.events.append(("DOUBLE", z.key))
                        z = p
                        self._left(z)
                    else:
                        self.events.append(("SINGLE", z.key))
                    z.parent.color = "B"
                    z.parent.parent.color = "R"
                    self._right(z.parent.parent)
            else:
                u = g.left
                if u.color == "R":
                    self.events.append(("RECOLOR", z.key))
                    p.color = u.color = "B"
                    g.color = "R"
                    z = g
                else:
                    if z is p.left:
                        self.events.append(("DOUBLE", z.key))
                        z = p
                        self._right(z)
                    else:
                        self.events.append(("SINGLE", z.key))
                    z.parent.color = "B"
                    z.parent.parent.color = "R"
                    self._left(z.parent.parent)
        self.root.color = "B"

    def _transplant(self, u, v):
        if u.parent is self.NIL:
            self.root = v
        elif u is u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        v.parent = u.parent

    def _find(self, k):
        x = self.root
        while x is not self.NIL and x.key != k:
            x = x.left if k < x.key else x.right
        return x

    def delete(self, k):
        self.events = []
        NIL = self.NIL
        z = self._find(k)
        if z is NIL:
            return
        y = z
        y_color = y.color
        if z.left is NIL:
            x = z.right
            self._transplant(z, z.right)
        elif z.right is NIL:
            x = z.left
            self._transplant(z, z.left)
        else:
            y = z.right
            while y.left is not NIL:
                y = y.left
            y_color = y.color
            x = y.right
            if y.parent is z:
                x.parent = y
            else:
                self._transplant(y, y.right)
                y.right = z.right
                y.right.parent = y
            self._transplant(z, y)
            y.left = z.left
            y.left.parent = y
            y.color = z.color
        if y_color == "B":
            self._del_fix(x)
        else:
            self.events.append(("NONE", k))

    def _del_fix(self, x):
        NIL = self.NIL

        def pk(n):
            return n.parent.key if n.parent is not NIL else None

        if x.color == "R":
            self.events.append(("PAINT", x.key))
            x.color = "B"
            return
        if x is self.root:
            self.events.append(("NONE", None))
        while x is not self.root and x.color == "B":
            if x is x.parent.left:
                w = x.parent.right
                if w.color == "R":
                    self.events.append(("D1", pk(x)))
                    w.color = "B"
                    x.parent.color = "R"
                    self._left(x.parent)
                    w = x.parent.right
                if w.left.color == "B" and w.right.color == "B":
                    self.events.append(("D2", pk(x)))
                    w.color = "R"
                    x = x.parent
                else:
                    if w.right.color == "B":
                        self.events.append(("D3", pk(x)))
                        w.left.color = "B"
                        w.color = "R"
                        self._right(w)
                        w = x.parent.right
                    self.events.append(("D4", pk(x)))
                    w.color = x.parent.color
                    x.parent.color = "B"
                    w.right.color = "B"
                    self._left(x.parent)
                    x = self.root
            else:
                w = x.parent.left
                if w.color == "R":
                    self.events.append(("D1", pk(x)))
                    w.color = "B"
                    x.parent.color = "R"
                    self._right(x.parent)
                    w = x.parent.left
                if w.left.color == "B" and w.right.color == "B":
                    self.events.append(("D2", pk(x)))
                    w.color = "R"
                    x = x.parent
                else:
                    if w.left.color == "B":
                        self.events.append(("D3", pk(x)))
                        w.right.color = "B"
                        w.color = "R"
                        self._left(w)
                        w = x.parent.left
                    self.events.append(("D4", pk(x)))
                    w.color = x.parent.color
                    x.parent.color = "B"
                    w.left.color = "B"
                    self._right(x.parent)
                    x = self.root
        x.color = "B"

    def contains(self, k):
        return self._find(k) is not self.NIL

    def keys(self):
        return [s["key"] for s in self.snapshot()]

    def snapshot(self):
        out = []
        NIL = self.NIL

        def walk(n, d, p):
            if n is NIL:
                return
            walk(n.left, d + 1, n.key)
            out.append({"key": n.key, "depth": d, "parent": p, "color": n.color})
            walk(n.right, d + 1, n.key)

        walk(self.root, 0, None)
        return out

    def preorder(self):
        res = []
        NIL = self.NIL

        def w(n):
            if n is not NIL:
                res.append((n.key, n.color))
                w(n.left)
                w(n.right)

        w(self.root)
        return res

    def first_code(self):
        return self.events[0][0] if self.events else "NONE"
