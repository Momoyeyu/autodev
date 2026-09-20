import unittest

from src.invoice import Invoice


class InvoiceTest(unittest.TestCase):
    def test_total_sums_amounts(self):
        self.assertEqual(Invoice([10, "2.50"]).total(), 12.5)


if __name__ == "__main__":
    unittest.main()
