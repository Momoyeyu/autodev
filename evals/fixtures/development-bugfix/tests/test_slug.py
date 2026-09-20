import unittest

from src.slug import slugify


class SlugifyTest(unittest.TestCase):
    def test_normalizes_words(self):
        self.assertEqual(slugify("Hello, World!"), "hello-world")


if __name__ == "__main__":
    unittest.main()
