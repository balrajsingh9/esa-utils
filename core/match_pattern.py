from dataclasses import dataclass


@dataclass
class Child:
    up: int = -1
    down: int = -1
    next_l_index: int = -1

    def __str__(self) -> str:
        return "up=%s, down=%s, nextLIndex=%s" % (self.up, self.down, self.next_l_index)


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


def match_pattern(s: str, p: str, child_tab: list[Child], lcp_tab: list[int], suf_tab: list[int]) -> bool:
    # considering empty pattern to be a valid string; returns false if the string s is non-empty
    if len(p) == 0:
        # len(s) == 1 is empty because we consider sentinel char $ at the end
        return len(s) == 1

    c: int = 0
    pattern_found: bool = True
    n, m = len(s), len(p)
    i, j = get_interval(0, n, p[c], s, child_tab, lcp_tab, suf_tab)

    while i != -1 and j != -1 and c < m and pattern_found is True:
        if i != j:
            lcp: int = get_lcp(i, j, child_tab, lcp_tab)
            min_val: int = min(lcp, m)
            pattern_found = s[suf_tab[i] + c: suf_tab[i] + min_val - 1] == p[c: min_val - 1]
            c = min_val

            if c == m:
                # check for the last character to match
                return s[suf_tab[i] + c - 1] == p[c - 1:]

            i, j = get_interval(i, j, p[c], s, child_tab, lcp_tab, suf_tab)

        else:
            # check for the last block that is left
            pattern_found = s[suf_tab[i] + c - 1: suf_tab[i] + m] == p[c - 1:]

            # can safely return from here I think
            return pattern_found

    pattern_found = i != -1 and j != -1

    return pattern_found


def find_pattern(s: str, p: str, suf_tab: list[int], lcp_tab: list[int]) -> bool:
    child_tab: list[Child] = compute_child_table(lcp_tab)

    return match_pattern(s, p, child_tab, lcp_tab, suf_tab)
