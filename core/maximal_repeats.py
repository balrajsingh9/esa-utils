from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Set, Tuple

repeats_set: set[tuple[tuple[int, int], tuple[int, int]]] = set()


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
        return f"lb={self.lb}, rb={self.rb}, lcp_value={self.lcp_value}, children={self.child_list}"


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


def process(lcp_interval: Interval, suf_tab: list[int], s: str, bwt_table: list[str]) -> None:
    # linked list to union the position sets and save it to the parent node(propagate)
    pos_set_list_head: Optional[Node] = None
    prev: Optional[Node] = None
    # init the alphabet set over the input string
    alphabet_set: set[str] = set(s)
    # init the dict that maps the alphabet to a pos p, -1 is for undefined at init
    alphabet_pos_map: dict[str, int] = {alphabet: -1 for alphabet in alphabet_set}
    lcp = lcp_interval.lcp_value

    for child_interval in lcp_interval.child_list:
        lb: int = child_interval.lb
        rb: int = child_interval.rb

        for alphabet in alphabet_set:
            for i in range(lb, rb + 1):
                if bwt_table[i] == alphabet:
                    alphabet_pos_map[alphabet] = suf_tab[i]

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
                    if a != b:
                        p = last_alphabet_pos_map[a]
                        p_prime = alphabet_pos_map[b]

                        if p < p_prime != -1 and p != -1 and bwt_table[p] != bwt_table[p_prime]:
                            repeats_set.add(((p, p + lcp - 1), (p_prime, p_prime + lcp - 1)))

            curr = curr.next

    # finally, propagate the computed position sets to the parent interval
    lcp_interval.pos_sets = pos_set_list_head


def find_maximal_repeats(s: str, suf_tab: list[int], lcp_table: list[int], bwt_table: list[str]) -> \
        set[tuple[tuple[int, int], tuple[int, int]]]:
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
            process(last_interval, suf_tab, s, bwt_table)

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

    return repeats_set
