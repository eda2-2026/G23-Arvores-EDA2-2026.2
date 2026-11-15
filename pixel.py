"""Kit de pixel art: paleta, fonte bitmap, sprites e botões estilo 8-bit."""
import random
import tkinter as tk
import unicodedata

P = dict(
    ink="#0f0f1c", bg="#1a1c2c", panel="#262b44", panel2="#333c57",
    mute="#566c86", soft="#94b0c2", white="#f4f4f4",
    red="#b13e53", orange="#ef7d57", yellow="#ffcd75", lime="#a7f070",
    green="#38b764", teal="#257179", navy="#29366f", blue="#3b5dc9",
    sky="#41a6f6", cyan="#73eff7", purple="#5d275d",
)
MONO = "Courier New"


def _mix(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(x + (y - x) * t) for x, y in zip(a, b))


def lighten(c, t=0.25):
    return _mix(c, "#ffffff", t)


def darken(c, t=0.35):
    return _mix(c, "#000000", t)


_RAW = {
    "A": ".XXX.|X...X|X...X|XXXXX|X...X|X...X|X...X",
    "B": "XXXX.|X...X|X...X|XXXX.|X...X|X...X|XXXX.",
    "C": ".XXX.|X...X|X....|X....|X....|X...X|.XXX.",
    "D": "XXXX.|X...X|X...X|X...X|X...X|X...X|XXXX.",
    "E": "XXXXX|X....|X....|XXXX.|X....|X....|XXXXX",
    "F": "XXXXX|X....|X....|XXXX.|X....|X....|X....",
    "G": ".XXX.|X...X|X....|X.XXX|X...X|X...X|.XXX.",
    "H": "X...X|X...X|X...X|XXXXX|X...X|X...X|X...X",
    "I": ".XXX.|..X..|..X..|..X..|..X..|..X..|.XXX.",
    "J": "..XXX|...X.|...X.|...X.|...X.|X..X.|.XX..",
    "K": "X...X|X..X.|X.X..|XX...|X.X..|X..X.|X...X",
    "L": "X....|X....|X....|X....|X....|X....|XXXXX",
    "M": "X...X|XX.XX|X.X.X|X.X.X|X...X|X...X|X...X",
    "N": "X...X|XX..X|X.X.X|X..XX|X...X|X...X|X...X",
    "O": ".XXX.|X...X|X...X|X...X|X...X|X...X|.XXX.",
    "P": "XXXX.|X...X|X...X|XXXX.|X....|X....|X....",
    "Q": ".XXX.|X...X|X...X|X...X|X.X.X|X..X.|.XX.X",
    "R": "XXXX.|X...X|X...X|XXXX.|X.X..|X..X.|X...X",
    "S": ".XXXX|X....|X....|.XXX.|....X|....X|XXXX.",
    "T": "XXXXX|..X..|..X..|..X..|..X..|..X..|..X..",
    "U": "X...X|X...X|X...X|X...X|X...X|X...X|.XXX.",
    "V": "X...X|X...X|X...X|X...X|X...X|.X.X.|..X..",
    "W": "X...X|X...X|X...X|X.X.X|X.X.X|XX.XX|X...X",
    "X": "X...X|X...X|.X.X.|..X..|.X.X.|X...X|X...X",
    "Y": "X...X|X...X|.X.X.|..X..|..X..|..X..|..X..",
    "Z": "XXXXX|....X|...X.|..X..|.X...|X....|XXXXX",
    "0": ".XXX.|X...X|X..XX|X.X.X|XX..X|X...X|.XXX.",
    "1": "..X..|.XX..|..X..|..X..|..X..|..X..|.XXX.",
    "2": ".XXX.|X...X|....X|...X.|..X..|.X...|XXXXX",
    "3": "XXXX.|....X|....X|.XXX.|....X|....X|XXXX.",
    "4": "...X.|..XX.|.X.X.|X..X.|XXXXX|...X.|...X.",
    "5": "XXXXX|X....|XXXX.|....X|....X|X...X|.XXX.",
    "6": ".XXX.|X....|X....|XXXX.|X...X|X...X|.XXX.",
    "7": "XXXXX|....X|...X.|..X..|.X...|.X...|.X...",
    "8": ".XXX.|X...X|X...X|.XXX.|X...X|X...X|.XXX.",
    "9": ".XXX.|X...X|X...X|.XXXX|....X|....X|.XXX.",
    " ": ".....|.....|.....|.....|.....|.....|.....",
    "-": ".....|.....|.....|XXXXX|.....|.....|.....",
    "+": ".....|..X..|..X..|XXXXX|..X..|..X..|.....",
    ".": ".....|.....|.....|.....|.....|.XX..|.XX..",
    ":": ".....|.XX..|.XX..|.....|.XX..|.XX..|.....",
    "!": "..X..|..X..|..X..|..X..|..X..|.....|..X..",
    "?": ".XXX.|X...X|....X|...X.|..X..|.....|..X..",
    "/": "....X|....X|...X.|..X..|.X...|X....|X....",
    ",": ".....|.....|.....|.....|.XX..|..X..|.X...",
    "(": "..X..|.X...|X....|X....|X....|.X...|..X..",
    ")": "..X..|...X.|....X|....X|....X|...X.|..X..",
    "'": ".XX..|..X..|.X...|.....|.....|.....|.....",
    "<": "...X.|..X..|.X...|X....|.X...|..X..|...X.",
    ">": ".X...|..X..|...X.|....X|...X.|..X..|.X...",
    "=": ".....|.....|XXXXX|.....|XXXXX|.....|.....",
    "*": ".....|X.X.X|.XXX.|XXXXX|.XXX.|X.X.X|.....",
}
FONT = {k: v.split("|") for k, v in _RAW.items()}


def _norm(t):
    t = unicodedata.normalize("NFD", str(t).upper())
    return "".join(ch for ch in t if unicodedata.category(ch) != "Mn")


def text_width(text, s):
    return max(0, (6 * len(_norm(text)) - 1) * s)


def pixel_text(cv, x, y, text, s=2, color="#ffffff", shadow=None, anchor="nw", tag=None):
    """Escreve texto com a fonte bitmap. Retorna a largura em pixels."""
    text = _norm(text)
    w, h = text_width(text, s), 7 * s
    if anchor == "center":
        x, y = x - w / 2, y - h / 2
    elif anchor == "n":
        x -= w / 2
    elif anchor == "ne":
        x -= w
    elif anchor == "e":
        x, y = x - w, y - h / 2
    elif anchor == "w":
        y -= h / 2
    x, y = int(x), int(y)

    def paint(ox, oy, col):
        cx = x + ox
        for ch in text:
            glyph = FONT.get(ch, FONT["?"])
            for r, row in enumerate(glyph):
                c = 0
                while c < 5:
                    if row[c] == "X":
                        c2 = c
                        while c2 < 5 and row[c2] == "X":
                            c2 += 1
                        cv.create_rectangle(cx + c * s, y + oy + r * s, cx + c2 * s, y + oy + (r + 1) * s,
                                            fill=col, width=0, tags=tag)
                        c = c2
                    else:
                        c += 1
            cx += 6 * s

    if shadow:
        off = max(1, s // 2 + (1 if s >= 4 else 0))
        paint(off, off, shadow)
    paint(0, 0, color)
    return w


HEART = [
    ".OO...OO.",
    "OHRO.ORRO",
    "OHRRORRRO",
    "ORRRRRRRO",
    ".ORRRRRO.",
    "..ORRRO..",
    "...ORO...",
    "....O....",
]
HEART_FULL = dict(O="#0f0f1c", R="#e0314b", H="#ff9bab")
HEART_EMPTY = dict(O="#566c86", R="#262b44", H="#333c57")
HEART_FLASH = dict(O="#f4f4f4", R="#ffffff", H="#ffffff")

STAR = [
    "...Y...",
    "...Y...",
    "YYYYYYY",
    ".YYYYY.",
    "..YYY..",
    ".YY.YY.",
    ".Y...Y.",
]
STAR_PAL = dict(Y="#ffcd75")

LOCK = [
    "..GGG..",
    ".G...G.",
    ".G...G.",
    "GGGGGGG",
    "GGGKGGG",
    "GGGKGGG",
    "GGGGGGG",
]
LOCK_PAL = dict(G="#94b0c2", K="#262b44")

TREE = [
    "....GGGG....",
    "...GGLGGG...",
    "..GGGGGLGG..",
    ".GGLGGGGGGG.",
    "GGGGGGGGLGGG",
    ".GGGGGGGGGG.",
    "GGGLGGGGGGGG",
    ".GGGGGGGLGG.",
    "..GGGGGGGG..",
    ".....TT.....",
    ".....TT.....",
    "....TTTT....",
]
TREE_GREEN = dict(G="#38b764", L="#a7f070", T="#8a4b2a")
TREE_RED = dict(G="#b13e53", L="#ef7d57", T="#8a4b2a")

COIN = [
    "..YYY..",
    ".YWYYY.",
    "YWYYYOY",
    "YWYYYOY",
    "YYYYYOY",
    ".YOOOY.",
    "..YYY..",
]
COIN_PAL = dict(Y="#ffcd75", W="#fff2c9", O="#ef7d57")

SKULL = [
    ".XXXXX.",
    "XXXXXXX",
    "X.XXX.X",
    "X.XXX.X",
    "XXX.XXX",
    ".XXXXX.",
    ".X.X.X.",
]
SKULL_PAL = dict(X="#f4f4f4")


def sprite_size(grid, s):
    return len(grid[0]) * s, len(grid) * s


def draw_sprite(cv, grid, pal, x, y, s=3, tag=None):
    for r, row in enumerate(grid):
        c = 0
        while c < len(row):
            ch = row[c]
            if ch in pal:
                c2 = c
                while c2 < len(row) and row[c2] == ch:
                    c2 += 1
                cv.create_rectangle(x + c * s, y + r * s, x + c2 * s, y + (r + 1) * s,
                                    fill=pal[ch], width=0, tags=tag)
                c = c2
            else:
                c += 1


def pixel_frame(cv, x1, y1, x2, y2, border=None, fill=None, u=4):
    """Moldura de cantos recortados (estilo janela de RPG)."""
    border = border or P["mute"]
    cv.create_rectangle(x1 + u, y1, x2 - u, y2, fill=P["ink"], width=0)
    cv.create_rectangle(x1, y1 + u, x2, y2 - u, fill=P["ink"], width=0)
    cv.create_rectangle(x1 + u, y1 + u, x2 - u, y2 - u, fill=border, width=0)
    cv.create_rectangle(x1 + 2 * u, y1 + 2 * u, x2 - 2 * u, y2 - 2 * u, fill=fill or P["panel"], width=0)


def starfield(cv, w, h, seed=7, count=70):
    rnd = random.Random(seed)
    for _ in range(count):
        x, y = rnd.randrange(0, w, 4), rnd.randrange(0, h, 4)
        col = rnd.choice([P["navy"], P["navy"], P["panel2"], P["mute"], P["soft"]])
        sz = 4 if col in (P["navy"], P["panel2"]) else 2
        cv.create_rectangle(x, y, x + sz, y + sz, fill=col, width=0)
    for _ in range(6):
        x, y = rnd.randrange(8, w - 8, 4), rnd.randrange(8, h - 8, 4)
        col = rnd.choice([P["cyan"], P["yellow"], P["white"]])
        for dx, dy in ((0, 0), (-4, 0), (4, 0), (0, -4), (0, 4)):
            cv.create_rectangle(x + dx, y + dy, x + dx + 4, y + dy + 4, fill=col, width=0)


def draw_hearts(cv, lives, total=3, x=0, y=0, s=3, gap=6, flash=None):
    """Desenha corações cheios e vazios. flash = índice do coração piscando."""
    w, _ = sprite_size(HEART, s)
    for i in range(total):
        if flash is not None and i == flash:
            pal = HEART_FLASH
        else:
            pal = HEART_FULL if i < lives else HEART_EMPTY
        draw_sprite(cv, HEART, pal, x + i * (w + gap), y, s)
    return total * w + (total - 1) * gap


class PixelButton(tk.Canvas):
    def __init__(self, parent, text="", command=None, w=240, h=48, color=None, fg=None,
                 font_size=11, big=0, icon=None, state="normal", bg=None, extra=None):
        super().__init__(parent, width=w, height=h, bg=bg or P["bg"], highlightthickness=0, bd=0)
        self.w, self.h = w, h
        self.text = text
        self.command = command
        self.color = color or P["blue"]
        self.fg = fg or P["white"]
        self.font_size = font_size
        self.big = big
        self.icon = icon
        self.extra = extra
        self._state = state
        self._hover = False
        self._pressed = False
        self.bind("<Enter>", lambda e: self._set(hover=True))
        self.bind("<Leave>", lambda e: self._set(hover=False, pressed=False))
        self.bind("<ButtonPress-1>", lambda e: self._set(pressed=True))
        self.bind("<ButtonRelease-1>", self._release)
        self._draw()

    def _set(self, hover=None, pressed=None):
        if hover is not None:
            self._hover = hover
        if pressed is not None:
            self._pressed = pressed
        try:
            self._draw()
        except tk.TclError:
            pass

    def _release(self, e):
        was = self._pressed
        self._set(pressed=False)
        if was and self._state == "normal" and 0 <= e.x <= self.w and 0 <= e.y <= self.h and self.command:
            self.command()

    def configure(self, cnf=None, **kw):
        redraw = False
        for k in ("state", "text", "command", "color"):
            if k in kw:
                v = kw.pop(k)
                if k == "state":
                    self._state = v
                elif k == "text":
                    self.text = v
                elif k == "command":
                    self.command = v
                else:
                    self.color = v
                redraw = True
        if kw or cnf:
            super().configure(cnf, **kw)
        if redraw:
            self._draw()
        elif not kw and not cnf:
            return super().configure()

    config = configure

    def _draw(self):
        self.delete("all")
        w, h = self.w, self.h
        disabled = self._state == "disabled"
        inert = self._state in ("disabled", "locked")
        base = P["panel2"] if disabled else self.color
        if self._hover and not inert:
            base = lighten(base, 0.14)
        light, dark = lighten(base, 0.35), darken(base, 0.4)
        pressed = self._pressed and not inert
        H = h - 4
        y0 = 4 if pressed else 0
        ink = P["ink"]

        def r(x1, y1, x2, y2, c):
            self.create_rectangle(x1, y1, x2, y2, fill=c, width=0)

        if not pressed:
            r(4, 4, w - 4, h, ink)
            r(0, 8, w, h - 4, ink)
        r(4, y0, w - 4, y0 + H, ink)
        r(0, y0 + 4, w, y0 + H - 4, ink)
        r(4, y0 + 4, w - 4, y0 + H - 4, base)
        r(8, y0 + 4, w - 8, y0 + 8, light)
        r(4, y0 + 8, 8, y0 + H - 8, light)
        r(8, y0 + H - 8, w - 8, y0 + H - 4, dark)
        r(w - 8, y0 + 8, w - 4, y0 + H - 8, dark)
        fg = P["mute"] if disabled else self.fg
        cy = y0 + H / 2
        if self.icon:
            grid, pal, s = self.icon
            iw, ih = sprite_size(grid, s)
            draw_sprite(self, grid, pal, 16, cy - ih / 2, s)
            tx, anchor = 16 + iw + 12, "w"
        else:
            tx, anchor = w / 2, "center"
        if self.big:
            pixel_text(self, tx, cy, self.text, s=self.big, color=fg,
                       shadow=None if disabled else darken(base, 0.5), anchor=anchor)
        else:
            self.create_text(tx, cy, text=self.text, fill=fg, anchor="w" if anchor == "w" else "center",
                             font=(MONO, self.font_size, "bold"))
        if self.extra:
            pixel_text(self, w - 18, cy, self.extra, s=2, color=P["yellow"] if not disabled else P["mute"],
                       shadow=None if disabled else darken(base, 0.5), anchor="e")
        super().configure(cursor="arrow" if inert else "hand2")
