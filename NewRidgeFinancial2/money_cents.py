"""Currency helpers for SoftDent/Apex financial honesty (cent-safe Decimal).

Use Decimal quantized to 2 places (ROUND_HALF_EVEN / banker's rounding) for
variance and ledger aggregates. Never coerce null/missing to 0.0.
empty != $0.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN
from typing import Any

from ui_honesty_policy import is_empty_money

TWOPLACES = Decimal("0.01")
CENT = Decimal("0.01")


def to_money(value: Any) -> Decimal | None:
    """Parse money to Decimal cents scale, or None if empty/unparseable.

    Explicit numeric 0 / 0.0 is kept as Decimal('0.00').
    Null / blank / ambiguous string zeros from honesty policy stay None.
    """
    if is_empty_money(value):
        return None
    if isinstance(value, Decimal):
        try:
            return value.quantize(TWOPLACES, rounding=ROUND_HALF_EVEN)
        except InvalidOperation:
            return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return Decimal(value).quantize(TWOPLACES, rounding=ROUND_HALF_EVEN)
    if isinstance(value, float):
        # Route through str to avoid binary float litter when possible
        try:
            return Decimal(str(value)).quantize(TWOPLACES, rounding=ROUND_HALF_EVEN)
        except (InvalidOperation, ValueError):
            return None
    text = str(value).strip().replace("$", "").replace(",", "")
    if not text:
        return None
    try:
        return Decimal(text).quantize(TWOPLACES, rounding=ROUND_HALF_EVEN)
    except (InvalidOperation, ValueError):
        return None


def money_to_api(value: Decimal | None) -> float | None:
    """JSON-friendly float after Decimal quantization (display/API only)."""
    if value is None:
        return None
    return float(value)


def money_add(a: Decimal | None, b: Decimal | None) -> Decimal | None:
    if a is None or b is None:
        return None
    return (a + b).quantize(TWOPLACES, rounding=ROUND_HALF_EVEN)


def money_sub(a: Decimal | None, b: Decimal | None) -> Decimal | None:
    if a is None or b is None:
        return None
    return (a - b).quantize(TWOPLACES, rounding=ROUND_HALF_EVEN)


def money_abs(a: Decimal | None) -> Decimal | None:
    if a is None:
        return None
    return abs(a).quantize(TWOPLACES, rounding=ROUND_HALF_EVEN)
