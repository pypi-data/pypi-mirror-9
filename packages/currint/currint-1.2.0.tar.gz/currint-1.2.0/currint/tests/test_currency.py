# encoding: utf8
from __future__ import unicode_literals
from decimal import Decimal
from unittest import TestCase
from ..currency import currencies


class CurrencyTests(TestCase):

    def test_major_to_minor(self):
        self.assertEqual(
            currencies["GBP"].major_to_minor(1),
            100,
        )
        self.assertEqual(
            currencies["GBP"].major_to_minor(Decimal("1.43")),
            143,
        )
        with self.assertRaises(ValueError):
            currencies["GBP"].major_to_minor(Decimal("1.435"))
        # Non-decimal currency
        self.assertEqual(
            currencies["MRO"].major_to_minor(Decimal(5)),
            25,
        )

    def test_minor_to_major(self):
        self.assertEqual(
            currencies["GBP"].minor_to_major(100),
            Decimal("1"),
        )
        self.assertEqual(
            currencies["GBP"].minor_to_major(143),
            Decimal("1.43"),
        )
        # Non-decimal currency
        self.assertEqual(
            currencies["MRO"].minor_to_major(25),
            Decimal("5"),
        )

    def test_format(self):
        self.assertEqual(
            currencies["GBP"].format(100),
            "£1.00",
        )
        self.assertEqual(
            currencies["USD"].format(43),
            "$0.43",
        )
        # Non-decimal currency
        self.assertEqual(
            currencies["MRO"].format(7),
            "1.2 MRO",
        )
