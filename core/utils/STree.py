from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Node:
    s_link: Optional[Node] = None
    children: dict[str, Node] = field(default_factory=dict)
    start: int = -1
    depth: int = -1
    parent: Optional[Node] = None


def create_node(s: str, u: Node, depth: int) -> Node:
    old_p = u.parent
    v = Node()
    v.start = u.start
    v.depth = depth
    v.children[s[u.start + depth]] = u

    u.parent = v
    old_p.children[s[v.start + old_p.depth]] = v
    v.parent = old_p

    return v


def create_and_attach_leaf(s: str, i: int, u: Node, depth: int) -> None:
    leaf = Node()
    leaf.start = i
    leaf.depth = len(s) - i

    u.children[s[i + depth]] = leaf
    leaf.parent = u


def compute_s_link(s: str, u: Node) -> None:
    d = u.depth
    v = u.parent.s_link

    while v.depth < d - 1:
        v = v.children[s[u.start + v.depth + 1]]

    # if no node at (v, d - 1), then create one
    if v.depth > d - 1:
        create_node(s, v, d - 1)

    u.s_link = v


@dataclass
class STree:
    root: Node = Node()
    root.parent = root
    root.s_link = root
    root.depth = 0
    root.start = 0

    def build_using_mccreight(self, s: str) -> None:
        """
        Construct a suffix tree for string s using McCreight's linear time algorithm
        as described here: https://www.cs.helsinki.fi/u/tpkarkka/opetus/13s/spa/lecture10-2x4.pdf
        """
        s = s + '$'

        u = self.root
        d = 0

        for i in range(len(s)):
            suffix = s[i + d]
            while d == u.depth and suffix in u.children:
                u = u.children[suffix]
                d += 1

                while d < u.depth and s[u.start + d] == s[i + d]:
                    d += 1

            if d < u.depth:
                u = create_node(s, u, d)

            create_and_attach_leaf(s, i, u, d)

            if u.s_link is None:
                compute_s_link(s, u)

            u = u.s_link
            d = max(0, d - 1)

