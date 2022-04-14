import time
import unittest

from core.match_pattern import find_pattern


class TestMatchPattern(unittest.TestCase):
    @classmethod
    def setUp(cls) -> None:
        cls.s: str = "acaaacatat"
        cls.suf_tab: list[int] = [2, 3, 0, 4, 6, 8, 1, 5, 7, 9, 10]
        cls.lcp_table: list[int] = [0, 2, 1, 3, 1, 2, 0, 2, 0, 1, 0]

    def test_time_to_execute_find_pattern_without_slice(self):
        start_time = time.time()
        find_pattern(self.s, "aca", self.suf_tab, self.lcp_table)

        print(f"execution time in s={(time.time() - start_time):.6f}")

    def test_time_to_execute_find_pattern_with_slice(self):
        start_time = time.time()
        find_pattern(self.s, "aca", self.suf_tab, self.lcp_table)

        print(f"execution time in s={(time.time() - start_time):.6f}")
