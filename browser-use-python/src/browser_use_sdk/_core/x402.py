"""Helpers for the optional x402 (pay-per-request) integration.

x402 is an HTTP payment protocol: instead of an API key, requests are
authenticated by signing a small USDC payment. See
``cloud/guides/x402`` in the docs and
https://www.x402.org for details.

The ``x402`` extra (``pip install "browser-use-sdk[x402]"``) pulls in the
real ``x402`` and ``eth-account`` packages. Until the user actually opts in
to x402 mode (by passing ``x402=`` or ``x402_private_key=`` to a client),
nothing in this file is imported.
"""

from __future__ import annotations

import importlib
from decimal import Decimal, InvalidOperation, ROUND_FLOOR
from typing import Any

# Public alias for optional x402.x402Client type
# Real class is only available when the x402 extra installed (Python 3.10+)
X402Client = Any


X402_BASE_URL_DEFAULT = "https://x402.api.browser-use.com/api/v3"
X402_BASE_URL_DEFAULT_V2 = "https://x402.api.browser-use.com/api/v2"

# Balance check is served on the regular (non-x402) host
X402_BALANCE_BASE_URL_DEFAULT = "https://api.browser-use.com/api/v3"

_USDC_ATOMIC_UNITS_PER_DOLLAR = Decimal("1000000")


def _build_wallet_auth_message(address: str, issued_at: str, nonce: str) -> str:
    # MUST match the backend's build_wallet_auth_message exactly.
    return (
        "Browser Use x402 wallet authentication\n"
        "Action: read credit balance\n"
        f"Wallet: {address}\n"
        f"Issued At: {issued_at}\n"
        f"Nonce: {nonce}"
    )


async def get_wallet_balance(
    private_key: str,
    *,
    base_url: str = X402_BALANCE_BASE_URL_DEFAULT,
    timeout: float = 30.0,
    **extra: Any,
) -> dict[str, Any]:
    """Read a wallet-derived project's credit balance

    Authenticates with an off-chain wallet signature (EIP-191): signs a
    canonical message proving control of the address; the server resolves the
    wallet to its project and returns the balance.

    Returns the parsed JSON: ``wallet``, ``project_id``, ``total_credits_usd``,
    ``additional_credits_usd``.
    """
    import secrets
    from datetime import datetime, timezone

    try:
        import httpx
        from eth_account import Account
        from eth_account.messages import encode_defunct
    except ImportError as e:
        raise _missing_x402() from e

    account = Account.from_key(private_key)
    address = account.address
    issued_at = datetime.now(timezone.utc).isoformat()
    nonce = secrets.token_hex(16)
    message = _build_wallet_auth_message(address, issued_at, nonce)
    signature = account.sign_message(encode_defunct(text=message)).signature.hex()
    if not signature.startswith("0x"):
        signature = "0x" + signature

    async with httpx.AsyncClient(timeout=timeout) as http:
        resp = await http.post(
            f"{base_url.rstrip('/')}/x402/balance",
            json={
                "address": address,
                "issued_at": issued_at,
                "nonce": nonce,
                "signature": signature,
                **extra,
            },
        )
        resp.raise_for_status()
        return resp.json()


def _missing_x402() -> ImportError:
    return ImportError(
        "x402 mode requires the optional 'x402' extra. "
        'Install with: pip install "browser-use-sdk[x402]"  '
        "(needs Python 3.10+)."
    )


def _max_payment_atomic_units(max_payment_usd: float | str) -> int:
    try:
        amount = Decimal(str(max_payment_usd))
    except (InvalidOperation, ValueError) as e:
        raise ValueError("x402_max_payment_usd must be a positive finite number") from e
    if not amount.is_finite() or amount <= 0:
        raise ValueError("x402_max_payment_usd must be a positive finite number")
    atomic_units = int(
        (amount * _USDC_ATOMIC_UNITS_PER_DOLLAR).to_integral_value(
            rounding=ROUND_FLOOR
        )
    )
    if atomic_units < 1:
        raise ValueError(
            "x402_max_payment_usd must resolve to at least one USDC atomic unit"
        )
    return atomic_units


def apply_x402_max_payment_usd(
    client: X402Client, max_payment_usd: float | str
) -> X402Client:
    """Add a hard USD ceiling to an x402 client."""
    try:
        x402_pkg = importlib.import_module("x402")
    except ImportError as e:
        raise _missing_x402() from e
    register_policy = getattr(client, "register_policy", None)
    if not callable(register_policy):
        raise TypeError("The supplied x402 client does not support payment policies")
    register_policy(x402_pkg.max_amount(_max_payment_atomic_units(max_payment_usd)))
    return client


def x402_client_from_private_key(
    private_key: str, *, max_payment_usd: float | str = 1.0
) -> X402Client:
    """Build a ready-to-use ``x402Client`` from an EVM private key.

    Equivalent to::

        from x402 import x402Client
        from x402.mechanisms.evm import EthAccountSigner
        from x402.mechanisms.evm.exact.register import register_exact_evm_client
        from eth_account import Account

        client = x402Client()
        register_exact_evm_client(client, EthAccountSigner(Account.from_key(key)))
    """
    try:
        eth_account = importlib.import_module("eth_account")
        x402_pkg = importlib.import_module("x402")
        evm_pkg = importlib.import_module("x402.mechanisms.evm")
        register_pkg = importlib.import_module("x402.mechanisms.evm.exact.register")
    except ImportError as e:
        raise _missing_x402() from e

    account = eth_account.Account.from_key(private_key)
    client = x402_pkg.x402Client()
    register_pkg.register_exact_evm_client(client, evm_pkg.EthAccountSigner(account))
    return apply_x402_max_payment_usd(client, max_payment_usd)


def x402_async_httpx_client(
    x402_client: X402Client,
    *,
    base_url: str,
    timeout: float,
    api_key: str = "",
) -> Any:
    """Return an ``httpx.AsyncClient``-compatible client wired for x402.

    If ``api_key`` is non-empty, the ``X-Browser-Use-API-Key`` header is sent
    on every request (top-up mode — backend credits the API key's project
    instead of auto-creating one keyed to the wallet).
    """
    try:
        clients_pkg = importlib.import_module("x402.http.clients")
    except ImportError as e:
        raise _missing_x402() from e

    headers = {"X-Browser-Use-API-Key": api_key} if api_key else None
    return clients_pkg.x402HttpxClient(
        x402_client, base_url=base_url, timeout=timeout, headers=headers
    )
