#!/usr/bin/env python3
"""Synthetic funnel tests — no sector TAM numbers."""
from __future__ import annotations

import unittest

from market_sizing import (
    MarketFunnel,
    bottom_up_som,
    exit_revenue_fits_som,
    market_price_allowed,
)


class MarketSizingTests(unittest.TestCase):
    def test_nested_ok(self) -> None:
        f = MarketFunnel(tam=1_000_000, sam=200_000, som=40_000, currency="USD")
        self.assertTrue(f.is_consistent)
        self.assertEqual(f.validate(), [])

    def test_sam_exceeds_tam(self) -> None:
        f = MarketFunnel(tam=100, sam=200, som=10, currency="USD")
        self.assertFalse(f.is_consistent)
        self.assertIn("SAM exceeds TAM", f.validate())

    def test_som_exceeds_sam(self) -> None:
        f = MarketFunnel(tam=1000, sam=100, som=200, currency="EUR")
        self.assertFalse(f.is_consistent)
        self.assertIn("SOM exceeds SAM", f.validate())

    def test_bottom_up(self) -> None:
        self.assertEqual(bottom_up_som(100, 1200), 120_000)

    def test_market_price_blocked_without_funnel(self) -> None:
        self.assertFalse(market_price_allowed(None))
        bad = MarketFunnel(tam=10, sam=20, som=5, currency="USD")
        self.assertFalse(market_price_allowed(bad))
        good = MarketFunnel(tam=100, sam=50, som=10, currency="USD")
        self.assertTrue(market_price_allowed(good))
        self.assertTrue(market_price_allowed(None, comps_without_funnel=True))

    def test_exit_revenue_vs_som(self) -> None:
        f = MarketFunnel(tam=1e9, sam=1e8, som=5e6, currency="USD")
        self.assertTrue(exit_revenue_fits_som(4e6, f))
        self.assertFalse(exit_revenue_fits_som(6e6, f))


if __name__ == "__main__":
    unittest.main()
