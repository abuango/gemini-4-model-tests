import unittest

from shop.invoice import discounted_lines, invoice_total


class InvoiceTest(unittest.TestCase):
    def test_total_is_reduced_by_the_whole_discount(self):
        lines = [("pen", 333), ("pad", 333), ("ink", 334)]
        self.assertEqual(invoice_total(lines, 100), 900)

    def test_no_discount(self):
        self.assertEqual(discounted_lines([("pen", 500)], 0), [("pen", 500)])

    def test_even_split(self):
        self.assertEqual(discounted_lines([("a", 100), ("b", 100)], 50), [("a", 75), ("b", 75)])


if __name__ == "__main__":
    unittest.main()
