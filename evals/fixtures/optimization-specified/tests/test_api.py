import unittest

from src.api import fetch_user


class ApiTest(unittest.TestCase):
    def test_fetches_user(self):
        self.assertEqual(fetch_user(7), {"id": 7, "name": "Ada"})


if __name__ == "__main__":
    unittest.main()
