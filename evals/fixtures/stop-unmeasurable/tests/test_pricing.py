import unittest

from src.pricing import final_price


class PricingTest(unittest.TestCase):
    def test_applies_member_discount(self):
        self.assertEqual(final_price(100, "member"), 90)


if __name__ == "__main__":
    unittest.main()
