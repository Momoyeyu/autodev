import unittest

from src.search import search


class SearchTest(unittest.TestCase):
    def test_returns_limited_results(self):
        self.assertEqual(len(search(limit=5)), 5)


if __name__ == "__main__":
    unittest.main()
