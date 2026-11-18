"""Unit test dasar untuk helper validasi input."""

import unittest

from src.utils.validators import is_not_empty, parse_positive_float, parse_positive_int


class TestValidators(unittest.TestCase):
    """Pengujian fungsi validasi input."""

    def test_is_not_empty(self) -> None:
        self.assertTrue(is_not_empty("Budi"))
        self.assertFalse(is_not_empty(""))
        self.assertFalse(is_not_empty("   "))

    def test_parse_positive_int(self) -> None:
        self.assertEqual(parse_positive_int("10"), 10)
        self.assertIsNone(parse_positive_int("0"))
        self.assertIsNone(parse_positive_int("-5"))
        self.assertIsNone(parse_positive_int("abc"))

    def test_parse_positive_float(self) -> None:
        self.assertEqual(parse_positive_float("12.5"), 12.5)
        self.assertIsNone(parse_positive_float("0"))
        self.assertIsNone(parse_positive_float("-1.5"))
        self.assertIsNone(parse_positive_float("xyz"))


if __name__ == "__main__":
    unittest.main()
