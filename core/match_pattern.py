from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

MatchResult = Optional[tuple[int, int]]


@dataclass
class Child:
    up: int = -1
    down: int = -1
    next_l_index: int = -1

    def __str__(self) -> str:
        return f"up={self.up}, down={self.down}, nextLIndex={self.next_l_index}"


def compute_up_and_down_values(child_table: list[Child], lcp_table: list[int]):
    last_idx = -1
    stack: list[int] = [0]

    for i in range(1, len(lcp_table)):
        top = stack[len(stack) - 1]

        while lcp_table[i] < lcp_table[top]:
            last_idx = stack.pop()
            top = stack[len(stack) - 1]

            if (lcp_table[i] <= lcp_table[top]) and (lcp_table[top] != lcp_table[last_idx]):
                child_table[top].down = last_idx

        if last_idx != -1:
            child_table[i].up = last_idx
            last_idx = -1

        stack.append(i)


def compute_next_l_indices(child_table: list[Child], lcp_tab: list[int]):
    stack: list[int] = [0]

    for i in range(1, len(lcp_tab)):
        top = stack[len(stack) - 1]

        while lcp_tab[i] < lcp_tab[top]:
            stack.pop()
            top = stack[len(stack) - 1]

        if lcp_tab[i] == lcp_tab[top]:
            last_idx = stack.pop()
            child_table[last_idx].next_l_index = i

        stack.append(i)


def compute_child_table(lcp_tab: list[int]):
    child_table: list[Child] = []

    for i in range(0, len(lcp_tab)):
        child_table.append(Child())

    compute_up_and_down_values(child_table, lcp_tab)
    compute_next_l_indices(child_table, lcp_tab)

    return child_table


def is_interval_eligible(a: str, i: int, lcp: int, s: str, suf_tab: list[int]) -> bool:
    idx_to_hit = suf_tab[i]

    return s[idx_to_hit + lcp] == a


def get_lcp(i: int, j: int, child_tab: list[Child], lcp_tab: list[int]):
    assert 0 <= i and 0 <= j <= len(child_tab)

    # root interval
    if i == 0 and j == len(child_tab):
        return 0
    elif i < child_tab[j].up < j:
        return lcp_tab[child_tab[j].up]
    else:
        return lcp_tab[child_tab[i].down]


def get_interval(i: int, j: int, a: str, s: str, child_tab: list[Child],
                 lcp_tab: list[int], suf_tab: list[int]) -> tuple[int, int]:
    i_1: int = -1
    i_2: int = -1

    assert 0 <= i and 0 <= j <= len(child_tab)

    lcp = get_lcp(i, j, child_tab, lcp_tab)

    if i == 0 and j == len(child_tab):
        i_1 = child_tab[i].next_l_index
    elif len(child_tab) > j > child_tab[j].up > i:
        i_1 = child_tab[j].up
    else:
        i_1 = child_tab[i].down

    # has no children
    if i_1 == -1:
        return -1, -1

    # runs in infinite loop for some test cases, so still returning (lb, rb - 1) instead of (lb, rb)
    if is_interval_eligible(a, i, lcp, s, suf_tab):
        return i, i_1 - 1

    while child_tab[i_1].next_l_index != -1:
        i_2 = child_tab[i_1].next_l_index

        if is_interval_eligible(a, i_1, lcp, s, suf_tab):
            return i_1, i_2 - 1

        i_1 = i_2

    if is_interval_eligible(a, i_1, lcp, s, suf_tab):
        return i_1, j

    # represents undefined
    return -1, -1


def comp_prefix_len(s: str, p: str, x_offset: int, y_offset: int, max_len: int | None = None) -> int:
    max_len = max_len or min(len(p) - x_offset, len(s) - y_offset)

    for prefix, i in enumerate(range(max_len)):
        if p[x_offset + i] != s[y_offset + i]:
            return prefix

    return max_len


def match_pattern(s: str, p: str, child_tab: list[Child], lcp_tab: list[int], suf_tab: list[int]) -> MatchResult:
    # considering empty pattern to be a valid string; returns false if the string s is non-empty
    if len(p) == 0:
        return 0, len(s) if len(s) > 1 else None

    matched: int = 0
    i, j = get_interval(0, len(s), p[0], s, child_tab, lcp_tab, suf_tab)

    while matched < len(p):
        if i == j:
            return None

        if i + 1 == j:
            matched += comp_prefix_len(s, p, matched, suf_tab[i] + matched)
            if matched != len(p):
                return None
            else:
                return i, j

        lcp: int = get_lcp(i, j, child_tab, lcp_tab)
        to_match: int = min(len(p) - matched, lcp)
        match: int = comp_prefix_len(s, p, matched, suf_tab[i] + matched, to_match)

        if match < to_match:
            return None

        matched += match

        if matched < len(p):
            i, j = get_interval(i, j, p[matched], s, child_tab, lcp_tab, suf_tab)

    return i, j


def find_pattern(s: str, p: str, suf_tab: list[int], lcp_tab: list[int]) -> MatchResult:
    child_tab: list[Child] = compute_child_table(lcp_tab)

    return match_pattern(s, p, child_tab, lcp_tab, suf_tab)
