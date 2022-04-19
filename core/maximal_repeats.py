from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


repeats_set: set[tuple[str, str]] = set()


@dataclass
class Node:
    data: dict[str, int]
    next: Optional[Node] = None


@dataclass
class Interval:
    lcp_value: int = 0
    lb: int = 0
    rb: int = -1
    child_list: list[Interval] = field(default_factory=list)
    pos_sets: Node = None

    def update_child_list(self, interval: Interval) -> None:
        self.child_list.append(interval)

    def __str__(self) -> str:
        return f"lb={self.rb}, rb={self.rb}, lcp_value={self.lcp_value}"


class SpecialStack:
    def __init__(self) -> None:
        self.__stack = []

    def top(self) -> Interval:
        if len(self.__stack) == 0:
            raise Exception("Trying to access top on an empty stack")
        else:
            return self.__stack[-1]

    def pop(self) -> Interval:
        return self.__stack.pop()

    def push(self, interval: Interval) -> None:
        self.__stack.append(interval)

    def is_empty(self) -> bool:
        return len(self.__stack) == 0


def process(lcp_interval: Interval, suf_tab: list[int], s: str) -> None:
    # linked list to union the position sets and save it to the parent node(propagate)
    pos_set_list_head: Optional[Node] = None
    prev: Optional[Node] = None
    # init the alphabet set over the input string
    alphabet_set: set[str] = set(s)
    # init the dict that maps the alphabet to a pos p, -1 is for undefined at init
    alphabet_pos_map: dict[str, int] = {alphabet: -1 for alphabet in alphabet_set}
    lcp: int = lcp_interval.lcp_value

    for j in range(0, len(lcp_interval.child_list)):
        child_interval: Interval = lcp_interval.child_list[j]
        # position set for this child
        p_set: set[int] = set()
        lb: int = child_interval.lb
        rb: int = child_interval.rb

        for i in range(lb, rb + 1):
            p_set.add(suf_tab[i])

        for alphabet in alphabet_set:
            for p in p_set:
                if p != 0 and (s[p - 1] == alphabet):
                    alphabet_pos_map[alphabet] = p

        # if this is the first child in this subtree
        if pos_set_list_head is None:
            pos_set_list_head = Node(alphabet_pos_map)
            prev = pos_set_list_head
        # start linking the previous position sets to be used by the next child
        else:
            new_node = Node(alphabet_pos_map)
            new_node.next = prev.next
            prev.next = new_node
            prev = new_node

        curr = pos_set_list_head

        # start processing all the position sets collected up to this child interval
        while curr is not None:
            last_alphabet_pos_map: dict[str, int] = curr.data

            for a in alphabet_set:
                for b in alphabet_set:
                    p = last_alphabet_pos_map[a]

                    if a != b and last_alphabet_pos_map[a] != -1 and alphabet_pos_map[b] != -1:
                        p_prime = alphabet_pos_map[b]

                        # print(f"({p}, {p + lcp}), ({p_prime}, {p_prime + lcp})")
                        left: str = s[p: p + lcp + 1]
                        right: str = s[p_prime: p_prime + lcp + 1]

                        # without this, I see abnormal pairs...don't know if this is ok to do?
                        if left == right:
                            repeats_set.add((left, right))

            curr = curr.next

    # finally, propagate the computed position sets to the parent interval
    lcp_interval.pos_sets = pos_set_list_head


def perform_bottom_up_traversal(s, suf_tab, lcp_table) -> set[tuple[str, str]]:
    # add the sentinel
    s = s + '$'
    last_interval: Optional[Interval] = None
    stack: SpecialStack = SpecialStack()

    # init stack with an empty interval
    stack.push(Interval())

    for i in range(1, len(lcp_table)):
        lb: int = i - 1
        top: Interval = stack.top()

        while lcp_table[i] < top.lcp_value:
            top.rb = i - 1
            last_interval: Interval = stack.pop()

            # we know the child intervals now, process this subtree
            process(last_interval, suf_tab, s)

            lb: int = last_interval.lb
            top: Interval = stack.top()

            if lcp_table[i] <= top.lcp_value:
                top.update_child_list(last_interval)
                last_interval = None

        if lcp_table[i] > top.lcp_value:
            if last_interval is not None:
                # -1 here represents undefined or bottom value
                stack.push(Interval(lcp_table[i], lb, -1, [last_interval]))
                last_interval = None
            else:
                stack.push(Interval(lcp_table[i], lb, -1, []))

    stack.top().rb = len(lcp_table)

    # process the root
    process(stack.pop(), suf_tab, s)

    return repeats_set
