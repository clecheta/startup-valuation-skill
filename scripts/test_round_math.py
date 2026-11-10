#!/usr/bin/env python3
"""Round identity tests — synthetic numbers only."""
from __future__ import annotations

import unittest

from round_math import (
    priced_round,
    reconcile_sold_gap,
    remaining_founder_fraction,
    sold_fraction_gap,
)


class RoundMathTests(unittest.TestCase):
    def test_from_pre(self) -> None:
        r = priced_round(pre_money=1_900_000, primary_check=100_000)
        self.assertEqual(r.post_money, 2_000_000)
        self.assertAlmostEqual(r.sold_fraction, 0.05)

    def test_from_post(self) -> None:
        r = priced_round(post_money=4_000_000, primary_check=300_000)
        self.assertEqual(r.pre_money, 3_700_000)
        self.assertAlmostEqual(r.sold_fraction, 0.075)

    def test_inconsistent_pair(self) -> None:
        with self.assertRaises(ValueError):
            priced_round(pre_money=100, post_money=250, primary_check=100)

    def test_sold_gap(self) -> None:
        # 500k / 7M ≈ 7.14% vs declared 10%
        r = priced_round(post_money=7_000_000, primary_check=500_000)
        gap = sold_fraction_gap(0.10, r)
        self.assertIsNotNone(gap)
        self.assertGreater(gap, 0.02)
        self.assertIsNone(sold_fraction_gap(r.sold_fraction, r))

    def test_multi_round_path(self) -> None:
        rem = remaining_founder_fraction([0.05, 0.075, 0.10])
        self.assertAlmostEqual(rem, 0.95 * 0.925 * 0.90, places=6)

    def test_reconcile_reasons(self) -> None:
        self.assertTrue(reconcile_sold_gap("option_pool"))
        self.assertTrue(reconcile_sold_gap("secondary"))
        self.assertTrue(reconcile_sold_gap("convertible"))
        self.assertFalse(reconcile_sold_gap("vibes"))


if __name__ == "__main__":
    unittest.main()
