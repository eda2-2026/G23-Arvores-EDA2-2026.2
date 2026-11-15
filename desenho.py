"""Desenho das árvores no canvas, em pixel art."""
import math

from pixel import P, pixel_frame, pixel_text

ESTILOS = {
    "AVL": dict(fill=P["sky"], shine=P["cyan"], edge=P["navy"], text=P["ink"]),
    "R": dict(fill="#d6405a", shine="#ff9bab", edge="#5d1a2a", text=P["white"]),
    "B": dict(fill=P["ink"], shine=P["mute"], edge=P["soft"], text=P["white"]),
}
COR_NOVO = P["lime"]
COR_REMOVIDO = P["orange"]


def _disc(cv, cx, cy, R, u, color):
    """Círculo feito de blocos (fiel à grade de pixels)."""
    for dy in range(-R, R + 1):
        dx = int(math.sqrt((R + 0.5) ** 2 - dy * dy))
        cv.create_rectangle(round(cx - (dx + 0.5) * u), round(cy + (dy - 0.5) * u),
                            round(cx + (dx + 0.5) * u), round(cy + (dy + 0.5) * u),
                            fill=color, width=0)


def _pixel_line(cv, x1, y1, x2, y2, u, color):
    steps = max(1, int(max(abs(x2 - x1), abs(y2 - y1)) / u))
    for i in range(steps + 1):
        x = x1 + (x2 - x1) * i / steps
        y = y1 + (y2 - y1) * i / steps
        gx, gy = round(x / u) * u, round(y / u) * u
        cv.create_rectangle(gx, gy, gx + u, gy + u, fill=color, width=0)


def draw_board(cv, W, H):
    """Fundo da área de jogo: moldura de pixel e piso quadriculado."""
    cv.delete("all")
    pixel_frame(cv, 0, 0, W, H, border=P["mute"], fill=P["panel"])
    check = "#2b3150"
    for gx in range(8, W - 8, 32):
        for gy in range(8, H - 8, 32):
            if ((gx // 32) + (gy // 32)) % 2 == 0:
                cv.create_rectangle(gx, gy, min(gx + 32, W - 8), min(gy + 32, H - 8), fill=check, width=0)


def draw_tree(cv, snap, kind, hl_new=None, hl_del=None, W=None, H=None):
    """Desenha a árvore e devolve a lista de áreas clicáveis [(chave, x, y, r)]."""
    W = W or int(cv["width"])
    H = H or int(cv["height"])
    draw_board(cv, W, H)
    n = len(snap)
    if n == 0:
        pixel_text(cv, W / 2, H / 2, "ARVORE VAZIA", s=3, color=P["mute"], anchor="center")
        return []
    maxd = max(s["depth"] for s in snap)
    margin = 40
    step = min(64, (W - 2 * margin) / (n - 1)) if n > 1 else 0
    x0 = (W - step * (n - 1)) / 2
    vstep = min(75, (H - 90) / maxd) if maxd else 0
    y0 = 52
    r_px = max(9, min(21, step / 2.1 if step else 21))
    if vstep:
        r_px = min(r_px, vstep / 2.3)
    u = 3 if r_px >= 15 else 2
    R = max(3, int(r_px / u) - 1)
    rt = (R + 1) * u
    pos = {}
    for i, s in enumerate(snap):
        pos[s["key"]] = (x0 + i * step, y0 + s["depth"] * vstep)
    for s in snap:
        if s["parent"] is not None:
            (xa, ya), (xb, yb) = pos[s["parent"]], pos[s["key"]]
            _pixel_line(cv, xa, ya, xb, yb, u, P["mute"])
    hits = []
    for s in snap:
        x, y = pos[s["key"]]
        st = ESTILOS["AVL"] if kind == "AVL" else ESTILOS[s["color"]]
        if s["key"] == hl_new:
            _disc(cv, x, y, R + 2, u, COR_NOVO)
        elif s["key"] == hl_del:
            _disc(cv, x, y, R + 2, u, COR_REMOVIDO)
        _disc(cv, x, y, R + 1, u, st["edge"])
        _disc(cv, x, y, R, u, st["fill"])
        if R >= 4:
            sx, sy = x - int(R * 0.55) * u, y - int(R * 0.6) * u
            cv.create_rectangle(sx, sy, sx + 2 * u, sy + u, fill=st["shine"], width=0)
            cv.create_rectangle(sx - u, sy + u, sx, sy + 2 * u, fill=st["shine"], width=0)
        label = str(s["key"])
        diam = (2 * R + 1) * u
        ts = max(1, min(3, int(diam * 0.85 / (6 * len(label) - 1))))
        pixel_text(cv, x, y, label, s=ts, color=st["text"], anchor="center")
        if kind == "AVL":
            bf = s["bf"]
            txt = f"{bf:+d}" if bf else "0"
            col = P["orange"] if abs(bf) > 1 else P["soft"]
            pixel_text(cv, x + rt + 3, y - 4, txt, s=2 if R >= 4 else 1, color=col,
                       shadow=P["ink"], anchor="w")
        hits.append((s["key"], x, y, rt))
    return hits
