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

    def update_child_list(self, interval: Interval, suf_tab, bwt_tab) -> None:
        # append leaves for non-root internal nodes
        if self.lcp_value > 0:
            for i in range(self.lb, interval.lb):
                self.child_list.append(Interval(lb=i, rb=i, child_list=[], pos_sets={bwt_tab[i]: ListNode(suf_tab[i])}))

        self.child_list.append(interval)

        # append leaves for non-root internal nodes
        if self.lcp_value > 0:
            for i in range(interval.rb, self.rb):
                self.child_list.append(Interval(lb=i, rb=i, child_list=[], pos_sets={bwt_tab[i]: ListNode(suf_tab[i])}))

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
    parent_pos_sets: PositionSets = {}
    last_leaf_pos_set: PositionSets = {}

    for i in range(lb, rb + 1):
        alphabet: str = bwt_table[i]
        curr_child_pos_set: PositionSets = {alphabet: ListNode(suf_tab[i])}

        if len(last_leaf_pos_set.keys()) == 0:
            last_leaf_pos_set = curr_child_pos_set
            parent_pos_sets[alphabet] = curr_child_pos_set[alphabet]
        else:
            for prev_key in last_leaf_pos_set:
                for curr_key in curr_child_pos_set:
                    if prev_key != curr_key:
                        p = last_leaf_pos_set[prev_key].data
                        p_prime = curr_child_pos_set[curr_key].data

                        if p_prime > p and lcp > 0:
                            maximal_repeats.append(((p, p + lcp), (p_prime, p_prime + lcp)))

            for prev_key in last_leaf_pos_set:
                for curr_key in curr_child_pos_set:
                    if prev_key in parent_pos_sets:
                        parent_pos_sets[prev_key].next = curr_child_pos_set[curr_key]
                    else:
                        parent_pos_sets[curr_key] = curr_child_pos_set[curr_key]

    lcp_interval.pos_sets = parent_pos_sets


def process(lcp_interval: Interval, suf_tab: list[int], bwt_table: list[str]) -> None:
    # this variable saves the union of pos sets of all child intervals of this interval
    prev_child_alphabet_post_sets: PositionSets = {}
    lcp = lcp_interval.lcp_value

    # the smallest interval that has no children is the parent of the leaves under this interval/subtree
    if len(lcp_interval.child_list) == 0:
        process_leaves(lcp_interval, suf_tab, bwt_table)
    else:
        # process the pos sets propagated to these intervals by their children
        for child_interval in lcp_interval.child_list:
            curr_child_alphabet_pos_sets: PositionSets = child_interval.pos_sets

            if len(prev_child_alphabet_post_sets.keys()) == 0:
                prev_child_alphabet_post_sets = curr_child_alphabet_pos_sets
            else:
                for prev_key in prev_child_alphabet_post_sets:
                    for curr_key in curr_child_alphabet_pos_sets:
                        if prev_key != curr_key:
                            prev_key_itr = prev_child_alphabet_post_sets[prev_key]
                            curr_key_itr_head = curr_child_alphabet_pos_sets[curr_key]

                            while prev_key_itr is not None:
                                curr_key_itr = curr_key_itr_head
                                p = prev_key_itr.data

                                while curr_key_itr is not None:
                                    p_prime = curr_key_itr.data

                                    maximal_repeats.append(((p, p + lcp), (p_prime, p_prime + lcp)))

                                    curr_key_itr = curr_key_itr.next
                                prev_key_itr = prev_key_itr.next

                # union the lists
                for key in curr_child_alphabet_pos_sets:
                    curr_child_ptr_itr = curr_child_alphabet_pos_sets[key]

                    # if key is present in prev pos sets, then link the pos set for this key found in this child pos set
                    if key in prev_child_alphabet_post_sets:
                        prev_child_ptr = prev_child_alphabet_post_sets[key]

                        while prev_child_ptr.next is not None:
                            prev_child_ptr = prev_child_ptr.next

                        prev_child_ptr.next = curr_child_ptr_itr
                    else:
                        prev_child_alphabet_post_sets[key] = curr_child_ptr_itr

        # propagate the union of lists after children are processed and all maximal repeats are output
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
                top.update_child_list(last_interval, suf_tab, bwt_table)
                last_interval = None

        if lcp_table[i] > top.lcp_value:
            if last_interval is not None:
                # -1 here represents undefined or bottom value
                stack.push(Interval(lcp_table[i], lb, -1, [last_interval]))
                last_interval = None
            else:
                stack.push(Interval(lcp_table[i], lb, -1, []))

    return maximal_repeats
