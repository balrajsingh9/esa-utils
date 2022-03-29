from dataclasses import dataclass
from typing import Tuple


@dataclass
class Child:
    up: int = -1
    down: int = -1
    next_l_index: int = -1

    def __str__(self):
        return f"up={self.up}, down={self.down}, nextLIndex={self.next_l_index}"


def compute_up_and_down_values(child_table, lcp_table):
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


def compute_next_l_indices(child_table, lcp_tab):
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


def compute_child_table(suf_tab, lcp_tab):
    child_table: list[Child] = []

    for i in range(0, len(lcp_tab)):
        child_table.append(Child())

    compute_up_and_down_values(child_table, lcp_tab)
    compute_next_l_indices(child_table, lcp_tab)

    return child_table


def get_child_intervals(i, j, child_tab: list[Child]) -> list[Tuple[int, int]]:
    intervals = []
    i_1: int = -1
    i_2: int = -1

    if i == 0 and j == len(child_tab):
        i_1 = child_tab[i].next_l_index
    elif (j + 1 < len(child_tab)) and i < child_tab[j + 1].up <= j:
        i_1 = child_tab[j + 1].up
    else:
        i_1 = child_tab[i].down

    # has no children
    if i_1 == -1:
        return intervals

    intervals.append((i, i_1 - 1))

    while child_tab[i_1].next_l_index != -1:
        i_2 = child_tab[i_1].next_l_index

        intervals.append((i_1, i_2 - 1))

        i_1 = i_2

    intervals.append((i_1, j))

    return intervals


def get_lcp(i, j, child_table: list[Child], lcp_tab):
    if (i < child_table[j + 1].up) and (child_table[j + 1].up <= j):
        return lcp_tab[child_table[j + 1].up]
    else:
        return lcp_tab[child_table[i].down]


def perform_top_down_traversal(s, p, suf_tap, lcp_tab):
    child_table = compute_child_table(suf_tap, lcp_tab)
    intervals: list[Tuple[int, int]] = get_child_intervals(0, len(child_table), child_table)
    print(intervals)
