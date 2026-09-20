import unittest

from src.importer import unique_rows


class ImporterTest(unittest.TestCase):
    def test_keeps_first_row_for_each_id(self):
        rows = [{"id": 1, "value": "a"}, {"id": 1, "value": "b"}]
        result, _ = unique_rows(rows)
        self.assertEqual(result, [{"id": 1, "value": "a"}])


if __name__ == "__main__":
    unittest.main()
