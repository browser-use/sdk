"""Unit tests for the optional x402 payment ceiling."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from browser_use_sdk._core import x402 as x402_helpers


class FakeRequirement:
    def __init__(self, amount: int) -> None:
        self.amount = amount

    def get_amount(self) -> int:
        return self.amount


class FakeClient:
    def __init__(self) -> None:
        self.policy: Any = None

    def register_policy(self, policy: Any) -> FakeClient:
        self.policy = policy
        return self


def test_x402_payment_cap_filters_requirements(monkeypatch: pytest.MonkeyPatch) -> None:
    def max_amount(limit: int) -> Any:
        return lambda _version, requirements: [
            item for item in requirements if item.get_amount() <= limit
        ]

    real_import = x402_helpers.importlib.import_module

    def fake_import(name: str) -> Any:
        if name == "x402":
            return SimpleNamespace(max_amount=max_amount)
        return real_import(name)

    monkeypatch.setattr(x402_helpers.importlib, "import_module", fake_import)
    client = FakeClient()

    returned = x402_helpers.apply_x402_max_payment_usd(client, "0.75")

    assert returned is client
    filtered = client.policy(2, [FakeRequirement(750_000), FakeRequirement(750_001)])
    assert [item.amount for item in filtered] == [750_000]


@pytest.mark.parametrize("cap", [0, -1, "nan", "inf", "bad"])
def test_x402_payment_cap_rejects_invalid_values(cap: float | str) -> None:
    with pytest.raises(ValueError, match="positive finite number"):
        x402_helpers._max_payment_atomic_units(cap)


def test_x402_payment_cap_requires_atomic_unit() -> None:
    with pytest.raises(ValueError, match="at least one USDC atomic unit"):
        x402_helpers._max_payment_atomic_units("0.0000001")
