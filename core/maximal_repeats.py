from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Set, Tuple

UNDEFINED: int = -1
alphabet_set: set[str]


@dataclass
class ListNode:
    data: int
    next: Optional[ListNode] = None


PositionSets = dict[str, ListNode]
Repeats = list[tuple[tuple[int, int], tuple[int, int]]]
maximal_repeats: Repeats = []


@dataclass
class Interval:
    lcp_value: int = 0
    lb: int = 0
    rb: int = -1
    child_list: list[Interval] = field(default_factory=list)
    pos_sets: PositionSets = field(default_factory=dict)

    def update_child_list(self, interval: Interval) -> None:
        self.child_list.append(interval)

    def __str__(self) -> str:
        return f"lb={self.lb}, rb={self.rb}, lcp_value={self.lcp_value}, child_list={self.child_list}"


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


def process_leaves(lcp_interval: Interval, suf_tab: list[int], bwt_table: list[str]) -> None:
    lb, rb, lcp = lcp_interval.lb, lcp_interval.rb, lcp_interval.lcp_value
    pos_sets: PositionSets = {}

    for alphabet in alphabet_set:
        for i in range(lb, rb + 1):
            if bwt_table[i] == alphabet:
                if alphabet in pos_sets:
                    curr_child_alphabet_itr = pos_sets[alphabet]

                    while curr_child_alphabet_itr.next is not None:
                        curr_child_alphabet_itr = curr_child_alphabet_itr.next

                    curr_child_alphabet_itr.next = ListNode(suf_tab[i])

                else:
                    pos_sets[alphabet] = ListNode(suf_tab[i])

    # process the leaves
    for a in pos_sets:
        for b in pos_sets:
            if a != b:
                a_itr = pos_sets[a]
                b_itr_head = pos_sets[b]

                while a_itr is not None:
                    b_itr = b_itr_head
                    p = a_itr.data

                    while b_itr is not None:
                        p_prime = b_itr.data

                        if p_prime > p and lcp > 0:
                            maximal_repeats.append(((p, p + lcp), (p_prime, p_prime + lcp)))

                        b_itr = b_itr.next
                    a_itr = a_itr.next

    lcp_interval.pos_sets = pos_sets


def process(lcp_interval: Interval, suf_tab: list[int], bwt_table: list[str]) -> None:
    # linked list to union the position sets and save it to the parent node(propagate)
    prev_child_alphabet_post_sets: PositionSets = {}
    lcp = lcp_interval.lcp_value

    if len(lcp_interval.child_list) == 0:
        process_leaves(lcp_interval, suf_tab, bwt_table)
    else:
        for child_interval in lcp_interval.child_list:
            curr_child_alphabet_pos_sets: PositionSets = child_interval.pos_sets

            if len(prev_child_alphabet_post_sets.keys()) == 0:
                prev_child_alphabet_post_sets = curr_child_alphabet_pos_sets
            else:
                for curr_key in curr_child_alphabet_pos_sets:
                    for prev_key in prev_child_alphabet_post_sets:
                        if curr_key != prev_key:
                            curr_alphabet_list_head = curr_child_alphabet_pos_sets[curr_key]
                            prev_alphabet_list_head = prev_child_alphabet_post_sets[prev_key]
                            curr_alphabet_list_ptr = curr_alphabet_list_head
                            prev_alphabet_list_ptr = prev_alphabet_list_head

                            while curr_alphabet_list_ptr is not None:
                                prev_alphabet_list_ptr = prev_alphabet_list_head
                                while prev_alphabet_list_ptr is not None:
                                    p = prev_alphabet_list_ptr.data
                                    p_prime = curr_alphabet_list_ptr.data

                                    if p_prime > p and lcp > 0:
                                        maximal_repeats.append(((p, p + lcp), (p_prime, p_prime + lcp)))

                                    prev_alphabet_list_ptr = prev_alphabet_list_ptr.next

                                curr_alphabet_list_ptr = curr_alphabet_list_ptr.next
                for key in curr_child_alphabet_pos_sets:
                    curr_child_ptr_itr = curr_child_alphabet_pos_sets[key]

                    if key in prev_child_alphabet_post_sets:
                        last_set = prev_child_alphabet_post_sets[key]
                        last_set_ptr = last_set
                        prev_ptr_last_set = last_set

                        while last_set_ptr is not None:
                            prev_ptr_last_set = last_set_ptr
                            last_set_ptr = last_set_ptr.next

                        prev_ptr_last_set.next = curr_child_ptr_itr
                    else:
                        prev_child_alphabet_post_sets[key] = curr_child_ptr_itr

        lcp_interval.pos_sets = prev_child_alphabet_post_sets


def find_maximal_repeats(s: str, suf_tab: list[int], lcp_table: list[int], bwt_table: list[str]) -> Repeats:
    # add the sentinel
    s = s + '$'
    # init the alphabet set over the input string
    global alphabet_set
    alphabet_set = set(s)
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
            process(last_interval, suf_tab, bwt_table)

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

    return maximal_repeats
