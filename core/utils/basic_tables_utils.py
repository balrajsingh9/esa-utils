from core.utils.STree import STree


def gen_suffix_array(s: str) -> list[int]:
    suffix_tree = STree()
    suffix_tree.build_using_mccreight(s)
    suf_tab: list[int] = []

    def build_sa_using_dfs(node, sa: list[int]):
        leaf = 1

        for val in sorted(node.children):
            child = node.children[val]
            leaf = 0
            build_sa_using_dfs(child, sa)

        if leaf == 1:
            sa.append(node.start)

    build_sa_using_dfs(suffix_tree.root, suf_tab)

    return suf_tab


"""
Compute lcp array using Kasai's Algorithm in linear time
"""


def gen_lcp_array(s: str, suf_tab: list[int]) -> list[int]:
    s += '$'
    inv_sa: list[int] = [-1] * len(suf_tab)

    for i, suffix in enumerate(suf_tab):
        inv_sa[suffix] = i

    lcp_array: list[int] = [-1] * len(suf_tab)
    lcp_array[0] = 0
    lcp = 0

    for i in inv_sa:
        if i > 0:
            j, k = suf_tab[i], suf_tab[i - 1]

            while s[j + lcp] == s[k + lcp]:
                lcp += 1

            lcp_array[i] = lcp
            lcp = max(0, lcp - 1)
        else:
            lcp = 0

    return lcp_array


def gen_bwt_array(s: str, suf_tab: list[int]) -> list[str]:
    s += '$'
    bwt_array: list[str] = []

    for suf in suf_tab:
        bwt_array.append(s[suf - 1])

    return bwt_array
