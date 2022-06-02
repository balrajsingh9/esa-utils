from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

MaximalRepeats = list[tuple[tuple[int, int], tuple[int, int]]]


@dataclass
class ListNode:
    data: int
    next: Optional[ListNode] = None


@dataclass
class Node:
    idx: int = -1
    depth: int = -1
    parent: Optional[Node] = None
    children: dict[str, Node] = field(default_factory=dict)
    s_link: Optional[Node] = None
    pos_list: dict[str, ListNode] = field(default_factory=dict)

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


def get_lcp(node: Node) -> int:
    return 0 if Node is None else (node.parent.idx + node.parent.depth)


def process_lists(node: Node, sorted_children: list, maximal_repeats: MaximalRepeats):
    # get lcp of parent node
    lcp = get_lcp(node)
    prev_child_pos_list: Optional[dict[str, ListNode]] = None

    for val in sorted_children:
        curr_child = node.children[val]
        curr_child_pos_list = curr_child.pos_list

        if prev_child_pos_list is None:
            prev_child_pos_list = curr_child_pos_list
        else:
            for curr_key in curr_child_pos_list:
                for prev_key in prev_child_pos_list:
                    if prev_key != curr_key:
                        prev_child_itr = prev_child_pos_list[prev_key]
                        curr_child_itr_head = curr_child_pos_list[curr_key]

                        while prev_child_itr is not None:
                            curr_child_itr = curr_child_itr_head
                            p = prev_child_itr.data

                            while curr_child_itr is not None:
                                p_prime = curr_child_itr.data

                                if p_prime > p and lcp > 0:
                                    maximal_repeats.append(((p, p + lcp), (p_prime, p_prime + lcp)))

                                curr_child_itr = curr_child_itr.next

                            prev_child_itr = prev_child_itr.next
            # start the union of all prev children pos sets with curr child pos set
            for key in curr_child_pos_list:
                curr_value = curr_child_pos_list[key]

                if key in prev_child_pos_list:
                    prev_pos_list_itr = prev_child_pos_list[key]

                    # find the tail of this list indexed by key
                    while prev_pos_list_itr.next is not None:
                        prev_pos_list_itr = prev_pos_list_itr.next

                    # link the pos of key found from curr_child to prev_child
                    prev_pos_list_itr.next = curr_value
                else:
                    prev_child_pos_list[key] = curr_value

    # prev_child_pos_list contains the union of all the children pos sets
    node.pos_list = prev_child_pos_list


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

    def find_maximal_repeats(self) -> MaximalRepeats:
        maximal_repeats: MaximalRepeats = []

        def bottom_up_traversal(node):
            if node.children:
                sorted_children = sorted(node.children)
                for val in sorted_children:
                    bottom_up_traversal(node.children[val])

                process_lists(node, sorted_children, maximal_repeats)
            else:
                node.pos_list[self.text[node.idx - 1]] = ListNode(node.idx)

        bottom_up_traversal(self.root)

        return maximal_repeats
