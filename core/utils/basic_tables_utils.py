from core.utils.STree import STree


def gen_suffix_array(suffix_tree: STree) -> list[int]:
    """
    Computes a suffix array using dfs over a suffix tree
    :param suffix_tree: suffix tree to perform dfs over
    :return: a suffix array
    """
    suf_tab: list[int] = []

    def build_sa_using_dfs(node, sa: list[int]):
        if node.children:
            # Internal node
            for val in sorted(node.children):
                build_sa_using_dfs(node.children[val], sa)
        else:
            # Leaf
            sa.append(node.idx)

    build_sa_using_dfs(suffix_tree.root, suf_tab)

    # assuming '$' is greater than all other alphabet
    # this is to conform the assumption in the paper
    # move position of '$' to suf_tab[len(original_text)]
    return suf_tab[1:] + [suf_tab[0]]


def gen_lcp_array(s: str, suf_tab: list[int]) -> list[int]:
    """
    Computes lcp array using Kasai's Algorithm in linear time
    :param s: the text for which lcp array is being computed
    :param suf_tab: suffix array, using which lcp array will be computed
    :return: the lcp array
    """
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
    """
    computes bwt array using suf_tab
    :param s: text for which bwt array is being computed
    :param suf_tab: suffix array for the input text
    :return: a bwt array for text
    """
    s += '$'
    bwt_array: list[str] = []

    for suf in suf_tab:
        bwt_array.append(s[suf - 1])

    return bwt_array
