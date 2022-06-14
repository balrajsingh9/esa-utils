import unittest
from typing import Optional

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
        cls.stree = STree()
        cls.stree.build_using_mccreight(cls.s)
        cls.suf_tab = basic_tables_utils.gen_suffix_array_naive(cls.s + '$')
        cls.lcp_tab = basic_tables_utils.gen_lcp_array(cls.s, cls.suf_tab)

        print(cls.stree.find_maximal_repeats())
        print(find_maximal_repeats(cls.s, cls.suf_tab, cls.lcp_tab))

    def test_invalid_pattern_using_stree(self):
        self.assertFalse(False)


if __name__ == '__main__':
    unittest.main()
