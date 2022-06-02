import unittest
from typing import Optional

from core.match_pattern import find_pattern
from core.maximal_repeats import find_maximal_repeats
from core.utils.STree import STree
from core.utils import basic_tables_utils


class TestMatchPattern(unittest.TestCase):
    bwt_tab = None
    s: Optional[str] = None
    p: Optional[str] = None
    non_existing_pattern: Optional[str] = None
    suf_tab: Optional[list[int]] = None
    stree: Optional[STree] = None
    lcp_tab: Optional[list[int]] = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.s = "xabcyabcwabcyz"
        cls.p = "a"
        cls.non_existing_pattern = "haha"
        cls.stree = STree()
        cls.stree.build_using_mccreight(cls.s)
        cls.suf_tab = basic_tables_utils.gen_suffix_array(cls.stree)
        cls.lcp_tab = basic_tables_utils.gen_lcp_array(cls.s, cls.suf_tab)
        cls.bwt_tab = basic_tables_utils.gen_bwt_array(cls.s, cls.suf_tab)

        print(find_maximal_repeats(cls.s, cls.suf_tab, cls.lcp_tab, cls.bwt_tab))

    def test_empty_pattern_in_non_empty_string_using_esa(self) -> None:
        self.assertIsNotNone(find_pattern(self.s, "", self.suf_tab, self.lcp_tab))

    def test_empty_pattern_in_non_empty_string_using_stree(self) -> None:
        self.assertTrue(self.stree.search(""))

    def test_valid_pattern_using_esa(self):
        self.assertIsNotNone(find_pattern(self.s, self.p, self.suf_tab, self.lcp_tab))

    def test_valid_pattern_using_stree(self):
        self.assertTrue(self.stree.search(self.p))

    def test_invalid_pattern_using_esa(self):
        self.assertIsNone(find_pattern(self.s, self.non_existing_pattern, self.suf_tab, self.lcp_tab))

    def test_invalid_pattern_using_stree(self):
        self.assertFalse(self.stree.search(self.non_existing_pattern))


if __name__ == '__main__':
    unittest.main()
