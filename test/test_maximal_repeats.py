import unittest
from typing import Optional

from core.maximal_repeats import find_maximal_repeats
from core.utils import basic_tables_utils
from core.utils.STree import STree


class TestMaximalRepeats(unittest.TestCase):
    s: Optional[str] = None
    suf_tab: Optional[list[int]] = None
    stree: Optional[STree] = None
    lcp_tab: Optional[list[int]] = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.s = "banana"
        cls.stree = STree()
        cls.stree.build_using_mccreight(cls.s)
        cls.suf_tab = basic_tables_utils.gen_suffix_array(cls.stree)
        cls.lcp_tab = basic_tables_utils.gen_lcp_array(cls.s, cls.suf_tab)
        cls.bwt_tab = basic_tables_utils.gen_bwt_array(cls.s, cls.suf_tab)

    def test_repeats_is_present_using_esa(self):
        repeats = find_maximal_repeats(self.s, self.suf_tab, self.lcp_tab, self.bwt_tab)
        self.assertTrue(len(repeats) > 0)

    def test_repeats_absent_in_string_made_of_only_one_char_using_esa(self):
        repeats = find_maximal_repeats("aaaaaa", self.suf_tab, self.lcp_tab, self.bwt_tab)
        self.assertTrue(len(repeats) == 0)


if __name__ == '__main__':
    unittest.main()
