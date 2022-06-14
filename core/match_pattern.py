from __future__ import annotations

from typing import Optional

MatchResult = Optional[tuple[int, int]]


def compute_child_table(lcp_tab: list[int]):
    child_table: list[int] = [-1] * (len(lcp_tab) - 1)

    last_idx = -1
    stack: list[int] = [0]

    for i in range(1, len(lcp_tab)):
        top = stack[-1]

        while lcp_tab[i] < lcp_tab[top]:
            last_idx = stack.pop()
            top = stack[-1]

            if (lcp_tab[i] < lcp_tab[top]) and (lcp_tab[top] != lcp_tab[last_idx]):
                child_table[top] = last_idx

        if last_idx != -1:
            child_table[i - 1] = last_idx
            last_idx = -1

        if lcp_tab[top] == lcp_tab[i]:
            child_table[top] = i

        stack.append(i)

    return child_table


def is_interval_eligible(a: str, i: int, lcp: int, s: str, suf_tab: list[int]) -> bool:
    return s[suf_tab[i] + lcp] == a


def get_lcp(i: int, j: int, child_tab: list[int], lcp_tab: list[int]):
    if i == 0 and j == len(child_tab):
        return 0
    elif j > child_tab[j - 1] > i:
        return lcp_tab[child_tab[j - 1]]
    else:
        return lcp_tab[child_tab[i]]


def get_interval(i: int, j: int, a: str, s: str, child_tab: list[int],
                 lcp_tab: list[int], suf_tab: list[int]) -> tuple[int, int]:
    i_1: int = -1
    i_2: int = -1

    lcp = get_lcp(i, j, child_tab, lcp_tab)

    # if root interval, then right boundary of first child is the starting index of the second child
    if i == 0 and j == len(s):
        i_1 = child_tab[child_tab[i]]
    # if not root, then look in up(j)
    elif j > child_tab[j - 1] > i:
        i_1 = child_tab[j - 1]
    # else it is in down(i)
    else:
        i_1 = child_tab[i]

    # check if suffixes of [i..i_1] have the letter 'a' at position lcp
    if is_interval_eligible(a, i, lcp, s, suf_tab):
        return i, i_1

    # otherwise look its siblings
    while i_1 < child_tab[i_1] and lcp_tab[i_1] == lcp_tab[child_tab[i_1]]:
        i_2 = child_tab[i_1]

        if is_interval_eligible(a, i_1, lcp, s, suf_tab):
            return i_1, i_2

        i_1 = i_2

    if is_interval_eligible(a, i_1, lcp, s, suf_tab):
        return i_1, j

    # we did not find any child intervals of [i..j] that whose suffixes starts with 'a'
    return -1, -1


def comp_prefix_len(s: str, p: str, x_offset: int, y_offset: int, max_len: int | None = None) -> int:
    max_len = max_len or min(len(p) - x_offset, len(s) - y_offset)

    for prefix, i in enumerate(range(max_len)):
        if p[x_offset + i] != s[y_offset + i]:
            return prefix

    return max_len


def match_pattern(s: str, p: str, child_tab: list[int], lcp_tab: list[int], suf_tab: list[int]) -> MatchResult:
    # considering empty pattern to be a valid string, hence occurs in each suffix
    if len(p) == 0:
        return 0, len(s) - 1

    matched: int = 0
    i, j = get_interval(0, len(s) - 1, p[0], s, child_tab, lcp_tab, suf_tab)

    while matched < len(p):
        if i == j:
            return None

        # we are at a leaf node, so we match the entire remaining suffix of p with suffix[i] of s
        # starting at position matched
        if i + 1 == j:
            matched += comp_prefix_len(s, p, matched, suf_tab[i] + matched)
            if matched != len(p):
                return None
            else:
                return i, j

        # l-value of this interval must be in either boundaries
        parent_lcp = max(lcp_tab[i], lcp_tab[j], 0)
        parent_to_child_edge_length: int = get_lcp(i, j, child_tab, lcp_tab) - parent_lcp
        print(parent_lcp, get_lcp(i, j, child_tab, lcp_tab), "HEre")
        to_match: int = min(len(p) - matched, parent_to_child_edge_length)

        match: int = comp_prefix_len(s, p, matched, suf_tab[i] + matched, to_match)

        if match < to_match:
            return None

        matched += match

        if matched < len(p):
            i, j = get_interval(i, j, p[matched], s, child_tab, lcp_tab, suf_tab)

    return i, j


def find_pattern(s: str, p: str, suf_tab: list[int], lcp_tab: list[int]) -> MatchResult:
    s += '$'
    child_tab: list[int] = compute_child_table(lcp_tab)
    print(child_tab)

    return match_pattern(s, p, child_tab, lcp_tab, suf_tab)
