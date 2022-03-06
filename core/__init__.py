import maximal_repeats

if __name__ == '__main__':
    s = "acaaacatat"
    suftab = [2, 3, 0, 4, 6, 8, 1, 5, 7, 9, 10]
    lcp_table = [0, 2, 1, 3, 1, 2, 0, 2, 0, 1, 0]
    maximal_repeats.perform_bottom_up_traversal(s, suftab, lcp_table)
