"""Interface gráfica (tkinter) em pixel art: menu, fases e laboratório livre."""
import json
import os
import random
import tkinter as tk

from avl import AVLTree
from desenho import draw_tree
from niveis import LEVELS
from perguntas import make_question, parse_preorder
from pixel import (COIN, COIN_PAL, LOCK, LOCK_PAL, MONO, P, SKULL, SKULL_PAL, STAR, STAR_PAL, TREE,
                   TREE_GREEN, TREE_RED, PixelButton, draw_hearts, draw_sprite, pixel_frame,
                   pixel_text, sprite_size, starfield, text_width)
from rbtree import RBTree
from textos import THEORY, explain_code, opts_for

SAVE = os.path.join(os.path.expanduser("~"), ".ordenaasarvores.json")
W = 940
RN_COLOR = "#ff8fa3"


class App:
    def __init__(self, root):
        self.root = root
        root.title("Ordena as Árvores - AVL e Rubro-Negra")
        root.geometry("980x800")
        root.minsize(980, 760)
        root.configure(bg=P["bg"])
        self.prog = {"unlocked": 1, "best": {}}
        self._job = None
        self.cheat = False
        self.bank = None
        try:
            with open(SAVE, encoding="utf-8") as f:
                self.prog.update(json.load(f))
        except Exception:
            pass
        self.menu()

    def get_bank(self):
        if self.bank is None:
            state = random.getstate()
            self.bank = []
            for i, lv in enumerate(LEVELS):
                random.seed(7000 + i)
                self.bank.append([make_question(lv) for _ in range(lv["rounds"])])
            random.setstate(state)
        return self.bank

    def clear(self):
        if self._job:
            try:
                self.root.after_cancel(self._job)
            except Exception:
                pass
            self._job = None
        for w in self.root.winfo_children():
            w.destroy()

    def save(self):
        try:
            with open(SAVE, "w", encoding="utf-8") as f:
                json.dump(self.prog, f)
        except Exception:
            pass

    def panel(self, parent, bg=None, border=None):
        bg = bg or P["panel"]
        border = border or P["mute"]
        return tk.Frame(parent, bg=bg, highlightbackground=border, highlightcolor=border, highlightthickness=4)

    def canvas(self, parent, w, h, bg=None):
        return tk.Canvas(parent, width=w, height=h, bg=bg or P["bg"], highlightthickness=0, bd=0)

    def pbtn(self, parent, text, cmd, color, w=200, h=46, **kw):
        kw.setdefault("bg", P["bg"])
        return PixelButton(parent, text=text, command=cmd, w=w, h=h, color=color, **kw)

    def popup(self, titulo, texto, cor=None):
        top = tk.Toplevel(self.root)
        top.title(titulo)
        top.configure(bg=P["bg"])
        top.resizable(False, False)
        top.transient(self.root)
        box = self.panel(top)
        box.pack(padx=16, pady=16)
        cv = self.canvas(box, 640, 56, P["panel"])
        cv.pack(pady=(8, 0))
        pixel_text(cv, 320, 28, titulo, s=4, color=cor or P["yellow"], shadow=P["ink"], anchor="center")
        tk.Label(box, text=texto, bg=P["panel"], fg=P["white"], font=(MONO, 10, "bold"), justify="left",
                 wraplength=620, padx=18, pady=8).pack()
        row = tk.Frame(box, bg=P["panel"])
        row.pack(pady=(4, 12))
        self.pbtn(row, "OK", top.destroy, P["green"], w=140, h=44, big=2, bg=P["panel"]).pack()
        top.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width() - top.winfo_width()) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - top.winfo_height()) // 3
        top.geometry(f"+{max(0, x)}+{max(0, y)}")
        try:
            top.grab_set()
        except tk.TclError:
            pass

    @staticmethod
    def lv_style(lv):
        if lv["tree"] == "AVL":
            return P["blue"], P["white"]
        if lv["tree"] == "RB":
            return P["red"], P["white"]
        return P["purple"], P["yellow"]

    def menu(self):
        self.clear()
        hdr = self.canvas(self.root, W, 176)
        hdr.pack(pady=(8, 0))
        starfield(hdr, W, 176, seed=3, count=70)
        draw_sprite(hdr, TREE, TREE_GREEN, 56, 40, 8)
        draw_sprite(hdr, TREE, TREE_RED, W - 56 - 96, 40, 8)
        pixel_text(hdr, W / 2, 12, "ORDENA AS", s=7, color=P["yellow"], shadow=P["red"], anchor="n")
        pixel_text(hdr, W / 2, 78, "ARVORES", s=7, color=P["lime"], shadow=P["teal"], anchor="n")
        parts = [("AVL", P["cyan"]), (" X ", P["white"]), ("RUBRO-NEGRA", RN_COLOR)]
        s = 3
        total = sum(text_width(t, s) for t, _ in parts) + s * (len(parts) - 1)
        x = (W - total) / 2
        for t, c in parts:
            x += pixel_text(hdr, x, 142, t, s=s, color=c, shadow=P["ink"]) + s

        best = self.prog["best"]
        bar = self.canvas(self.root, W, 48)
        bar.pack(pady=(4, 6))
        pixel_frame(bar, 110, 0, W - 110, 48, border=P["mute"], fill=P["panel"])
        draw_sprite(bar, COIN, COIN_PAL, 142, 13, 3)
        pixel_text(bar, 176, 13, f"{sum(best.values())}", s=3, color=P["yellow"], shadow=P["ink"])
        txt = f"FASES {len(best)}/{len(LEVELS)}"
        w = text_width(txt, 3)
        pixel_text(bar, W - 142, 13, txt, s=3, color=P["white"], shadow=P["ink"], anchor="ne")
        draw_sprite(bar, STAR, STAR_PAL, W - 142 - w - 32, 13, 3)

        grid = tk.Frame(self.root, bg=P["bg"])
        grid.pack(pady=2)
        for i, lv in enumerate(LEVELS):
            unlocked = i < self.prog["unlocked"] or self.cheat
            score = best.get(str(i))
            color, fg = self.lv_style(lv)
            if not unlocked:
                icon, text, extra = (LOCK, LOCK_PAL, 3), f"FASE {i + 1} - BLOQUEADA", None
            else:
                if score is not None:
                    icon = (STAR, STAR_PAL, 3)
                elif lv["tree"] == "MIX":
                    icon = (SKULL, SKULL_PAL, 3)
                else:
                    icon = (TREE, TREE_GREEN if lv["tree"] == "AVL" else TREE_RED, 2)
                text, extra = lv["name"], (str(score) if score is not None else None)
            b = self.pbtn(grid, text, lambda i=i: self.level_intro(i), color, w=452, h=52, fg=fg,
                          font_size=10, icon=icon, extra=extra, state="normal" if unlocked else "disabled")
            b.grid(row=i % 6, column=i // 6, padx=8, pady=3)

        row = tk.Frame(self.root, bg=P["bg"])
        row.pack(pady=(10, 0))
        self.pbtn(row, "LABORATORIO", self.lab, P["green"], w=230, h=48, big=2, fg=P["ink"]).pack(side="left", padx=6)
        self.pbtn(row, "RESPOSTAS", self.answers_list, P["orange"], w=230, h=48, big=2,
                  fg=P["ink"]).pack(side="left", padx=6)
        self.pbtn(row, "COMO JOGAR", self.how, P["blue"], w=210, h=48, big=2).pack(side="left", padx=6)
        row2 = tk.Frame(self.root, bg=P["bg"])
        row2.pack(pady=(6, 0))
        self.pbtn(row2, "GABARITO: SIM" if self.cheat else "GABARITO: NAO", self.toggle_cheat,
                  P["yellow"] if self.cheat else P["panel2"], w=270, h=48, big=2,
                  fg=P["ink"] if self.cheat else P["white"]).pack(side="left", padx=6)
        self.pbtn(row2, "SAIR", self.root.destroy, P["red"], w=120, h=48, big=2).pack(side="left", padx=6)

    def toggle_cheat(self):
        self.cheat = not self.cheat
        self.menu()

    def how(self):
        self.popup(
            "COMO JOGAR",
            "Em cada fase você recebe uma árvore e uma operação (inserir ou remover um valor).\n\n"
            "Tipos de pergunta:\n"
            " - Escolha: qual correção ou rotação acontece primeiro\n"
            " - Clique: clique no nó desbalanceado (árvore mostrada sem correção)\n"
            " - Pré-ordem: digite a pré-ordem da árvore final (RN: 'v' depois dos nós vermelhos)\n\n"
            "Você começa com 3 corações. Errar custa um coração.\n"
            "A dica vale metade dos pontos da rodada.\n\n"
            "RESPOSTAS: no menu, veja a lista de todas as perguntas do jogo com as respostas.\n"
            "GABARITO: ligue no menu para ver a resposta exata de cada pergunta (libera todas as fases, "
            "mas não salva pontos nem progresso).\n\n"
            "Na AVL, o número ao lado do nó é o fator de balanceamento.\n"
            "Contorno verde = valor inserido. Contorno laranja = valor removido.")

    def level_intro(self, i):
        self.clear()
        lv = LEVELS[i]
        color, _ = self.lv_style(lv)
        hdr = self.canvas(self.root, W, 132)
        hdr.pack(pady=(10, 0))
        starfield(hdr, W, 132, seed=i + 11, count=55)
        pixel_text(hdr, W / 2, 14, f"FASE {i + 1}", s=7, color=P["yellow"], shadow=P["red"], anchor="n")
        pixel_text(hdr, W / 2, 84, lv["name"], s=3, color=P["lime"], shadow=P["ink"], anchor="n")
        draw_sprite(hdr, TREE, TREE_GREEN, 70, 24, 6)
        draw_sprite(hdr, TREE, TREE_RED, W - 70 - 72, 24, 6)

        tk.Label(self.root, text=lv["desc"], bg=P["bg"], fg=P["soft"], font=(MONO, 12, "bold"),
                 wraplength=840, justify="center").pack(pady=(8, 8))
        kinds = ["AVL", "RB"] if lv["tree"] == "MIX" else [lv["tree"]]
        ops = ["insert", "delete"] if lv["op"] == "MIX" else [lv["op"]]
        text = "\n\n".join(THEORY[(k, o)] for k in kinds for o in ops)
        box = self.panel(self.root, border=color)
        box.pack(padx=40)
        tk.Label(box, text=text, bg=P["panel"], fg=P["white"], justify="left", anchor="w",
                 font=(MONO, 10, "bold"), padx=18, pady=12, wraplength=840).pack()

        info = self.canvas(self.root, W, 52)
        info.pack(pady=(10, 2))
        hw = draw_hearts(info, 3, x=0, y=-100, s=4)
        info.delete("all")
        label = f"{lv['rounds']} RODADAS"
        tw = text_width(label, 3)
        x0 = (W - (hw + 24 + tw)) / 2
        draw_hearts(info, 3, x=x0, y=8, s=4, gap=6)
        pixel_text(info, x0 + hw + 24, 26, label, s=3, color=P["yellow"], shadow=P["ink"], anchor="w")

        row = tk.Frame(self.root, bg=P["bg"])
        row.pack(pady=6)
        self.pbtn(row, "COMECAR", lambda: self.start_level(i), P["green"], w=240, h=52, big=3,
                  fg=P["ink"]).pack(side="left", padx=8)
        self.pbtn(row, "VOLTAR", self.menu, P["panel2"], w=200, h=52, big=3).pack(side="left", padx=8)

    def start_level(self, i):
        self.li = i
        self.lv = LEVELS[i]
        self.lives = 3
        self.score = 0
        self.streak = 0
        self.round = 0
        self.done = 0
        self.hint_used = False
        self.awaiting = False
        self.hits = []
        self.opt_btns = {}
        self.ans_widgets = []
        self.clear()

        bar = tk.Frame(self.root, bg=P["bg"])
        bar.pack(side="bottom", pady=(2, 8))
        self.hint_btn = self.pbtn(bar, "DICA", self.hint, P["yellow"], w=150, h=46, big=2, fg=P["ink"])
        self.hint_btn.pack(side="left", padx=8)
        self.next_btn = self.pbtn(bar, "PROXIMA", self.next_question, P["green"], w=220, h=46, big=2,
                                  fg=P["ink"], state="disabled")
        self.next_btn.pack(side="left", padx=8)
        self.pbtn(bar, "MENU", self.menu, P["panel2"], w=150, h=46, big=2).pack(side="left", padx=8)

        self.hud = self.canvas(self.root, W, 76)
        self.hud.pack(pady=(8, 2))
        self.cv = self.canvas(self.root, W, 336)
        self.cv.pack(pady=2)
        self.cv.bind("<Button-1>", self.on_click)

        self.qbox = self.panel(self.root)
        self.qbox.pack(fill="x", padx=20, pady=(4, 2))
        self.badge = self.canvas(self.qbox, 150, 34, P["panel"])
        self.badge.pack(side="left", padx=(10, 4), pady=6)
        self.qlabel = tk.Label(self.qbox, text="", bg=P["panel"], fg=P["white"], font=(MONO, 11, "bold"),
                               wraplength=740, justify="left", anchor="w")
        self.qlabel.pack(side="left", fill="x", expand=True, padx=6, pady=6)

        self.ans = tk.Frame(self.root, bg=P["bg"])
        self.ans.pack(pady=2)
        self.banner = self.canvas(self.root, W, 34)
        self.banner.pack()
        self.fb = tk.Label(self.root, text="", bg=P["bg"], fg=P["soft"], font=(MONO, 10, "bold"),
                           wraplength=900, justify="center", height=3)
        self.fb.pack()
        self.next_question()

    def draw_hud(self, flash=None):
        cv = self.hud
        cv.delete("all")
        pixel_frame(cv, 0, 0, W, 76, border=P["mute"], fill=P["panel"])
        pixel_text(cv, 26, 14, f"FASE {self.li + 1}", s=3, color=P["yellow"], shadow=P["ink"])
        total = self.lv["rounds"]
        for k in range(total):
            if k < self.done:
                col = P["green"]
            elif k == self.done and self.awaiting:
                col = P["yellow"]
            else:
                col = P["panel2"]
            x = 26 + k * 20
            cv.create_rectangle(x, 46, x + 16, 58, fill=P["ink"], width=0)
            cv.create_rectangle(x + 2, 48, x + 14, 56, fill=col, width=0)
        hw = 3 * 36 + 2 * 10
        draw_hearts(cv, self.lives, x=(W - hw) / 2, y=12, s=4, gap=10, flash=flash)
        if self.streak > 1:
            pixel_text(cv, W / 2, 52, f"COMBO X{self.streak}", s=2, color=P["orange"], shadow=P["ink"], anchor="n")
        sc = f"{self.score}"
        tw = text_width(sc, 4)
        pixel_text(cv, W - 26, 14, sc, s=4, color=P["yellow"], shadow=P["ink"], anchor="ne")
        draw_sprite(cv, COIN, COIN_PAL, W - 26 - tw - 36, 16, 3)
        pixel_text(cv, W - 26, 50, "PONTOS", s=2, color=P["soft"], shadow=P["ink"], anchor="ne")

    def next_question(self):
        if self.round >= self.lv["rounds"]:
            return self.finish_level()
        self.round += 1
        self.q = self.get_bank()[self.li][self.round - 1]
        q = self.q
        self.hint_used = False
        self.awaiting = True
        self.fb.config(text="")
        self.banner.delete("all")
        self.next_btn.config(state="disabled", text="PROXIMA")
        self.hint_btn.config(state="normal")
        self.draw_hud()
        verb = "INSERIR" if q["op"] == "insert" else "REMOVER"
        self.badge.delete("all")
        if q["kind"] == "AVL":
            self.badge.create_rectangle(0, 0, 150, 34, fill=P["blue"], width=0)
            pixel_text(self.badge, 75, 17, "AVL", s=3, color=P["white"], shadow=P["ink"], anchor="center")
        else:
            self.badge.create_rectangle(0, 0, 150, 34, fill=P["red"], width=0)
            pixel_text(self.badge, 75, 17, "RUBRO-NEGRA", s=2, color=P["white"], shadow=P["ink"], anchor="center")
        if self.cheat:
            pixel_text(self.banner, W / 2, 17, "GABARITO: " + self.cheat_text(q), s=2, color=P["yellow"],
                       shadow=P["ink"], anchor="center")
        self.hl_new = q["key"] if (q["op"] == "insert" and q["qt"] == "click") else None
        self.hl_del = q["key"] if q["op"] == "delete" else None
        self.hits = draw_tree(self.cv, q["before"], q["kind"], self.hl_new, self.hl_del)
        for w in self.ans.winfo_children():
            w.destroy()
        self.opt_btns = {}
        self.ans_widgets = []
        if q["qt"] == "case":
            self.qlabel.config(text=f"Vai {verb} o valor {q['key']}. O que acontece primeiro?")
            opts = opts_for(q["kind"], q["op"])
            codes = [c for c in (self.lv["allowed"] or list(opts)) if c in opts]
            random.shuffle(codes)
            for j, c in enumerate(codes):
                b = self.pbtn(self.ans, opts[c], lambda c=c: self.submit(c), P["blue"], w=452, h=44,
                              font_size=9)
                b.grid(row=j // 2, column=j % 2, padx=6, pady=2)
                self.opt_btns[c] = b
        elif q["qt"] == "click":
            self.qlabel.config(text=f"O valor {q['key']} entrou (contorno verde) SEM correção. "
                                    f"Clique no nó desbalanceado mais fundo.")
            pixel_text_lbl = self.canvas(self.ans, 420, 30)
            pixel_text_lbl.pack(pady=6)
            pixel_text(pixel_text_lbl, 210, 15, "CLIQUE EM UM NO!", s=3, color=P["cyan"], shadow=P["ink"],
                       anchor="center")
        else:
            colored = q["kind"] == "RB"
            extra = "  Escreva 'v' depois dos nós vermelhos (ex: 10 5v 20v)." if colored else ""
            self.qlabel.config(text=f"Vai {verb} o valor {q['key']}. Qual a pré-ordem da árvore final?{extra}")
            self.entry = tk.Entry(self.ans, width=40, font=(MONO, 15, "bold"), bg=P["ink"], fg=P["lime"],
                                  insertbackground=P["lime"], relief="flat", highlightthickness=4,
                                  highlightbackground=P["mute"], highlightcolor=P["sky"])
            self.entry.pack(side="left", padx=8, ipady=6)
            self.entry.bind("<Return>", lambda e: self.submit(self.entry.get()))
            self.entry.focus_set()
            self.go_btn = self.pbtn(self.ans, "RESPONDER", lambda: self.submit(self.entry.get()), P["sky"],
                                    w=210, h=46, big=2, fg=P["ink"])
            self.go_btn.pack(side="left", padx=8)
            self.ans_widgets = [self.entry, self.go_btn]

    def on_click(self, ev):
        if not self.awaiting or self.q["qt"] != "click":
            return
        for key, x, y, r in self.hits:
            if (ev.x - x) ** 2 + (ev.y - y) ** 2 <= (r + 3) ** 2:
                self.submit(key)
                return

    def hint(self):
        if not self.awaiting:
            return
        self.hint_used = True
        q = self.q
        self.popup("DICA", THEORY[(q["kind"], q["op"])] + "\n\n(Usar a dica vale metade dos pontos.)")

    def submit(self, value):
        if not self.awaiting:
            return
        q = self.q
        if q["qt"] == "case":
            ok = value == q["code"]
        elif q["qt"] == "click":
            ok = value == q["node"]
        else:
            colored = q["kind"] == "RB"
            parsed = parse_preorder(value, colored)
            if parsed is None or not parsed:
                self.fb.config(text="Formato inválido. Digite números separados por espaço.", fg=P["orange"])
                return
            ok = parsed == q["pre"]
        self.awaiting = False
        self.done += 1
        for code, b in self.opt_btns.items():
            if code == q["code"]:
                b.configure(state="locked", color=P["green"])
            elif code == value and not ok:
                b.configure(state="locked", color=P["red"])
            else:
                b.configure(state="disabled")
        for w in self.ans_widgets:
            try:
                w.config(state="disabled")
            except tk.TclError:
                pass
        self.hint_btn.config(state="disabled")
        if ok:
            self.streak += 1
            gain = (100 + min(self.streak - 1, 5) * 20) // (2 if self.hint_used else 1)
            self.score += gain
            self.show_banner(True, f"CORRETO! +{gain}")
        else:
            self.streak = 0
            self.lives -= 1
            self.show_banner(False, "ERROU! -1 CORACAO")
        self.fb.config(text=self.feedback_text(q), fg=P["soft"])
        draw_tree(self.cv, q["after"], q["kind"], q["key"] if q["op"] == "insert" else None, None)
        self.draw_hud()
        if not ok:
            self.blink_heart(self.lives)
        last = self.round >= self.lv["rounds"] or self.lives <= 0
        self.next_btn.config(state="normal", text="CONCLUIR" if last else "PROXIMA")
        if self.lives <= 0:
            self.round = self.lv["rounds"]

    def show_banner(self, ok, text):
        cv = self.banner
        cv.delete("all")
        col, sh = (P["lime"], P["teal"]) if ok else (P["orange"], P["red"])
        tw = text_width(text, 3)
        pixel_text(cv, W / 2, 17, text, s=3, color=col, shadow=sh, anchor="center")
        grid, pal = (STAR, STAR_PAL) if ok else (SKULL, SKULL_PAL)
        iw, ih = sprite_size(grid, 3)
        draw_sprite(cv, grid, pal, W / 2 - tw / 2 - iw - 16, 17 - ih / 2, 3)
        draw_sprite(cv, grid, pal, W / 2 + tw / 2 + 16, 17 - ih / 2, 3)

    def blink_heart(self, idx, n=5):
        try:
            self.draw_hud(flash=idx if n % 2 == 1 else None)
            if n > 0:
                self._job = self.root.after(110, lambda: self.blink_heart(idx, n - 1))
        except tk.TclError:
            pass

    def cheat_text(self, q):
        if q["qt"] == "case":
            return opts_for(q["kind"], q["op"])[q["code"]]
        if q["qt"] == "click":
            return f"CLIQUE NO NO {q['node']}"
        if q["kind"] == "RB":
            return " ".join(f"{k}{'v' if c == 'R' else ''}" for k, c in q["pre"])
        return " ".join(map(str, q["pre"]))

    def feedback_text(self, q):
        if q["qt"] == "case":
            opts = opts_for(q["kind"], q["op"])
            t = f"Resposta: {opts[q['code']]}.\n" + explain_code(q["kind"], q["code"], q["node"])
            if len(q["events"]) > 1 and q["kind"] == "RB":
                t += "\n(Depois disso ainda houve outras correções subindo na árvore.)"
            return t
        if q["qt"] == "click":
            return (f"O nó desbalanceado era {q['node']}.\n" +
                    explain_code("AVL", q["code"], q["node"]) + "\nÁrvore corrigida exibida acima.")
        if q["kind"] == "RB":
            s = " ".join(f"{k}{'v' if c == 'R' else ''}" for k, c in q["pre"])
        else:
            s = " ".join(map(str, q["pre"]))
        return f"Pré-ordem correta: {s}\nÁrvore final exibida acima."

    def q_parts(self, q):
        verb = "Inserir" if q["op"] == "insert" else "Remover"
        nome = "AVL" if q["kind"] == "AVL" else "Rubro-Negra"
        tipo = {"case": "escolha", "click": "clique no nó", "preorder": "pré-ordem"}[q["qt"]]
        head = f"[{nome}] {verb} {q['key']}   (tipo: {tipo})"
        ordem = " ".join(map(str, q["keys"]))
        if q["qt"] == "click":
            tree = f"Árvore: inserir nesta ordem {ordem} e depois {q['key']} SEM corrigir"
        else:
            tree = f"Árvore: inserir nesta ordem {ordem}"
        if q["qt"] == "case":
            ask = "Pergunta: o que acontece primeiro?"
            ans = opts_for(q["kind"], q["op"])[q["code"]]
            why = explain_code(q["kind"], q["code"], q["node"])
        elif q["qt"] == "click":
            ask = "Pergunta: clique no nó desbalanceado mais fundo."
            ans = f"nó {q['node']}"
            why = explain_code("AVL", q["code"], q["node"])
        else:
            ask = "Pergunta: qual a pré-ordem da árvore final?"
            ans = self.cheat_text(q) + ("   (v = nó vermelho)" if q["kind"] == "RB" else "")
            why = ""
        return head, tree, ask, ans, why

    def answers_list(self):
        self.clear()
        bank = self.get_bank()
        top = tk.Frame(self.root, bg=P["bg"])
        top.pack(fill="x", padx=20, pady=(8, 2))
        title = self.canvas(top, 420, 48)
        title.pack(side="left")
        pixel_text(title, 4, 6, "RESPOSTAS", s=5, color=P["yellow"], shadow=P["red"])
        self.pbtn(top, "MENU", self.menu, P["panel2"], w=130, h=44, big=2).pack(side="right")
        self.pbtn(top, "VER ARVORES", lambda: self.answers_view(0, 0), P["sky"], w=250, h=44, big=2,
                  fg=P["ink"]).pack(side="right", padx=10)

        jump = tk.Frame(self.root, bg=P["bg"])
        jump.pack(pady=4)
        box = tk.Frame(self.root, bg=P["bg"])
        txt = tk.Text(box, width=106, height=33, bg=P["ink"], fg=P["white"], relief="flat", wrap="word",
                      font=(MONO, 10, "bold"), highlightthickness=4, highlightbackground=P["mute"],
                      highlightcolor=P["mute"], padx=10, pady=6, spacing1=1)
        sb = tk.Scrollbar(box, command=txt.yview, bg=P["panel2"], troughcolor=P["ink"], bd=0,
                          activebackground=P["mute"], highlightthickness=0)
        txt.config(yscrollcommand=sb.set)
        txt.pack(side="left")
        sb.pack(side="left", fill="y")
        box.pack(pady=4)
        txt.tag_configure("fase", foreground=P["yellow"], font=(MONO, 12, "bold"), spacing1=10, spacing3=4)
        txt.tag_configure("head", foreground=P["cyan"])
        txt.tag_configure("tree", foreground=P["soft"])
        txt.tag_configure("ask", foreground=P["white"])
        txt.tag_configure("ans", foreground=P["lime"])
        txt.tag_configure("why", foreground=P["soft"])
        for i, lv in enumerate(LEVELS):
            color, fg = self.lv_style(lv)
            self.pbtn(jump, str(i + 1), lambda i=i: txt.yview(f"f{i}"), color, w=64, h=36, font_size=11,
                      fg=fg).pack(side="left", padx=3)
            txt.mark_set(f"f{i}", "end-1c")
            txt.mark_gravity(f"f{i}", "left")
            txt.insert("end", f"FASE {i + 1}  -  {lv['name']}\n", "fase")
            for n, q in enumerate(bank[i], 1):
                head, tree, ask, ans, why = self.q_parts(q)
                txt.insert("end", f"{n}) {head}\n", "head")
                txt.insert("end", f"    {tree}\n", "tree")
                txt.insert("end", f"    {ask}\n", "ask")
                txt.insert("end", f"    RESPOSTA: {ans}\n", "ans")
                if why:
                    txt.insert("end", f"    Por quê: {why}\n", "why")
                txt.insert("end", "\n")
        txt.config(state="disabled")
        tk.Label(self.root, text="Use a rolagem do mouse ou os números das fases para pular. "
                                 "São as mesmas perguntas que aparecem no jogo.",
                 bg=P["bg"], fg=P["soft"], font=(MONO, 9, "bold")).pack(pady=2)

    def answers_view(self, li, qi, after=False):
        self.clear()
        bank = self.get_bank()
        flat = [(a, b) for a in range(len(LEVELS)) for b in range(len(bank[a]))]
        pos = flat.index((li, qi))
        q = bank[li][qi]
        lv = LEVELS[li]
        hdr = self.canvas(self.root, W, 56)
        hdr.pack(pady=(8, 0))
        pixel_text(hdr, 6, 8, f"FASE {li + 1} - PERGUNTA {qi + 1}/{len(bank[li])}", s=4, color=P["yellow"],
                   shadow=P["red"])
        pixel_text(hdr, W - 6, 36, lv["name"], s=2, color=P["lime"], shadow=P["ink"], anchor="e")
        cv = self.canvas(self.root, W, 330)
        cv.pack(pady=2)
        if after:
            draw_tree(cv, q["after"], q["kind"], q["key"] if q["op"] == "insert" else None, None)
        else:
            new = q["key"] if (q["op"] == "insert" and q["qt"] == "click") else None
            dele = q["key"] if q["op"] == "delete" else None
            draw_tree(cv, q["before"], q["kind"], new, dele)
        pixel_text(cv, 24, 18, "DEPOIS DA OPERACAO" if after else "ANTES DA OPERACAO", s=2,
                   color=P["lime"] if after else P["cyan"], shadow=P["ink"])
        head, tree, ask, ans, why = self.q_parts(q)
        box = self.panel(self.root)
        box.pack(fill="x", padx=20, pady=4)
        for text, col in ((head, P["cyan"]), (ask, P["white"]), ("RESPOSTA: " + ans, P["lime"]), (why, P["soft"])):
            if text:
                tk.Label(box, text=text, bg=P["panel"], fg=col, font=(MONO, 11, "bold"), wraplength=880,
                         justify="left", anchor="w").pack(fill="x", padx=14, pady=2)
        row = tk.Frame(self.root, bg=P["bg"])
        row.pack(pady=6)
        prev_ = flat[pos - 1] if pos > 0 else None
        next_ = flat[pos + 1] if pos + 1 < len(flat) else None
        self.pbtn(row, "< ANTERIOR", (lambda: self.answers_view(*prev_)) if prev_ else None, P["blue"], w=190,
                  h=46, big=2, state="normal" if prev_ else "disabled").pack(side="left", padx=5)
        self.pbtn(row, "VER ANTES" if after else "VER DEPOIS", lambda: self.answers_view(li, qi, not after),
                  P["yellow"], w=220, h=46, big=2, fg=P["ink"]).pack(side="left", padx=5)
        self.pbtn(row, "PROXIMA >", (lambda: self.answers_view(*next_)) if next_ else None, P["blue"], w=190,
                  h=46, big=2, state="normal" if next_ else "disabled").pack(side="left", padx=5)
        self.pbtn(row, "LISTA", self.answers_list, P["orange"], w=130, h=46, big=2,
                  fg=P["ink"]).pack(side="left", padx=5)

    def finish_level(self):
        i = self.li
        win = self.lives > 0
        bonus = self.lives * 100
        total = self.score + bonus
        record = False
        if win and not self.cheat:
            old = self.prog["best"].get(str(i))
            record = old is None or total > old
            self.prog["best"][str(i)] = max(old or 0, total)
            if i + 1 < len(LEVELS):
                self.prog["unlocked"] = max(self.prog["unlocked"], i + 2)
            self.save()
        self.clear()
        cv = self.canvas(self.root, W, 520)
        cv.pack(pady=(14, 0))
        starfield(cv, W, 520, seed=21 if win else 5, count=80)
        if win:
            rnd = random.Random(i)
            for _ in range(60):
                x, y = rnd.randrange(0, W, 4), rnd.randrange(0, 520, 4)
                cv.create_rectangle(x, y, x + 6, y + 6, fill=rnd.choice(
                    [P["yellow"], P["lime"], P["cyan"], P["orange"], RN_COLOR]), width=0)
            pixel_text(cv, W / 2, 30, "FASE COMPLETA!", s=8, color=P["yellow"], shadow=P["red"], anchor="n")
            if i == len(LEVELS) - 1:
                pixel_text(cv, W / 2, 112, "MESTRE DAS ARVORES!", s=5, color=P["cyan"], shadow=P["navy"],
                           anchor="n")
            else:
                pixel_text(cv, W / 2, 112, LEVELS[i]["name"], s=3, color=P["lime"], shadow=P["ink"], anchor="n")
            draw_sprite(cv, TREE, TREE_GREEN, 80, 150, 8)
            draw_sprite(cv, TREE, TREE_RED, W - 80 - 96, 150, 8)
        else:
            pixel_text(cv, W / 2, 40, "GAME OVER", s=11, color=P["red"], shadow=P["ink"], anchor="n")
            draw_sprite(cv, SKULL, SKULL_PAL, 100, 160, 12)
            draw_sprite(cv, SKULL, SKULL_PAL, W - 100 - 84, 160, 12)
            pixel_text(cv, W / 2, 140, "SEUS CORACOES ACABARAM", s=3, color=P["soft"], shadow=P["ink"], anchor="n")
        hw = 3 * 44 + 2 * 12
        draw_hearts(cv, self.lives, x=(W - hw) / 2, y=190, s=5, gap=12)
        if win:
            lines = [(f"PONTOS  {self.score}", P["white"]), (f"BONUS DE CORACOES  +{bonus}", P["lime"]),
                     (f"TOTAL  {total}", P["yellow"])]
        else:
            lines = [(f"PONTOS  {self.score}", P["white"]), ("REVEJA A TEORIA E TENTE DE NOVO!", P["orange"])]
        y = 262
        for t, c in lines:
            pixel_text(cv, W / 2, y, t, s=4 if c == P["yellow"] else 3, color=c, shadow=P["ink"], anchor="n")
            y += 44
        if self.cheat:
            pixel_text(cv, W / 2, y + 6, "MODO GABARITO: PONTOS NAO SALVOS", s=2, color=P["yellow"],
                       shadow=P["ink"], anchor="n")
        elif record:
            pixel_text(cv, W / 2, y + 6, "NOVO RECORDE!", s=3, color=P["orange"], shadow=P["red"], anchor="n")

        row = tk.Frame(self.root, bg=P["bg"])
        row.pack(pady=10)
        if win and i + 1 < len(LEVELS):
            self.pbtn(row, "PROXIMA FASE", lambda: self.level_intro(i + 1), P["green"], w=270, h=52, big=2,
                      fg=P["ink"]).pack(side="left", padx=8)
        if not win:
            self.pbtn(row, "TENTAR DE NOVO", lambda: self.start_level(i), P["orange"], w=300, h=52, big=2,
                      fg=P["ink"]).pack(side="left", padx=8)
        self.pbtn(row, "MENU", self.menu, P["panel2"], w=170, h=52, big=2).pack(side="left", padx=8)

    def lab(self):
        self.clear()
        self.avl = AVLTree()
        self.rb = RBTree()
        top = tk.Frame(self.root, bg=P["bg"])
        top.pack(fill="x", padx=20, pady=(8, 2))
        title = self.canvas(top, 560, 48)
        title.pack(side="left")
        pixel_text(title, 4, 6, "LABORATORIO", s=5, color=P["yellow"], shadow=P["red"])
        self.pbtn(top, "MENU", self.menu, P["panel2"], w=140, h=44, big=2).pack(side="right")

        self.cv_avl = self.canvas(self.root, W, 268)
        self.cv_avl.pack(pady=2)
        self.cv_rb = self.canvas(self.root, W, 268)
        self.cv_rb.pack(pady=2)

        ctl = tk.Frame(self.root, bg=P["bg"])
        ctl.pack(pady=4)
        self.lab_entry = tk.Entry(ctl, width=18, font=(MONO, 15, "bold"), bg=P["ink"], fg=P["lime"],
                                  insertbackground=P["lime"], relief="flat", highlightthickness=4,
                                  highlightbackground=P["mute"], highlightcolor=P["sky"])
        self.lab_entry.pack(side="left", padx=6, ipady=6)
        self.lab_entry.bind("<Return>", lambda e: self.lab_op("insert"))
        self.pbtn(ctl, "INSERIR", lambda: self.lab_op("insert"), P["green"], w=140, h=44, big=2,
                  fg=P["ink"]).pack(side="left", padx=4)
        self.pbtn(ctl, "REMOVER", lambda: self.lab_op("delete"), P["red"], w=140, h=44, big=2).pack(side="left", padx=4)
        self.pbtn(ctl, "ALEATORIO", self.lab_random, P["blue"], w=170, h=44, big=2).pack(side="left", padx=4)
        self.pbtn(ctl, "LIMPAR", self.lab_clear, P["panel2"], w=130, h=44, big=2).pack(side="left", padx=4)

        self.log = tk.Text(self.root, height=6, width=104, bg=P["ink"], fg=P["lime"], relief="flat",
                           font=(MONO, 10, "bold"), state="disabled", highlightthickness=4,
                           highlightbackground=P["mute"], highlightcolor=P["mute"], padx=8, pady=4)
        self.log.tag_configure("avl", foreground=P["cyan"])
        self.log.tag_configure("rn", foreground=RN_COLOR)
        self.log.tag_configure("info", foreground=P["yellow"])
        self.log.pack(pady=4)
        self.lab_log("Digite um ou mais valores (ex: 10 20 30) e clique em INSERIR ou REMOVER.", "info")
        self.lab_draw()

    def lab_log(self, text, tag=None):
        self.log.config(state="normal")
        self.log.insert("end", text + "\n", tag)
        self.log.see("end")
        self.log.config(state="disabled")

    def lab_draw(self, new=None, dele=None):
        for cv, t in ((self.cv_avl, self.avl), (self.cv_rb, self.rb)):
            draw_tree(cv, t.snapshot(), t.kind, new, dele)
        pixel_text(self.cv_avl, 24, 18, "AVL", s=3, color=P["cyan"], shadow=P["ink"])
        pixel_text(self.cv_avl, 110, 22, "NUMERO AO LADO = FATOR DE BALANCEAMENTO", s=1, color=P["soft"])
        pixel_text(self.cv_rb, 24, 18, "RUBRO-NEGRA", s=3, color=RN_COLOR, shadow=P["ink"])

    def lab_op(self, op):
        try:
            vals = [int(x) for x in self.lab_entry.get().replace(",", " ").split()]
        except ValueError:
            self.lab_log("Valor inválido: use apenas números inteiros.", "info")
            return
        if not vals:
            return
        last = None
        for v in vals:
            if op == "insert":
                if self.avl.contains(v):
                    self.lab_log(f"{v} já existe (duplicatas ignoradas).", "info")
                    continue
                self.avl.insert(v)
                ea = list(self.avl.events)
                self.rb.insert(v)
                er = list(self.rb.events)
                self.lab_log(f"+{v}   AVL: {self.describe('AVL', 'insert', ea)}", "avl")
                self.lab_log(f"      RN:  {self.describe('RB', 'insert', er)}", "rn")
            else:
                if not self.avl.contains(v):
                    self.lab_log(f"{v} não está na árvore.", "info")
                    continue
                self.avl.delete(v)
                ea = list(self.avl.events)
                self.rb.delete(v)
                er = list(self.rb.events)
                self.lab_log(f"-{v}   AVL: {self.describe('AVL', 'delete', ea)}", "avl")
                self.lab_log(f"      RN:  {self.describe('RB', 'delete', er)}", "rn")
            last = v
        self.lab_entry.delete(0, "end")
        self.lab_draw(last if op == "insert" else None)

    def describe(self, kind, op, events):
        if not events:
            return "sem correções"
        opts = opts_for(kind, op)
        parts = []
        for code, key in events:
            parts.append(opts.get(code, code) + (f" [nó {key}]" if key is not None and kind == "AVL" else ""))
        return "; ".join(parts)

    def lab_random(self):
        free = [x for x in range(1, 100) if not self.avl.contains(x)]
        if free:
            self.lab_entry.delete(0, "end")
            self.lab_entry.insert(0, str(random.choice(free)))
            self.lab_op("insert")

    def lab_clear(self):
        self.avl = AVLTree()
        self.rb = RBTree()
        self.lab_log("--- árvores limpas ---", "info")
        self.lab_draw()


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
