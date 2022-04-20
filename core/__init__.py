from core import maximal_repeats

if __name__ == '__main__':
    s = "acaaacatat"
    suf_tab = [2, 3, 0, 4, 6, 8, 1, 5, 7, 9, 10]
    lcp_table = [0, 2, 1, 3, 1, 2, 0, 2, 0, 1, 0]
    bwt_table = ['c', 'a', '$', 'a', 'c', 't', 'a', 'a', 'a', 't']
    repeats_set = maximal_repeats.find_maximal_repeats(s, suf_tab, lcp_table, bwt_table)

    for repeat in repeats_set:
        ((i_1, j_1), (i_2, j_2)) = repeat
        if i_1 <= j_1 and i_2 <= j_2:
            print(f"({s[i_1:j_1 + 1]}, {s[i_2:j_2 + 1]})")
