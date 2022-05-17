import random
import time
import unittest
from typing import Optional

from matplotlib import pyplot as plt

from core.match_pattern import find_pattern
from core.utils import basic_tables_utils
from core.utils.IOUtils import get_seqs_from_file
from core.utils.STree import STree
from core.utils.helper import gen_random_substrings


class TestMatchPattern(unittest.TestCase):
    random_seq = None
    s: Optional[str] = None
    patterns: Optional[list[str]] = None
    suf_tab: Optional[list[int]] = None
    stree: Optional[STree] = None
    lcp_tab: Optional[list[int]] = None
    time_taken_using_esa = {}
    time_taken_using_stree = {}

    @classmethod
    def setUpClass(cls) -> None:
        cls.stree = STree()
        seqs = get_seqs_from_file("../../resources/genomes/random_seqs_max_len_300.fasta")

        cls.random_seq = seqs[random.randrange(0, len(seqs) - 1)]
        cls.s = cls.random_seq.seq
        cls.stree.build_using_mccreight(cls.s)
        cls.suf_tab = basic_tables_utils.gen_suffix_array(cls.stree)
        cls.lcp_tab = basic_tables_utils.gen_lcp_array(cls.s, cls.suf_tab)
        cls.patterns = gen_random_substrings(cls.s, 20, 30, 10)

    @classmethod
    def tearDownClass(cls) -> None:
        x_esa = sorted(list(TestMatchPattern.time_taken_using_esa.keys()))
        y_esa = []

        for key in x_esa:
            y_esa.append(TestMatchPattern.time_taken_using_esa[key])

        x_stree = sorted(list(TestMatchPattern.time_taken_using_stree.keys()))
        y_stree = []

        for key in x_stree:
            y_stree.append(TestMatchPattern.time_taken_using_stree[key])

        plt.plot(x_esa, y_esa, label="ESA")
        plt.plot(x_stree, y_stree, label="Suffix Tree")

        plt.xlabel('pattern length')
        plt.ylabel('Time(s)')

        plt.title('ESA vs Suffix Tree runtime')

        plt.legend(loc="best")

        plot_file_name = "results/" + cls.random_seq.id + "_" + "plot.png"

        # save the plot in a file, to let tests finish
        plt.savefig(plot_file_name)

    # def test_time_to_search_pattern_using_esa(self):
    #     start_time = time.time()
    #     find_pattern(self.s, self.p, self.suf_tab, self.lcp_tab)
    #     TestMatchPattern.time_taken_using_esa[len(self.p)] = round((time.time() - start_time), 5)
    #
    # def test_time_to_search_pattern_using_stree(self):
    #     start_time = time.time()
    #     self.stree.search(self.p)
    #     TestMatchPattern.time_taken_using_stree[len(self.p)] = round((time.time() - start_time), 5)
    #
    # def test_time_to_search_patter_rand(self):
    #     start = time.time()
    #     find_pattern(self.s, "anana", self.suf_tab, self.lcp_tab)
    #     TestMatchPattern.time_taken_using_esa[5] = round((time.time() - start), 5)
    #
    #     start = time.time()
    #     self.stree.search("anana")
    #     TestMatchPattern.time_taken_using_stree[5] = round((time.time() - start), 5)

    def test_time_search_valid_sub_str_e_coli_esa(self):
        for pattern in self.patterns:
            start_time = time.time()
            find_pattern(self.s, pattern, self.suf_tab, self.lcp_tab)
            time_to_exe = round((time.time() - start_time), 5)

            TestMatchPattern.time_taken_using_esa[len(pattern)] = time_to_exe

    def test_time_search_valid_sub_str_e_coli_stree(self):
        for pattern in self.patterns:
            start_time = time.time()
            self.stree.search(pattern)
            time_to_exe = round((time.time() - start_time), 5)

            TestMatchPattern.time_taken_using_stree[len(pattern)] = time_to_exe


if __name__ == '__main__':
    unittest.main()
