#!/usr/bin/env python3
"""TAM / SAM / SOM nesting checks and helpers. Stdlib only."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MarketFunnel:
    tam: float
    sam: float
    som: float
    currency: str
    horizon_years: float | None = None

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.tam < 0 or self.sam < 0 or self.som < 0:
            errors.append("layers must be non-negative")
        if self.sam > self.tam:
            errors.append("SAM exceeds TAM")
        if self.som > self.sam:
            errors.append("SOM exceeds SAM")
        if not self.currency:
            errors.append("currency required")
        return errors

    @property
    def is_consistent(self) -> bool:
        return not self.validate()


def bottom_up_som(accounts: float, annual_spend: float) -> float:
    if accounts < 0 or annual_spend < 0:
        raise ValueError("accounts and annual_spend must be non-negative")
    return accounts * annual_spend


def market_price_allowed(funnel: MarketFunnel | None, *, comps_without_funnel: bool = False) -> bool:
    """Headline market price needs a consistent funnel unless draft comps-only."""
    if comps_without_funnel:
        return True
    if funnel is None:
        return False
    return funnel.is_consistent


def exit_revenue_fits_som(exit_revenue: float, funnel: MarketFunnel) -> bool:
    if not funnel.is_consistent:
        return False
    return exit_revenue <= funnel.som
