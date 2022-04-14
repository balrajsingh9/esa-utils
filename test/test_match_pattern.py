import unittest

from core.match_pattern import find_pattern


class TestMatchPattern(unittest.TestCase):
    @classmethod
    def setUp(cls) -> None:
        cls.s: str = "acaaacatat"
        cls.suf_tab: list[int] = [2, 3, 0, 4, 6, 8, 1, 5, 7, 9, 10]
        cls.lcp_table: list[int] = [0, 2, 1, 3, 1, 2, 0, 2, 0, 1, 0]

    def test_empty_pattern_in_non_empty_string(self) -> None:
        self.assertIsNotNone(find_pattern(self.s, "", self.suf_tab, self.lcp_table))


if __name__ == '__main__':
    unittest.main()
