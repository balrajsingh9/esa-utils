import time
import unittest
from typing import Optional

from core.match_pattern import find_pattern
from core.utils import basic_tables_utils
from core.utils.STree import STree


class TestMatchPattern(unittest.TestCase):
    s: Optional[str] = None
    p: Optional[str] = None
    suf_tab: Optional[list[int]] = None
    stree: Optional[STree] = None
    lcp_tab: Optional[list[int]] = None
    time_taken_using_esa = 0
    time_taken_using_stree = 0

    @classmethod
    def setUpClass(cls) -> None:
        cls.s = "banana"
        cls.p = "ana"
        cls.stree = STree()
        cls.stree.build_using_mccreight(cls.s)
        cls.suf_tab = basic_tables_utils.gen_suffix_array(cls.stree)
        cls.lcp_tab = basic_tables_utils.gen_lcp_array(cls.s, cls.suf_tab)

    @classmethod
    def tearDownClass(cls) -> None:
        print('\n\n--------- Benchmark Results Starts ---------\n')
        print(f"Time taken to search for pattern using esa: {TestMatchPattern.time_taken_using_esa:.6f}")
        print(f"Time taken to search for pattern using suffix tree: {TestMatchPattern.time_taken_using_stree:.6f}")
        print('\n--------- Benchmark Result Ends ---------')

    def test_time_to_search_pattern_using_esa(self):
        start_time = time.time()
        find_pattern(self.s, self.p, self.suf_tab, self.lcp_tab)
        TestMatchPattern.time_taken_using_esa = time.time() - start_time

    def test_time_to_search_pattern_using_stree(self):
        start_time = time.time()
        self.stree.search(self.p)
        TestMatchPattern.time_taken_using_stree = time.time() - start_time


if __name__ == '__main__':
    unittest.main()
