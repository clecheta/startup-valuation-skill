#!/usr/bin/env python3
"""Pre/post-money identities and multi-round dilution path. Stdlib only."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RoundResult:
    pre_money: float
    post_money: float
    primary_check: float
    sold_fraction: float


def priced_round(*, pre_money: float | None = None, post_money: float | None = None, primary_check: float) -> RoundResult:
    if primary_check < 0:
        raise ValueError("primary_check must be non-negative")
    if pre_money is not None and post_money is not None:
        expected = pre_money + primary_check
        if abs(expected - post_money) > 1e-9:
            raise ValueError(
                f"post_money {post_money} != pre_money {pre_money} + check {primary_check}"
            )
        post = post_money
        pre = pre_money
    elif pre_money is not None:
        pre = pre_money
        post = pre_money + primary_check
    elif post_money is not None:
        post = post_money
        pre = post_money - primary_check
        if pre < 0:
            raise ValueError("primary_check exceeds post_money")
    else:
        raise ValueError("provide pre_money or post_money")

    if post == 0:
        sold = 0.0
    else:
        sold = primary_check / post
    return RoundResult(pre_money=pre, post_money=post, primary_check=primary_check, sold_fraction=sold)


def sold_fraction_gap(declared_sold: float, result: RoundResult, *, tol: float = 1e-6) -> float | None:
    """Return absolute gap if declared sold % disagrees with check/post; else None."""
    gap = abs(declared_sold - result.sold_fraction)
    if gap <= tol:
        return None
    return gap


def remaining_founder_fraction(dilutions: list[float]) -> float:
    """Product of (1 - d_i) over rounds. Each d_i in [0, 1]."""
    remaining = 1.0
    for d in dilutions:
        if d < 0 or d > 1:
            raise ValueError(f"dilution {d} out of [0, 1]")
        remaining *= 1.0 - d
    return remaining


RECONCILE_REASONS = frozenset({"option_pool", "secondary", "convertible"})


def reconcile_sold_gap(reason: str) -> bool:
    return reason in RECONCILE_REASONS
