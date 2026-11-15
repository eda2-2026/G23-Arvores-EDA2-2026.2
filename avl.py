"""Árvore AVL (com registro dos eventos de rotação)."""

class AVLNode:
    __slots__ = ("key", "left", "right", "h")

    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None
        self.h = 1


def _h(n):
    return n.h if n else 0


def _upd(n):
    n.h = 1 + max(_h(n.left), _h(n.right))


def _bf(n):
    return _h(n.left) - _h(n.right)


def _rot_r(y):
    x = y.left
    y.left = x.right
    x.right = y
    _upd(y)
    _upd(x)
    return x


def _rot_l(x):
    y = x.right
    x.right = y.left
    y.left = x
    _upd(x)
    _upd(y)
    return y


class AVLTree:
    kind = "AVL"

    def __init__(self):
        self.root = None
        self.events = []

    def insert(self, k, rebalance=True):
        self.events = []
        self.root = self._ins(self.root, k, rebalance)

    def _ins(self, n, k, rb):
        if n is None:
            return AVLNode(k)
        if k < n.key:
            n.left = self._ins(n.left, k, rb)
        elif k > n.key:
            n.right = self._ins(n.right, k, rb)
        else:
            return n
        if rb:
            return self._fix(n)
        _upd(n)
        return n

    def delete(self, k):
        self.events = []
        self.root = self._del(self.root, k)

    def _del(self, n, k):
        if n is None:
            return None
        if k < n.key:
            n.left = self._del(n.left, k)
        elif k > n.key:
            n.right = self._del(n.right, k)
        else:
            if n.left is None:
                return n.right
            if n.right is None:
                return n.left
            s = n.right
            while s.left:
                s = s.left
            n.key = s.key
            n.right = self._del(n.right, s.key)
        return self._fix(n)

    def _fix(self, n):
        _upd(n)
        b = _bf(n)
        if b > 1:
            if _bf(n.left) < 0:
                n.left = _rot_l(n.left)
                self.events.append(("LR", n.key))
            else:
                self.events.append(("LL", n.key))
            return _rot_r(n)
        if b < -1:
            if _bf(n.right) > 0:
                n.right = _rot_r(n.right)
                self.events.append(("RL", n.key))
            else:
                self.events.append(("RR", n.key))
            return _rot_l(n)
        return n

    def contains(self, k):
        n = self.root
        while n:
            if k == n.key:
                return True
            n = n.left if k < n.key else n.right
        return False

    def keys(self):
        return [s["key"] for s in self.snapshot()]

    def snapshot(self):
        out = []

        def walk(n, d, p):
            if not n:
                return
            walk(n.left, d + 1, n.key)
            out.append({"key": n.key, "depth": d, "parent": p, "bf": _bf(n)})
            walk(n.right, d + 1, n.key)

        walk(self.root, 0, None)
        return out

    def preorder(self):
        res = []

        def w(n):
            if n:
                res.append(n.key)
                w(n.left)
                w(n.right)

        w(self.root)
        return res

    def first_code(self):
        return self.events[0][0] if self.events else "NONE"
