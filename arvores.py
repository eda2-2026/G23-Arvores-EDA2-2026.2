
from avl import AVLTree
from rbtree import RBTree


def new_tree(kind):
    return AVLTree() if kind == "AVL" else RBTree()
