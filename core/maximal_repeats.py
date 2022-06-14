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

    def update_child_list(self, interval: Interval, s, suf_tab) -> None:
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


def process_leaves(lcp_interval: Interval, suf_tab: list[int], s) -> None:
    lb, rb, lcp = lcp_interval.lb, lcp_interval.rb, lcp_interval.lcp_value
    parent_pos_sets: PositionSets = {}
    last_leaf_pos_set: PositionSets = {}

    for i in range(lb, rb):
        alphabet: str = s[suf_tab[i] - 1]
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

                        if lcp > 0:
                            maximal_repeats.append(((p, p + lcp), (p_prime, p_prime + lcp)))

                for curr_key in curr_child_pos_set:
                    if curr_key in parent_pos_sets:
                        parent_pos_sets[curr_key].next = curr_child_pos_set[curr_key]
                    else:
                        parent_pos_sets[curr_key] = curr_child_pos_set[curr_key]

    lcp_interval.pos_sets = parent_pos_sets


def process(lcp_interval: Interval, s, suf_tab: list[int]) -> None:
    # this variable saves the union of pos sets of all child intervals of this interval
    prev_child_alphabet_post_sets: PositionSets = {}
    lcp = lcp_interval.lcp_value

    # the smallest interval that has no children is the parent of the leaves under this interval/subtree
    if len(lcp_interval.child_list) == 0:
        process_leaves(lcp_interval, suf_tab, s)
    else:
        if lcp_interval.child_list[0].lb - lcp_interval.lb > 0:
            letter = s[suf_tab[lcp_interval.lb] - 1]
            prev_child_alphabet_post_sets[letter] = ListNode(suf_tab[lcp_interval.lb])
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

                                    if lcp > 0:
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


        if lcp_interval.rb - lcp_interval.child_list[-1].rb == 1:
            letter = s[suf_tab[lcp_interval.child_list[-1].rb] - 1]
            p_prime = suf_tab[lcp_interval.child_list[-1].rb]

            for prev_key in prev_child_alphabet_post_sets:
                if prev_key != letter:
                    prev_key_itr_head = prev_child_alphabet_post_sets[prev_key]
                    prev_key_itr = prev_key_itr_head

                    while prev_key_itr is not None:
                        p = prev_key_itr.data

                        if lcp > 0:
                            maximal_repeats.append(((p, p + lcp), (p_prime, p_prime + lcp)))

                        prev_key_itr = prev_key_itr.next

            new_node = ListNode(p_prime)

            if letter in prev_child_alphabet_post_sets:
                prev_key_itr_head = prev_child_alphabet_post_sets[letter]

                while prev_key_itr_head.next is not None:
                    prev_key_itr_head = prev_key_itr_head

                prev_key_itr_head.next = new_node
            else:
                prev_child_alphabet_post_sets[letter] = new_node

        # propagate the union of lists after children are processed and all maximal repeats are output
        lcp_interval.pos_sets = prev_child_alphabet_post_sets


def find_maximal_repeats(s: str, suf_tab: list[int], lcp_table: list[int]) -> Repeats:
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
            top.rb = i
            last_interval: Interval = stack.pop()

            # we know the child intervals now, process this subtree
            process(last_interval, s, suf_tab)

            lb: int = last_interval.lb

            if stack.is_empty():
                break

            top: Interval = stack.top()

            if lcp_table[i] <= top.lcp_value:
                top.update_child_list(last_interval, s, suf_tab)
                last_interval = None

        if lcp_table[i] > top.lcp_value:
            if last_interval is not None:
                # -1 here represents undefined or bottom value
                stack.push(Interval(lcp_table[i], lb, -1, [last_interval]))
                last_interval = None
            else:
                stack.push(Interval(lcp_table[i], lb, -1, []))

    return maximal_repeats
