from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Node:
    data: list[int]
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
    pos_set_list_head: Optional[Node] = None
    prev: Optional[Node] = None

    lcp: int = lcp_interval.lcp_value

    for j in range(0, len(lcp_interval.child_list)):
        pos_set: list[int] = [-1] * 26
        child_interval: Interval = lcp_interval.child_list[j]
        p_set: set[int] = set()
        lb: int = child_interval.lb
        rb: int = child_interval.rb

        for i in range(lb, rb + 1):
            p_set.add(suf_tab[i])

        for i in range(0, 26):
            for p in p_set:
                if p != 0 and (s[p - 1] == chr(i + 97)):
                    pos_set[i] = p

        if pos_set_list_head is None:
            pos_set_list_head = Node(pos_set)
            prev = pos_set_list_head
        else:
            new_node = Node(pos_set)
            new_node.next = prev.next
            prev.next = new_node
            prev = new_node

        curr = pos_set_list_head

        while curr is not None:
            last_pos_set = curr.data

            for i in range(0, 26):
                for k in range(0, 26):
                    p = last_pos_set[i]
                    if i != k and last_pos_set[i] != -1 and pos_set[k] != -1:
                        p_prime = pos_set[k]

                        if p < p_prime:
                            print(f"({p}, {p + lcp - 1}), ({p_prime}, {p_prime + lcp - 1})")

            curr = curr.next

    lcp_interval.pos_sets = pos_set_list_head


def perform_bottom_up_traversal(s, suf_tab, lcp_table) -> None:
    last_interval: Optional[Interval] = None
    stack: SpecialStack = SpecialStack()

    stack.push(Interval())

    for i in range(1, len(lcp_table)):
        lb: int = i - 1
        top: Interval = stack.top()
        while lcp_table[i] < top.lcp_value:
            top.rb = i - 1
            last_interval: Interval = stack.pop()

            process(last_interval, suf_tab, s)

            lb: int = last_interval.lb
            top: Interval = stack.top()

            if lcp_table[i] <= top.lcp_value:
                top.update_child_list(last_interval)
                last_interval = None

        if lcp_table[i] > top.lcp_value:
            if last_interval is not None:
                stack.push(Interval(lcp_table[i], lb, -1, [last_interval]))
                last_interval = None
            else:
                stack.push(Interval(lcp_table[i], lb, -1, []))

    stack.top().rb = len(lcp_table)
    process(stack.pop(), suf_tab, s)
