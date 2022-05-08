from core import maximal_repeats
from core.utils.STree import STree
from utils import basic_tables_utils

if __name__ == '__main__':
    s = "mississipi"
    p = "missi"
    # lcp_table = [0, 2, 1, 3, 1, 2, 0, 2, 0, 1, 0]
    # bwt_table = ['c', 'a', '$', 'a', 'c', 't', 'a', 'a', 'a', 't']
    # repeats_set = maximal_repeats.find_maximal_repeats(s, suf_tab, lcp_table, bwt_table)
    #
    # for repeat in repeats_set:
    #     ((i_1, j_1), (i_2, j_2)) = repeat
    #     print(f"({s[i_1:j_1 + 1]}, {s[i_2:j_2 + 1]})")

    suffix_tree = STree()
    suffix_tree.build_using_mccreight(s)

    suf_tab = basic_tables_utils.gen_suffix_array(suffix_tree)
    lcp_tab = basic_tables_utils.gen_lcp_array(s, suf_tab)
    bwt_tab = basic_tables_utils.gen_bwt_array(s, suf_tab)
    # print(suf_tab)
    # print(lcp_tab)
    # print(bwt_tab)
    print("Pattern found" if suffix_tree.search(p) else "Pattern not found")
