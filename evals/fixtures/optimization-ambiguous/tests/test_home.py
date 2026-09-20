import unittest

from src.home import render_home


class HomeTest(unittest.TestCase):
    def test_renders_name(self):
        self.assertIn("Hello Ada", render_home("Ada"))


if __name__ == "__main__":
    unittest.main()
