#!/usr/bin/env python3
"""
ORDENAASARVORES - o jogo das árvores balanceadas (AVL e Rubro-Negra)

Como rodar:   python ordenaasarvores.py
"""
import tkinter as tk

from interface import App


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
