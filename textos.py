"""Textos do jogo: opções de resposta, explicações e teoria."""

AVL_OPTS = {
    "NONE": "Nenhuma rotação",
    "LL": "Rotação simples à direita (LL)",
    "RR": "Rotação simples à esquerda (RR)",
    "LR": "Rotação dupla esquerda-direita (LR)",
    "RL": "Rotação dupla direita-esquerda (RL)",
}
RB_INS_OPTS = {
    "ROOT": "Só pintar a raiz de preto",
    "NONE": "Nada a corrigir (pai é preto)",
    "RECOLOR": "Tio vermelho: recolorir",
    "SINGLE": "Tio preto, linha reta: rotação simples",
    "DOUBLE": "Tio preto, zigue-zague: rotação dupla",
}
RB_DEL_OPTS = {
    "NONE": "Nada a corrigir (saiu um nó vermelho)",
    "PAINT": "Só pintar o substituto vermelho de preto",
    "D1": "Irmão vermelho: recolorir + rotacionar o pai",
    "D2": "Irmão preto, sobrinhos pretos: irmão vira vermelho",
    "D3": "Irmão preto, sobrinho de perto vermelho: girar o irmão",
    "D4": "Irmão preto, sobrinho de longe vermelho: girar o pai",
}


def opts_for(kind, op):
    if kind == "AVL":
        return AVL_OPTS
    return RB_INS_OPTS if op == "insert" else RB_DEL_OPTS


EXPL = {
    "NONE_AVL": "Nenhum nó ficou com |FB| > 1, então a árvore continua balanceada e não há rotação.",
    "LL": "O nó {k} ficou com FB=+2 e o lado esquerdo pesa mais (filho esquerdo com FB >= 0): rotação simples à direita.",
    "RR": "O nó {k} ficou com FB=-2 e o lado direito pesa mais (filho direito com FB <= 0): rotação simples à esquerda.",
    "LR": "O nó {k} ficou com FB=+2, mas o filho esquerdo pende para a direita (FB < 0): gira o filho à esquerda e depois o nó à direita.",
    "RL": "O nó {k} ficou com FB=-2, mas o filho direito pende para a esquerda (FB > 0): gira o filho à direita e depois o nó à esquerda.",
    "ROOT": "O novo nó é a raiz. Raiz é sempre preta, então só é preciso pintá-la.",
    "NONE_RB": "O nó removido/inserido não violou nenhuma regra (pai preto ou nó removido vermelho).",
    "RECOLOR": "Pai e tio são vermelhos: pai e tio viram pretos e o avô vira vermelho. O problema pode subir para o avô.",
    "SINGLE": "Pai vermelho, tio preto e o nó está em linha reta com o avô: rotação simples no avô, trocando as cores.",
    "DOUBLE": "Pai vermelho, tio preto e o nó está em zigue-zague: primeiro gira o pai para alinhar, depois gira o avô.",
    "PAINT": "O nó que saiu era preto, mas o substituto é vermelho: basta pintá-lo de preto e a altura-negra se mantém.",
    "D1": "Caso 1: o irmão é vermelho. Pinta o irmão de preto, o pai de vermelho e gira o pai. Cai em outro caso.",
    "D2": "Caso 2: irmão preto com os dois filhos pretos. Pinta o irmão de vermelho e o 'preto extra' sobe para o pai.",
    "D3": "Caso 3: irmão preto, sobrinho de longe preto e o de perto vermelho. Gira o irmão para cair no caso 4.",
    "D4": "Caso 4: irmão preto com sobrinho de longe vermelho. O irmão herda a cor do pai, pai e sobrinho ficam pretos e gira o pai.",
}


def explain_code(kind, code, key):
    if code == "NONE":
        t = EXPL["NONE_AVL" if kind == "AVL" else "NONE_RB"]
    else:
        t = EXPL[code]
    return t.format(k=key)


THEORY = {
    ("AVL", "insert"): (
        "AVL: fator de balanceamento FB = altura(esq) - altura(dir). Precisa ficar entre -1 e +1.\n"
        "  FB=+2, filho esq. com FB>=0  ->  rotação simples à direita (LL)\n"
        "  FB=-2, filho dir. com FB<=0  ->  rotação simples à esquerda (RR)\n"
        "  FB=+2, filho esq. com FB<0   ->  dupla esquerda-direita (LR)\n"
        "  FB=-2, filho dir. com FB>0   ->  dupla direita-esquerda (RL)\n"
        "Na inserção, o nó a corrigir é o desbalanceado mais fundo no caminho do novo nó."
    ),
    ("AVL", "delete"): (
        "AVL na remoção: nó com dois filhos é trocado pelo seu sucessor (menor da subárvore direita).\n"
        "Depois sobe-se pelo caminho recalculando FB. Aqui perguntamos a PRIMEIRA rotação.\n"
        "Atenção: se o filho pesado tem FB=0, a rotação é simples (LL ou RR)."
    ),
    ("RB", "insert"): (
        "Rubro-Negra: raiz preta; vermelho não tem filho vermelho; todo caminho tem o mesmo nº de pretos.\n"
        "O novo nó nasce VERMELHO. Olhe o pai:\n"
        "  pai preto -> nada a fazer\n"
        "  pai vermelho e tio vermelho -> recolorir (pai e tio pretos, avô vermelho)\n"
        "  pai vermelho e tio preto -> rotação: simples se em linha reta, dupla se em zigue-zague"
    ),
    ("RB", "delete"): (
        "Rubro-Negra na remoção (nó removido preto deixa um 'preto a menos'):\n"
        "  removeu vermelho -> nada | substituto vermelho -> pinta de preto\n"
        "  Caso 1: irmão vermelho -> recolore e gira o pai\n"
        "  Caso 2: irmão preto, sobrinhos pretos -> irmão vira vermelho\n"
        "  Caso 3: irmão preto, sobrinho de perto vermelho e de longe preto -> gira o irmão\n"
        "  Caso 4: sobrinho de longe vermelho -> gira o pai e acerta as cores\n"
        "Sucessor = menor da subárvore direita, quando o nó tem dois filhos."
    ),
}
