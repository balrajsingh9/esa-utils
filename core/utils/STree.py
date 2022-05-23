from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Node:
    idx: int = -1
    depth: int = -1
    parent: Optional[Node] = None
    children: dict[str, Node] = field(default_factory=dict)
    s_link: Optional[Node] = None

    def __str__(self) -> str:
        return f"children={list(self.children.keys())}"


def create_node(s: str, u: Node, depth: int) -> Node:
    parent = u.parent
    v = Node(u.idx, depth, u.parent)

    v.children[s[u.idx + depth]] = u
    u.parent = v

    parent.children[s[u.idx + parent.depth]] = v
    v.parent = parent

    return v


def create_and_attach_leaf(s: str, i: int, u: Node, depth: int) -> None:
    leaf = Node()
    leaf.idx = i
    leaf.depth = len(s) - i

    u.children[s[i + depth]] = leaf
    leaf.parent = u


def compute_s_link(s: str, u: Node) -> None:
    d = u.depth
    v = u.parent.s_link

    while v.depth < d - 1:
        v = v.children[s[u.idx + v.depth + 1]]

    # if no node at (v, d - 1), then create one
    if v.depth > d - 1:
        v = create_node(s, v, d - 1)

    u.s_link = v


def traverse_edge(text: str, pattern: str, idx: int, start: int, end: int) -> tuple[int, int]:
    i: int = start

    while i < end and idx < len(pattern):
        if text[i] != pattern[idx]:
            return -1, idx

        i += 1
        idx += 1

    # we have a match
    if idx == len(pattern):
        return 1, idx

    # 0 means there are still more characters to match
    return 0, idx


def perform_search(node: Node, text: str, pattern: str, idx: int) -> int:
    # case where the pattern starts with same alphabet as text
    if node.idx == 0 and node.depth >= len(pattern):
        return text.startswith(pattern)

    if node.idx != 0:

        # We will traverse the edge and match alphabet by alphabet
        # The edge label has length = end - start + 1, where
        # start = node.idx + node.parent.depth
        # end = node.idx + node.depth

        search_res, idx = traverse_edge(text, pattern, idx, node.idx + node.parent.depth, node.idx + node.depth)

        if search_res != 0:
            return search_res

    if pattern[idx] in node.children:
        return perform_search(node.children[pattern[idx]], text, pattern, idx)

    return -1


@dataclass
class STree:
    root: Node = Node()
    text: str = ""
    root.parent = root
    root.s_link = root
    root.depth = 0
    root.idx = 0

    def build_using_mccreight(self, s: str) -> None:
        """
        Construct a suffix tree for string s using McCreight's linear time algorithm
        as described here: https://www.cs.helsinki.fi/u/tpkarkka/opetus/13s/spa/lecture10-2x4.pdf
        """
        s += '$'
        self.text = s

        u = self.root
        d = 0

        for i in range(len(s)):
            while d == u.depth and s[i + d] in u.children:
                u = u.children[s[i + d]]
                d += 1

                while d < u.depth and s[u.idx + d] == s[i + d]:
                    d += 1

            if d < u.depth:
                u = create_node(s, u, d)

            create_and_attach_leaf(s, i, u, d)

            if u.s_link is None:
                compute_s_link(s, u)

            u = u.s_link
            d = max(0, d - 1)

    def search(self, pattern: str) -> bool:
        if not self.root:
            return False

        if len(pattern) == 0:
            return True

        search_res: int = perform_search(self.root, self.text, pattern, 0)

        return search_res == 1

